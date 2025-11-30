import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class Agent(Base):
    __tablename__ = "agents"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))
    name = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text)
    created_by = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())