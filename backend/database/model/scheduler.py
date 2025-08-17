from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JobTemplateModel(BaseModel):
    id: Optional[int] = Field(None, description="主键ID")
    name: str = Field("", description="模板名称")
    description: Optional[str] = Field(None, description="描述")
    template_type: str = Field("db_query", description="模板类型")
    default_config: Dict[str, Any] = Field(
        default_factory=dict, description="默认配置JSON"
    )
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class ScheduledJobModel(BaseModel):
    id: Optional[int] = Field(None, description="主键ID")
    name: str = Field("", description="任务名称")
    template_id: int = Field(..., description="模板ID")
    schedule_type: str = Field("cron", description="cron|interval")
    cron_expression: Optional[str] = Field(None, description="cron 表达式")
    interval_seconds: Optional[int] = Field(None, description="间隔秒")
    is_active: bool = Field(True, description="是否激活")
    next_run_time: Optional[datetime] = Field(None, description="下次运行时间")
    override_config: Optional[Dict[str, Any]] = Field(None, description="覆盖配置")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class JobRunModel(BaseModel):
    id: Optional[int] = Field(None, description="主键ID")
    job_id: int = Field(..., description="任务ID")
    status: str = Field("pending", description="pending|running|success|failed")
    started_at: Optional[datetime] = Field(None)
    finished_at: Optional[datetime] = Field(None)
    duration_ms: Optional[int] = Field(None)
    rows_affected: Optional[int] = Field(None)
    result: Optional[Any] = Field(None)
    error: Optional[str] = Field(None)

    class Config:
        from_attributes = True
