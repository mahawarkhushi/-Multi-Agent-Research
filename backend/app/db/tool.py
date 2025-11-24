import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class Tool(Base):
    __tablename__ = "tools"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))
    name = sa.Column(sa.String(256), nullable=False)
    type = sa.Column(sa.String(128), nullable=False)
    config = sa.Column(pg.JSONB)

    agent_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("agents.id"), nullable=True)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())
