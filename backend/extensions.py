from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from celery import Celery

db = SQLAlchemy()
cache = Cache()
login_manager = LoginManager()
login_manager.session_protection = "strong"

celery = Celery(__name__)