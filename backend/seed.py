# Shurur time e creating the db and admin account

from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    db.create_all()

    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        print(f"Admin already exists: {existing_admin.username}")
    else:
        admin = User(
            username=app.config["ADMIN_USERNAME"],
            email=app.config["ADMIN_EMAIL"],
            role="admin",
        ) #kono error hole this format will help in debugging tai rakchi etai
        
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin: {admin.username}")

    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")