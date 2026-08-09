"""
Run the Celery worker: celery -A celery_worker.celery worker --loglevel=info

Run Celery beat separately: celery -A celery_worker.celery beat --loglevel=info
"""

from celery.schedules import crontab

from app import create_app
from extensions import make_celery
import tasks  # noqa: F401  (import so celery registers the tasks)

flask_app = create_app()
celery = make_celery(flask_app)

celery.conf.beat_schedule = {
    "daily-deadline-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    "interview-reminders": {
        "task": "tasks.send_interview_reminders",
        "schedule": crontab(minute=0, hour="8,18"),
    },
    "monthly-activity-report-admin": {
        "task": "tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),
    },
    "monthly-activity-report-companies": {
        "task": "tasks.generate_company_monthly_reports",
        "schedule": crontab(day_of_month=1, hour=6, minute=30),  # shortly after the admin report
    },
}
celery.conf.timezone = "UTC"
