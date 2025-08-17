from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class JobTemplateCreateReq(BaseModel):
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="描述")
    template_type: str = Field("db_query", description="模板类型，仅支持 db_query")
    default_config: Dict[str, Any] = Field(
        ..., description="默认配置，例如: {connector_id:int, sql:str, params:dict?}"
    )


class JobTemplateUpdateReq(BaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    default_config: Optional[Dict[str, Any]] = Field(None)


class JobTemplateRsp(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template_type: str
    default_config: Dict[str, Any]
    created_at: Optional[str]
    updated_at: Optional[str]


class ScheduledJobCreateReq(BaseModel):
    name: str = Field(..., description="任务名称")
    template_id: int = Field(..., description="任务模板ID")
    schedule_type: str = Field("cron", description="cron 或 interval")
    cron_expression: Optional[str] = Field(
        None, description="当 schedule_type=cron 时必填，标准 crontab 表达式"
    )
    interval_seconds: Optional[int] = Field(
        None, description="当 schedule_type=interval 时必填"
    )
    is_active: bool = Field(True, description="是否激活")
    override_config: Optional[Dict[str, Any]] = Field(
        None, description="覆盖模板默认配置"
    )


class ScheduledJobUpdateReq(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    is_active: Optional[bool] = None
    override_config: Optional[Dict[str, Any]] = None


class ScheduledJobRsp(BaseModel):
    id: int
    name: str
    template_id: int
    schedule_type: str
    cron_expression: Optional[str]
    interval_seconds: Optional[int]
    is_active: bool
    next_run_time: Optional[str]
    override_config: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


class JobRunRsp(BaseModel):
    id: int
    job_id: int
    status: str
    started_at: Optional[str]
    finished_at: Optional[str]
    duration_ms: Optional[int]
    rows_affected: Optional[int]
    result: Optional[Any]
    error: Optional[str]
