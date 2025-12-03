from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.job import Job
from app.schemas.job import JobCreate, JobRead
from app.dependencies import get_db
from app.services.job_runner import run_job_in_background
from app.kafka.producer import publish_event  # updated producer

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobRead)
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    """
    Create a job, save to DB and publish Kafka event
    """
    new_job = Job(**data.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Publish Created Event
    publish_event(
        job_id=str(new_job.id),
        status="created",
        metadata={"payload": data.dict()}
    )

    # Start async background processing
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
    """
    Cancel job and publish Kafka event
    """
    job = db.query(Job).get(job_id)

    if not job:
        raise HTTPException(404, "Job not found")

    if job.status in ["completed", "failed"]:
        raise HTTPException(400, "Cannot cancel a completed or failed job")

    job.status = "cancelled"
    db.commit()

    # Publish Cancel Event
    publish_event(
        job_id=str(job.id),
        status="cancelled"
    )

    return {"message": "Job cancelled"}
