
from datetime import datetime
from sqlmodel import SQLModel,Field, Column, DateTime, func


class Job(SQLModel, table=True):
    id: str = Field(primary_key=True)
    opt_id: str | None
    dep_code: str | None
    mode: str | None
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now(), nullable=False))
    status: str
    
    