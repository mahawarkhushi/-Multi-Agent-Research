import threading
import time
from sqlalchemy.orm import sessionmaker
from app.db.base import engine
from app.db.job import Job
from app.services.agent_orchestrator import AgentOrchestrator

SessionLocal = sessionmaker(bind=engine)
orchestrator = AgentOrchestrator()

def run_job_in_background(job_id: str):
    thread = threading.Thread(target=_process_job, args=(job_id,), daemon=True)
    thread.start()

def _update_job(job: Job, db, *, status=None, progress=None, output_data=None):
    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if output_data is not None:
        job.output_data = output_data
    db.commit()

def _process_job(job_id: str):
    db = SessionLocal()
    job = db.get(Job, job_id)
    if not job:
        db.close()
        print(f"[ERROR] Job {job_id} not found")
        return
    if job.status != "pending":
        db.close()
        return

    # Mark as running
    _update_job(job, db, status="running", progress=0)

    stages = ["ingestion", "research", "citation", "formatting", "compliance"]
    total_stages = len(stages)
    current_text = job.input_data.get("text", "") if job.input_data else ""

    try:
        for idx, stage in enumerate(stages):
            stage_output = orchestrator.run_single(stage, current_text)
            current_text = stage_output

            # smooth progress update
            for tick in range(1, 21):
                time.sleep(0.2)
                db_inner = SessionLocal()
                job_inner = db_inner.get(Job, job_id)
                stage_progress = ((idx + tick/20)/total_stages) * 100
                _update_job(job_inner, db_inner, progress=int(stage_progress))
                db_inner.close()

                db_inner = SessionLocal()
                job_inner = db_inner.get(Job, job_id)
                if job_inner.status == "cancelled":
                    db_inner.close()
                    return
                db_inner.close()

        db_final = SessionLocal()
        job_final = db_final.get(Job, job_id)
        if job_final.status != "cancelled":
            _update_job(job_final, db_final, status="completed", progress=100,
                        output_data={"final_report": current_text})
        db_final.close()
    except Exception as e:
        db_error = SessionLocal()
        job_error = db_error.get(Job, job_id)
        if job_error:
            _update_job(job_error, db_error, status="failed", output_data={"error": str(e)})
        db_error.close()
