from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from pymysql.cursors import DictCursor
from backend.database.session import get_db_cursor, create_tables
from backend.database.service.scheduler_service import SchedulerService
from backend.api.model.scheduler import (
    JobTemplateCreateReq,
    JobTemplateUpdateReq,
    JobTemplateRsp,
    ScheduledJobCreateReq,
    ScheduledJobUpdateReq,
    ScheduledJobRsp,
)
from backend.scheduler.manager import scheduler_manager
from backend.database.dao.scheduler_dao import SchedulerDAO


router = APIRouter()


def ensure_scheduler_tables():
    create_tables()  # 基础表
    # 其余表在 create_tables 内部扩展或在此处保证


# 模板
@router.post("/templates", response_model=JobTemplateRsp)
def create_template(
    req: JobTemplateCreateReq, cursor: DictCursor = Depends(get_db_cursor)
):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    try:
        tpl = service.create_template(req.dict())
        return JobTemplateRsp.model_validate(tpl.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[JobTemplateRsp])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    cursor: DictCursor = Depends(get_db_cursor),
):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    tpls = service.list_templates(skip, limit)
    return [JobTemplateRsp.model_validate(t.model_dump()) for t in tpls]


@router.put("/templates/{template_id}", response_model=JobTemplateRsp)
def update_template(
    template_id: int,
    req: JobTemplateUpdateReq,
    cursor: DictCursor = Depends(get_db_cursor),
):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    tpl = service.update_template(template_id, req.dict(exclude_unset=True))
    if not tpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return JobTemplateRsp.model_validate(tpl.model_dump())


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    if not service.delete_template(template_id):
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "删除成功"}


# 任务
@router.post("/jobs", response_model=ScheduledJobRsp)
def create_job(req: ScheduledJobCreateReq, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    try:
        job = service.create_job(req.dict())
        # 注册到 APScheduler
        scheduler_manager.sync_job(job)
        return ScheduledJobRsp.model_validate(job.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=List[ScheduledJobRsp])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    cursor: DictCursor = Depends(get_db_cursor),
):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    jobs = service.list_jobs(skip, limit)
    return [ScheduledJobRsp.model_validate(j.model_dump()) for j in jobs]


@router.put("/jobs/{job_id}", response_model=ScheduledJobRsp)
def update_job(
    job_id: int, req: ScheduledJobUpdateReq, cursor: DictCursor = Depends(get_db_cursor)
):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    job = service.update_job(job_id, req.dict(exclude_unset=True))
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    scheduler_manager.sync_job(job)
    return ScheduledJobRsp.model_validate(job.model_dump())


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, cursor: DictCursor = Depends(get_db_cursor)):
    ensure_scheduler_tables()
    service = SchedulerService(cursor)
    if not service.delete_job(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    scheduler_manager.remove_job(job_id)
    return {"message": "删除成功"}


@router.post("/jobs/{job_id}/run")
def run_job_now(job_id: int):
    # 触发一次立即运行
    ok = scheduler_manager.trigger_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="任务不存在或未激活")
    return {"message": "已触发执行"}


@router.get("/jobs/{job_id}/runs")
def list_job_runs(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    cursor: DictCursor = Depends(get_db_cursor),
):
    dao = SchedulerDAO(cursor)
    runs = dao.list_job_runs(job_id, skip, limit)
    return [r.model_dump() for r in runs]
