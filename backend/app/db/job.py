import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class Job(Base):
    __tablename__ = "jobs"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))

    agent_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("agents.id"), nullable=False)
    created_by = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)

    input_data = sa.Column(pg.JSONB)
    output_data = sa.Column(pg.JSONB)

    status = sa.Column(sa.String(32), server_default="pending")  # pending, running, completed, failed

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())

