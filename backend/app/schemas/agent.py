from pydantic import BaseModel
from uuid import UUID

class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    created_by: UUID

class AgentRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_by: UUID

    class Config:
        orm_mode = True
