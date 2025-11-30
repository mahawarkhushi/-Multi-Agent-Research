from pydantic import BaseModel
from uuid import UUID
from typing import Any, Optional

class ToolCreate(BaseModel):
    name: str
    type: str
    config: Optional[Any] = None
    agent_id: UUID | None = None

class ToolRead(BaseModel):
    id: UUID
    name: str
    type: str
    config: Optional[Any] = None
    agent_id: UUID | None

    class Config:
        orm_mode = True
