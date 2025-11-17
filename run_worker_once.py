# run_worker_once.py
import os
from app.worker import celery_app
from app.celery_tasks import analyze_pr_task

# This command tells Celery to connect, run ONE task, and then exit.
# It's perfect for a Cron Job.
if __name__ == "__main__":
    print("Cron Worker: Waking up...")
    
    # We must set the environment variable that Celery needs
    # This is normally done by docker-compose, but we do it manually here
    os.environ.setdefault('CELERY_BROKER_URL', os.getenv('REDIS_URL'))
    
    # -A: Points to our app
    # -Q: Specifies the queue (default is 'celery')
    # --concurrency 1: Only run one task
    # -l info: Log info
    # 'worker' is the command
    celery_app.worker_main(
        argv=[
            'worker',
            '-A', 'app.worker.celery_app',
            '-Q', 'celery',
            '--concurrency', '1',
            '-l', 'info',
            '--exit-on-complete', # <-- This is the magic flag
        ]
    )
    print("Cron Worker: One task processed. Shutting down.")
