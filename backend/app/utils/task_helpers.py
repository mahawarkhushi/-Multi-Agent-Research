from threading import Thread
from app.workers.job_worker import process_job

def run_job_in_background(job_id: str):
    thread = Thread(target=process_job, args=(job_id,))
    thread.start()
