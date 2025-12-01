import threading
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker

from app.db.job import Job
from app.db.base import engine
from app.services.agent_orchestrator import AgentOrchestrator

SessionLocal = sessionmaker(bind=engine)


def run_job_in_background(job_id: str):
    """
    Start the job in a separate daemon thread.
    """
    thread = threading.Thread(target=_process_job, args=(job_id,), daemon=True)
    thread.start()


def _update_job(job: Job, db: Session, *, status=None, progress=None, output_data=None):
    """
    Helper to safely update job status, progress, and output_data.
    (Kafka removed)
    """
    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if output_data is not None:
        job.output_data = output_data

    db.commit()
    print(f"[DB] Updated job {job.id} → status={job.status}, progress={job.progress}")


def _process_job(job_id: str):
    """
    Core job processing function (Kafka removed).
    """
    print(f"[THREAD START] Processing job {job_id}")

    steps = ["ingestion", "research", "citation", "formatting", "compliance"]
    total_steps = len(steps)

    db = SessionLocal()
    job = db.get(Job, job_id)

    if not job:
        print(f"[ERROR] Job {job_id} not found")
        db.close()
        return

    if job.status != "pending":
        print(f"[SKIP] Job {job_id} is already {job.status}")
        db.close()
        return

    # Mark job as running
    _update_job(job, db, status="running", progress=0)
    print(f"[RUNNING] Job {job_id} started")
    db.close()

    try:
        orchestrator = AgentOrchestrator()
        current_text = job.input_data.get("text", "")

        for idx, stage in enumerate(steps):
            # Check cancellation at every step
            db = SessionLocal()
            job = db.get(Job, job_id)
            if job.status == "cancelled":
                print(f"[CANCELLED] Job {job_id} stopped at stage '{stage}'")
                _update_job(job, db, status="cancelled")
                db.close()
                return
            db.close()

            print(f"[STAGE] {stage.upper()} running...")
            current_text = orchestrator.run_single(stage, current_text)

            # Update progress
            db = SessionLocal()
            job = db.get(Job, job_id)
            progress_percent = int(((idx + 1) / total_steps) * 100)
            _update_job(job, db, progress=progress_percent)
            print(f"[PROGRESS] Job {job_id}: {progress_percent}% after '{stage}'")
            db.close()

        # Final completion
        db = SessionLocal()
        job = db.get(Job, job_id)
        if job.status != "cancelled":
            _update_job(
                job,
                db,
                status="completed",
                progress=100,
                output_data={"final_output": current_text},
            )
            print(f"[DONE] Job {job_id} completed successfully")
        db.close()

    except Exception as e:
        print(f"[ERROR] Job {job_id} failed: {e}")
        db = SessionLocal()
        job = db.get(Job, job_id)
        if job:
            _update_job(job, db, status="failed", output_data={"error": str(e)})
        db.close()
