from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
import time
import json

from backend.database.session import db_connection
from backend.database.service.scheduler_service import SchedulerService
from backend.database.service.connector_service import ConnectorService
from backend.infra.connectors import get_connector_instance


logger = logging.getLogger("scheduler_manager")


class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.started = False

    def start(self):
        if not self.started:
            self.scheduler.start()
            self.started = True
            logger.info("APScheduler started")
            # 启动时同步一次激活任务
            self.sync_active_jobs()

    def shutdown(self):
        if self.started:
            self.scheduler.shutdown(wait=False)
            self.started = False
            logger.info("APScheduler shutdown")

    def sync_active_jobs(self):
        with db_connection.get_cursor() as cursor:
            service = SchedulerService(cursor)
            jobs = service.list_active_jobs()
            for job in jobs:
                self.sync_job(job)

    def build_trigger(self, job) -> Optional[Any]:
        if job.schedule_type == "cron" and job.cron_expression:
            return CronTrigger.from_crontab(job.cron_expression)
        if job.schedule_type == "interval" and job.interval_seconds:
            return IntervalTrigger(seconds=job.interval_seconds)
        return None

    def _job_func(self, job_id: int):
        with db_connection.get_cursor() as cursor:
            sched_service = SchedulerService(cursor)
            run = sched_service.start_run(job_id)
            start_time = time.time()
            rows_affected = 0
            error: Optional[str] = None
            result_str: Optional[str] = None
            try:
                job = sched_service.get_job(job_id)
                if not job:
                    raise RuntimeError("job missing")
                # 合并配置
                tpl = sched_service.dao.get_template_by_id(job.template_id)
                cfg: Dict[str, Any] = {}
                if tpl and tpl.default_config:
                    cfg.update(tpl.default_config)
                if job.override_config:
                    cfg.update(job.override_config)

                connector_id = cfg.get("connector_id")
                sql = cfg.get("sql")
                params = cfg.get("params")
                if not connector_id or not sql:
                    raise ValueError("配置不完整: 需要 connector_id 和 sql")

                conn_service = ConnectorService(cursor)
                connector = conn_service.get_connector(connector_id)
                if not connector:
                    raise ValueError("连接器不存在")

                connector_instance = get_connector_instance(
                    db_type=connector.db_type,
                    host=connector.host,
                    port=connector.port,
                    username=connector.username,
                    password=connector.password,
                    database=connector.database_name,
                )
                data = connector_instance.execute_query(sql, params)
                rows_affected = len(data) if isinstance(data, list) else 0
                result_str = json.dumps(
                    {"preview": data[:10], "total": rows_affected}, ensure_ascii=False
                )
                status = "success"
                error = None
            except Exception as e:
                status = "failed"
                error = str(e)
            finally:
                duration_ms = int((time.time() - start_time) * 1000)
                sched_service.finish_run(
                    run.id,
                    status=status,
                    duration_ms=duration_ms,
                    rows_affected=rows_affected,
                    result=result_str,
                    error=error,
                )

    def sync_job(self, job_model):
        job_id = job_model.id
        # 先移除旧的
        try:
            self.scheduler.remove_job(job_id=str(job_id))
        except Exception:
            pass
        if not job_model.is_active:
            return
        trigger = self.build_trigger(job_model)
        if not trigger:
            logger.warning(f"job {job_id} has invalid schedule")
            return
        self.scheduler.add_job(
            func=self._job_func,
            trigger=trigger,
            args=[job_id],
            id=str(job_id),
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        logger.info(f"synced job {job_id}")

    def remove_job(self, job_id: int):
        try:
            self.scheduler.remove_job(job_id=str(job_id))
            logger.info(f"removed job {job_id}")
        except Exception:
            pass

    def trigger_job(self, job_id: int) -> bool:
        try:
            self.scheduler.add_job(
                func=self._job_func,
                args=[job_id],
                id=f"run_once_{job_id}_{time.time()}",
            )
            return True
        except Exception:
            return False


scheduler_manager = SchedulerManager()
