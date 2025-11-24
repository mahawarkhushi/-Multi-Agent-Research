import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class Report(Base):
    __tablename__ = "reports"
    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))
    title = sa.Column(sa.String(512), nullable=False)
    summary = sa.Column(sa.Text)
    created_by = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("users.id"))
    current_version_id = sa.Column(pg.UUID(as_uuid=True), nullable=True)
    report_metadata= sa.Column(pg.JSONB)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())
