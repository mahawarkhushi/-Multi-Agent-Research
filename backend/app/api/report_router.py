from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.report import ReportCreate, ReportRead
from app.db.report import Report
from app.dependencies import get_db
from uuid import UUID

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=ReportRead)
def create_report(data: ReportCreate, db: Session = Depends(get_db)):
    new_report = Report(**data.dict())
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/", response_model=list[ReportRead])
def list_reports(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return db.query(Report).offset(skip).limit(limit).all()

@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: UUID, db: Session = Depends(get_db)):
    report = db.query(Report).get(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@router.delete("/{report_id}")
def delete_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).get(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    db.delete(report)
    db.commit()
    return {"message": "Report deleted"}
