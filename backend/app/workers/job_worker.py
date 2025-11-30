import time
from sqlalchemy.orm import Session
from app.db.job import Job
from app.dependencies import get_db

def process_job(job_id: str):
    db: Session = next(get_db())
    job = db.query(Job).get(job_id)
    if not job or job.status in ["completed", "failed", "cancelled"]:
        return

    job.status = "running"
    db.commit()

    try:
        # Example: processing input_data
        steps = ["Step 1: Agent orchestration", "Step 2: Tool execution", "Step 3: Compile output"]
        for step in steps:
            db.refresh(job)
            if job.status == "cancelled":
                return

            # Simulate work
            job.output_data = {"progress_step": step}
            db.commit()
            time.sleep(5)  # Replace with real LLM + tools calls

        # Job completed
        job.status = "completed"
        job.output_data = {"result": "Job completed successfully"}
        db.commit()
    except Exception as e:
        job.status = "failed"
        job.output_data = {"error": str(e)}
        db.commit()
