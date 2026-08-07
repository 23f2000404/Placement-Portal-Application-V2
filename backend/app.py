import os
from flask import Flask

from config import Config
from extensions import db, cache, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)



    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
