from flask import Flask, render_template, jsonify, session
import os

from config import Config
from extensions import db, cache, login_manager, make_celery
from models import User
from datetime import timedelta

def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    make_celery(app)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7) #sesh kept logging out for every reload ahannn

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        #i could use User.query.get(int(user_id)) but ig eta more efficient

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Authentication required"}), 401
    
    # Registering da blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    @app.route("/")
    @app.route("/<path:_any>")   #SPA frontend?
    def index(_any=None):
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True,port=5000)
