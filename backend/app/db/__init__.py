from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

DATABASE_URL = settings.DATABASE_URL


# Database engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import your models
from .base import Base
from .user import User
from .report import Report
from .report_version import ReportVersion
from .agent import Agent
from .tool import Tool
from .job import Job
from .audit_log import AuditLog

__all__ = [
    "Base",
    "User",
    "Report",
    "ReportVersion",
    "Agent",
    "Tool",
    "Job",
    "AuditLog",
    "SessionLocal",
    "engine"
]
