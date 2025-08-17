from typing import List, Optional, Dict, Any
from pymysql.cursors import DictCursor
from backend.database.model.scheduler import (
    JobTemplateModel,
    ScheduledJobModel,
    JobRunModel,
)


class SchedulerDAO:
    def __init__(self, cursor: DictCursor):
        self.cursor = cursor

    # Templates
    def create_template(self, data: Dict[str, Any]) -> JobTemplateModel:
        sql = (
            "INSERT INTO job_templates (name, description, template_type, default_config) "
            "VALUES (%(name)s, %(description)s, %(template_type)s, JSON_OBJECT())"
        )
        # default_config 作为 JSON
        self.cursor.execute(
            "INSERT INTO job_templates (name, description, template_type, default_config) VALUES (%s,%s,%s,CAST(%s AS JSON))",
            (
                data.get("name"),
                data.get("description"),
                data.get("template_type", "db_query"),
                json_dumps(data.get("default_config", {})),
            ),
        )
        template_id = self.cursor.lastrowid
        return self.get_template_by_id(template_id)

    def get_template_by_id(self, template_id: int) -> Optional[JobTemplateModel]:
        self.cursor.execute("SELECT * FROM job_templates WHERE id=%s", (template_id,))
        row = self.cursor.fetchone()
        return JobTemplateModel.model_validate(row) if row else None

    def get_template_by_name(self, name: str) -> Optional[JobTemplateModel]:
        self.cursor.execute("SELECT * FROM job_templates WHERE name=%s", (name,))
        row = self.cursor.fetchone()
        return JobTemplateModel.model_validate(row) if row else None

    def list_templates(self, skip: int = 0, limit: int = 100) -> List[JobTemplateModel]:
        self.cursor.execute(
            "SELECT * FROM job_templates ORDER BY id LIMIT %s OFFSET %s", (limit, skip)
        )
        rows = self.cursor.fetchall()
        return [JobTemplateModel.model_validate(r) for r in rows]

    def update_template(
        self, template_id: int, update: Dict[str, Any]
    ) -> Optional[JobTemplateModel]:
        set_clauses = []
        values: List[Any] = []
        for key in ("name", "description", "template_type"):
            if key in update:
                set_clauses.append(f"{key}=%s")
                values.append(update[key])
        if "default_config" in update:
            set_clauses.append("default_config=CAST(%s AS JSON)")
            values.append(json_dumps(update["default_config"]))
        if not set_clauses:
            return self.get_template_by_id(template_id)
        sql = f"UPDATE job_templates SET {', '.join(set_clauses)} WHERE id=%s"
        values.append(template_id)
        self.cursor.execute(sql, values)
        return self.get_template_by_id(template_id)

    def delete_template(self, template_id: int) -> bool:
        self.cursor.execute("DELETE FROM job_templates WHERE id=%s", (template_id,))
        return self.cursor.rowcount > 0

    # Jobs
    def create_job(self, data: Dict[str, Any]) -> ScheduledJobModel:
        self.cursor.execute(
            """
            INSERT INTO scheduled_jobs
            (name, template_id, schedule_type, cron_expression, interval_seconds, is_active, next_run_time, override_config)
            VALUES (%s,%s,%s,%s,%s,%s,NULL,CAST(%s AS JSON))
            """,
            (
                data.get("name"),
                data.get("template_id"),
                data.get("schedule_type", "cron"),
                data.get("cron_expression"),
                data.get("interval_seconds"),
                data.get("is_active", True),
                json_dumps(data.get("override_config")),
            ),
        )
        job_id = self.cursor.lastrowid
        return self.get_job_by_id(job_id)

    def get_job_by_id(self, job_id: int) -> Optional[ScheduledJobModel]:
        self.cursor.execute("SELECT * FROM scheduled_jobs WHERE id=%s", (job_id,))
        row = self.cursor.fetchone()
        return ScheduledJobModel.model_validate(row) if row else None

    def list_jobs(self, skip: int = 0, limit: int = 100) -> List[ScheduledJobModel]:
        self.cursor.execute(
            "SELECT * FROM scheduled_jobs ORDER BY id LIMIT %s OFFSET %s", (limit, skip)
        )
        rows = self.cursor.fetchall()
        return [ScheduledJobModel.model_validate(r) for r in rows]

    def list_active_jobs(self) -> List[ScheduledJobModel]:
        self.cursor.execute(
            "SELECT * FROM scheduled_jobs WHERE is_active=TRUE ORDER BY id"
        )
        rows = self.cursor.fetchall()
        return [ScheduledJobModel.model_validate(r) for r in rows]

    def update_job(
        self, job_id: int, update: Dict[str, Any]
    ) -> Optional[ScheduledJobModel]:
        set_clauses = []
        values: List[Any] = []
        for key in (
            "name",
            "schedule_type",
            "cron_expression",
            "interval_seconds",
            "is_active",
        ):
            if key in update:
                set_clauses.append(f"{key}=%s")
                values.append(update[key])
        if "override_config" in update:
            set_clauses.append("override_config=CAST(%s AS JSON)")
            values.append(json_dumps(update["override_config"]))
        if not set_clauses:
            return self.get_job_by_id(job_id)
        sql = f"UPDATE scheduled_jobs SET {', '.join(set_clauses)} WHERE id=%s"
        values.append(job_id)
        self.cursor.execute(sql, values)
        return self.get_job_by_id(job_id)

    def delete_job(self, job_id: int) -> bool:
        self.cursor.execute("DELETE FROM scheduled_jobs WHERE id=%s", (job_id,))
        return self.cursor.rowcount > 0

    # Job runs
    def create_job_run(self, data: Dict[str, Any]) -> JobRunModel:
        self.cursor.execute(
            """
            INSERT INTO job_runs (job_id, status, started_at)
            VALUES (%s,%s,NOW())
            """,
            (
                data.get("job_id"),
                data.get("status", "running"),
            ),
        )
        run_id = self.cursor.lastrowid
        return self.get_job_run_by_id(run_id)

    def finish_job_run(
        self, run_id: int, data: Dict[str, Any]
    ) -> Optional[JobRunModel]:
        set_clauses = ["finished_at=NOW()"]
        values: List[Any] = []
        for key in ("status", "duration_ms", "rows_affected", "result", "error"):
            if key in data:
                if key in ("result", "error"):
                    set_clauses.append(f"{key}=%s")
                    values.append(data[key])
                else:
                    set_clauses.append(f"{key}=%s")
                    values.append(data[key])
        sql = f"UPDATE job_runs SET {', '.join(set_clauses)} WHERE id=%s"
        values.append(run_id)
        self.cursor.execute(sql, values)
        return self.get_job_run_by_id(run_id)

    def get_job_run_by_id(self, run_id: int) -> Optional[JobRunModel]:
        self.cursor.execute("SELECT * FROM job_runs WHERE id=%s", (run_id,))
        row = self.cursor.fetchone()
        return JobRunModel.model_validate(row) if row else None

    def list_job_runs(
        self, job_id: int, skip: int = 0, limit: int = 100
    ) -> List[JobRunModel]:
        self.cursor.execute(
            "SELECT * FROM job_runs WHERE job_id=%s ORDER BY id DESC LIMIT %s OFFSET %s",
            (job_id, limit, skip),
        )
        rows = self.cursor.fetchall()
        return [JobRunModel.model_validate(r) for r in rows]


def json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)
