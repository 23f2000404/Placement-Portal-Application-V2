from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from celery import Celery

db = SQLAlchemy()
cache = Cache()
login_manager = LoginManager()
login_manager.session_protection = "strong"

celery = Celery(__name__)

def make_celery(app):    
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
    )

    # run korte hobe Celery tasks inside the app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
