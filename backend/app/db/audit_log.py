import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))

    user_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True)

    entity = sa.Column(sa.String(64), nullable=False)        # user, report, job, tool, agent
    entity_id = sa.Column(pg.UUID(as_uuid=True), nullable=False)

    action = sa.Column(sa.String(64), nullable=False)        # create, update, delete
    old_values = sa.Column(pg.JSONB)
    new_values = sa.Column(pg.JSONB)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())