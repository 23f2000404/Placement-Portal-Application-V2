import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "placement_portal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    CACHE_REDIS_DB = 1
    CACHE_DEFAULT_TIMEOUT = 60

    # Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
