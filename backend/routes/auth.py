from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, cache
from models import User, CompanyProfile, StudentProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(force=True) or {}
    role = data.get("role")#role er jonne tut e diff model baniyeche, amar ta orom  noy
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip()

    if role not in ("student", "company"):
        return jsonify({"error": "Role must be either 'Student' or 'Company'"}), 400
    if not username or not password:
        return jsonify({"error": "Username and Password are required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Oops! Username is already taken.."}), 409
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Oops! Email is already registered.."}), 409 #duplicate email is a noo noo 

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  #assigning a new user.id before we commit

    if role == "student":
        name = (data.get("name") or "").strip()
        department = (data.get("department") or "").strip()
        phone = (data.get("phone") or "").strip()
        
        if not phone.isdigit() or len(phone) != 10:
            return jsonify({"error": "Phone number must be exactly 10 digits"}), 400

        if not name or not department or not phone:
            return jsonify({"error": "Name, department and phone num are required"}), 400

        if data.get("cgpa") in (None, "") or data.get("year") in (None, ""):
            return jsonify({"error": "CGPA and graduation year are required"}), 400

        profile = StudentProfile(
            user_id=user.id,
            name=name,
            department=department,
            skills=(data.get("skills") or "").strip(),
            cgpa=float(data["cgpa"]),
            year=int(data["year"]),
            phone=phone,
        )
        db.session.add(profile)
    else:
        company_name = (data.get("company_name") or "").strip()
        industry = (data.get("industry") or "").strip()
        hr_contact = (data.get("hr_contact") or "").strip()
        hr_email = (data.get("hr_email") or "").strip()
        location = (data.get("location") or "").strip()

        if not all([company_name, industry, hr_contact, hr_email, location]):#imp details are made necessary to register
            return jsonify({"error": "All company details are required (excluding website and description)"}), 400

        profile = CompanyProfile(
            user_id=user.id,
            company_name=data.get("company_name") or username,
            industry=data.get("industry"),
            hr_contact=data.get("hr_contact"),
            hr_email=data.get("hr_email"),
            website=data.get("website"),
            location=data.get("location"),
            description=data.get("description"),
            approval_status="pending",
        )
        db.session.add(profile)

    db.session.commit()
    cache.delete("admin_dashboard_stats")
    return jsonify({"message": "Registered successfully.",
                     "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password): #authentication timeee
        return jsonify({"error": "Invalid credentials"}), 401
    if user.is_blacklisted or not user.is_active_flag:
        return jsonify({"error": "Account is inactive"}), 403

    login_user(user,remember=True)
    return jsonify({"message": "Logged in successfully", "user": _user_payload(user)})

@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user": _user_payload(current_user)})


def _user_payload(user):
    payload = user.to_dict()
    if user.role == "student" and user.student_profile:
        payload["profile"] = user.student_profile.to_dict()
    elif user.role == "company" and user.company_profile:
        payload["profile"] = user.company_profile.to_dict()
    return payload