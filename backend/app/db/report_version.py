import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class ReportVersion(Base):
    __tablename__ = "report_versions"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))
    report_id = sa.Column(pg.UUID(as_uuid=True), sa.ForeignKey("reports.id"), nullable=False)

    content = sa.Column(sa.Text)
    report_metadata = sa.Column(pg.JSONB)   # <- fixed indentation

    version_number = sa.Column(sa.Integer, nullable=False)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())