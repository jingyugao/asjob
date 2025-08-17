from typing import List, Optional, Dict, Any
from pymysql.cursors import DictCursor
from backend.database.dao.scheduler_dao import SchedulerDAO
from backend.database.model.scheduler import (
    JobTemplateModel,
    ScheduledJobModel,
    JobRunModel,
)


class SchedulerService:
    def __init__(self, cursor: DictCursor):
        self.dao = SchedulerDAO(cursor)

    # Templates
    def create_template(self, data: Dict[str, Any]) -> JobTemplateModel:
        if self.dao.get_template_by_name(data["name"]):
            raise ValueError("模板名称已存在")
        return self.dao.create_template(data)

    def get_template(self, template_id: int) -> Optional[JobTemplateModel]:
        return self.dao.get_template_by_id(template_id)

    def list_templates(self, skip: int = 0, limit: int = 100) -> List[JobTemplateModel]:
        return self.dao.list_templates(skip, limit)

    def update_template(
        self, template_id: int, update: Dict[str, Any]
    ) -> Optional[JobTemplateModel]:
        return self.dao.update_template(template_id, update)

    def delete_template(self, template_id: int) -> bool:
        return self.dao.delete_template(template_id)

    # Jobs
    def create_job(self, data: Dict[str, Any]) -> ScheduledJobModel:
        if not self.dao.get_template_by_id(data["template_id"]):
            raise ValueError("模板不存在")
        return self.dao.create_job(data)

    def get_job(self, job_id: int) -> Optional[ScheduledJobModel]:
        return self.dao.get_job_by_id(job_id)

    def list_jobs(self, skip: int = 0, limit: int = 100) -> List[ScheduledJobModel]:
        return self.dao.list_jobs(skip, limit)

    def list_active_jobs(self) -> List[ScheduledJobModel]:
        return self.dao.list_active_jobs()

    def update_job(
        self, job_id: int, update: Dict[str, Any]
    ) -> Optional[ScheduledJobModel]:
        return self.dao.update_job(job_id, update)

    def delete_job(self, job_id: int) -> bool:
        return self.dao.delete_job(job_id)

    # Runs
    def start_run(self, job_id: int) -> JobRunModel:
        return self.dao.create_job_run({"job_id": job_id, "status": "running"})

    def finish_run(
        self,
        run_id: int,
        status: str,
        duration_ms: Optional[int] = None,
        rows_affected: Optional[int] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[JobRunModel]:
        data: Dict[str, Any] = {"status": status}
        if duration_ms is not None:
            data["duration_ms"] = duration_ms
        if rows_affected is not None:
            data["rows_affected"] = rows_affected
        if result is not None:
            data["result"] = result
        if error is not None:
            data["error"] = error
        return self.dao.finish_job_run(run_id, data)
