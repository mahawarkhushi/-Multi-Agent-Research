from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.db.job import Job
from app.schemas.job import JobRead
from app.dependencies import get_db
from app.services.job_runner import run_job_in_background

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobRead)
async def create_job(
    agent_id: UUID = Form(...),
    created_by: UUID = Form(...),
    input_file: UploadFile | None = File(None),
    input_data: str | None = Form(None),
    db: Session = Depends(get_db)
):
    if input_file:
        content = await input_file.read()
        input_json = {"text": content.decode("utf-8")}
    elif input_data:
        try:
            input_json = json.loads(input_data)
        except Exception as e:
            raise HTTPException(400, f"Invalid JSON: {e}")
    else:
        input_json = None

    new_job = Job(agent_id=agent_id, created_by=created_by, input_data=input_json)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    run_job_in_background(str(new_job.id))
    return new_job

@router.get("/", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return db.query(Job).offset(skip).limit(limit).all()

@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@router.delete("/{job_id}")
def cancel_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status in ["completed", "failed"]:
        raise HTTPException(400, "Cannot cancel a completed or failed job")

    job.status = "cancelled"
    db.commit()
    return {"message": "Job cancelled"}
