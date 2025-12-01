import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.sql import func
from .base import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    agent_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("agents.id"), nullable=False)
    created_by = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)

    input_data = sa.Column(sa.JSON)
    output_data = sa.Column(sa.JSON)

    status = sa.Column(sa.String(32), server_default="pending")
    progress = sa.Column(sa.Integer, server_default="0")

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())
