# Placement Portal Application (PPA) — V2

Flask + VueJS (CDN) + Bootstrap + SQLite + Redis + Celery

## Stack (matches mandatory requirements)
- **Flask** — REST API
- **VueJS 3** (global CDN build, no CLI/build step) — all UI, mounted from a single Jinja2 entry point
- **Bootstrap 5** — only CSS framework used (`static/css/style.css`)
- **SQLite** — created programmatically via SQLAlchemy models (`seed.py`)
- **Redis** — backs both Flask-Caching (dashboard/drive listing caching) and the Celery broker/result backend
- **Celery + Redis** — background jobs (daily reminders, monthly report, async CSV export)

## Folder structure
```
placement_portal/
├── backend/
│   ├── app.py            
│   ├── config.py
│   ├── extensions.py     # db, cache, login_manager, celery
│   ├── models.py         # User, CompanyProfile, StudentProfile, PlacementDrive, Application
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── company.py
│   │   └── student.py
│   ├── tasks.py          # Celery tasks (reminders, monthly report, CSV export)
│   ├── celery_worker.py  # celery app + beat schedule
│   ├── seed.py           # creates DB tables + the one admin user
│   ├── requirements.txt
│   ├── uploads/          # resumes
│   └── exports/          # generated CSVs / HTML reports
└── frontend/
    ├── templates/
    │   └── index.html    # the ONLY Jinja2 template (Vue CDN entry point)
    └── static/
        ├── css/style.css
        └── js/
            ├── api.js
            ├── router.js
            ├── app.js
            └── components/*.js
```

## Prerequisites
- Python 3.10+
- Redis server running locally (`redis-server`)

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed.py
```

## Running the app (3 terminals, all from `backend/`)

**Terminal 1 — Flask app**
```bash
python app.py
# visit http://localhost:5000
```

**Terminal 2 — Celery worker** (requires Redis running)
```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 3 — Celery beat** (schedules the daily reminder + monthly report jobs)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

