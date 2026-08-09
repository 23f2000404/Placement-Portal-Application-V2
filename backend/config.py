import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "placement_portal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    CACHE_REDIS_DB = 1
    CACHE_DEFAULT_TIMEOUT = 60

    #session
    PERMANENT_SESSION_LIFETIME = 604800  #7 days
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  #CSRF protection


    #Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # Notifications
    GCHAT_WEBHOOK_URL = os.environ.get("GCHAT_WEBHOOK_URL", "")

    # Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "placement-portal@example.com")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")

    # Default admin credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
