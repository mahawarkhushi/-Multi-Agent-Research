from pydantic import BaseModel
from uuid import UUID

class ReportCreate(BaseModel):
    title: str
    summary: str
    created_by: UUID


class ReportRead(BaseModel):
    id: UUID
    title: str
    summary: str
    created_by: UUID

    model_config = {
        "from_attributes": True
    }
