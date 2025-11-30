import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from .base import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()"))
    full_name = sa.Column(sa.String(256), nullable=False)
    email = sa.Column(sa.String(256), unique=True, nullable=False, index=True)
    role = sa.Column(sa.String(32), nullable=False, server_default="analyst")
    hashed_password = sa.Column(sa.String(512), nullable=False)
    is_active = sa.Column(sa.Boolean, server_default=sa.text("true"))
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())
