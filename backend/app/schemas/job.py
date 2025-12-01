from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID

class JobCreate(BaseModel):
    agent_id: UUID
    created_by: UUID
    input_data: Optional[Any] = None

class JobRead(BaseModel):
    id: UUID
    agent_id: UUID
    created_by: UUID
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    status: str
    progress: int

    class Config:
        from_attributes = True  # Pydantic v2
