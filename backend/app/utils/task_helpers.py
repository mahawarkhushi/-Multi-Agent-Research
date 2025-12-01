import threading
import time
from sqlalchemy.orm import Session
from app.db.job import Job
from app.dependencies import get_db

def run_job_in_background(job_id: str):
    """
    Runs a job asynchronously in a background thread.
    """
    thread = threading.Thread(target=_process_job, args=(job_id,), daemon=True)
    thread.start()


def _process_job(job_id: str):
    db: Session = next(get_db())
    job = db.query(Job).get(job_id)

    # Idempotency: do not run twice
    if not job or job.status not in ["pending"]:
        return

    try:
        job.status = "running"
        job.progress = 0
        db.commit()

        # Simulate long-running work
        for i in range(1, 101):
            time.sleep(0.05)  # ~5 seconds total

            job.progress = i
            db.commit()

            # Allow cancellation mid-way
            db.refresh(job)
            if job.status == "cancelled":
                return

        job.status = "completed"
        job.output_data = {
            "message": "Job completed successfully",
            "processed_input": job.input_data,
        }
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.output_data = {"error": str(e)}
        db.commit()
