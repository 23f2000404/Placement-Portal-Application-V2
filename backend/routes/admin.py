from flask import Blueprint, request, jsonify
from flask_login import login_required

from extensions import db, cache
from models import User, CompanyProfile, StudentProfile, PlacementDrive, Application, Placement
from utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/dashboard")
@login_required
@role_required("admin")
@cache.cached(timeout=60, key_prefix="admin_dashboard_stats")
def dashboard():
    stats = {
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "pending_company_approvals": CompanyProfile.query.filter_by(approval_status="pending").count(),
        "pending_drive_approvals": PlacementDrive.query.filter_by(status="pending").count(),
        "total_applications": Application.query.count(),
        "total_placed": Application.query.filter_by(status="placed").count(),
    }
    return jsonify(stats)


@admin_bp.get("/companies")
@login_required
@role_required("admin")
def list_companies():
    companies = CompanyProfile.query.all()
    return jsonify([c.to_dict() for c in companies])


@admin_bp.post("/companies/<int:company_id>/approve")
@login_required
@role_required("admin")
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()  #could cause production issues, usme we gotta specify which keys
    return jsonify({"message": "company approved", "company": company.to_dict()})


@admin_bp.post("/companies/<int:company_id>/reject")
@login_required
@role_required("admin")
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()
    return jsonify({"message": "company rejected", "company": company.to_dict()})


@admin_bp.post("/companies/<int:company_id>/blacklist")
@login_required
@role_required("admin")
def blacklist_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    user = company.user
    user.is_blacklisted = not user.is_blacklisted
    
    if user.is_blacklisted:
        for drive in company.drives:
            drive.status = "closed"
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()
    return jsonify({"message": "toggled blacklist", "is_blacklisted": user.is_blacklisted})


@admin_bp.get("/companies/<int:company_id>")
@login_required
@role_required("admin")
def get_company_detail(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    return jsonify(company.to_dict())


@admin_bp.get("/students")
@login_required
@role_required("admin")
def list_students():
    students = StudentProfile.query.all()
    return jsonify([s.to_dict() for s in students])


@admin_bp.post("/students/<int:student_id>/blacklist")
@login_required
@role_required("admin")
def blacklist_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    user = student.user
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()
    return jsonify({"message": "toggled blacklist", "is_blacklisted": user.is_blacklisted})


@admin_bp.get("/students/<int:student_id>")
@login_required
@role_required("admin")
def get_student_detail(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    return jsonify(student.to_dict())


@admin_bp.get("/drives")
@login_required
@role_required("admin")
def list_drives():
    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives])


@admin_bp.post("/drives/<int:drive_id>/approve")
@login_required
@role_required("admin")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()
    cache.delete("approved_drives_list")
    return jsonify({"message": "drive approved", "drive": drive.to_dict()})


@admin_bp.post("/drives/<int:drive_id>/reject")
@login_required
@role_required("admin")
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    cache.clear()
    return jsonify({"message": "drive rejected", "drive": drive.to_dict()})


@admin_bp.get("/drives/<int:drive_id>")
@login_required
@role_required("admin")
def get_drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    return jsonify(drive.to_dict())

@admin_bp.get("/applications")
@login_required
@role_required("admin")
def list_applications():
    apps = Application.query.order_by(Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])



@admin_bp.get("/placements")
@login_required
@role_required("admin")
def list_placements():
    placements = Placement.query.order_by(Placement.created_at.desc()).all()
    return jsonify([p.to_dict() for p in placements])

@admin_bp.get("/search/companies")
@login_required
@role_required("admin")
@cache.cached(timeout=30, query_string=True)
def search_companies():
    """Search companies by name or industry."""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([c.to_dict() for c in CompanyProfile.query.all()])
    like = f"%{q}%"
    companies = CompanyProfile.query.filter(
        db.or_(CompanyProfile.company_name.ilike(like), CompanyProfile.industry.ilike(like))
    ).all()
    return jsonify([c.to_dict() for c in companies])



@admin_bp.get("/search/students")
@login_required
@role_required("admin")
@cache.cached(timeout=30, query_string=True)
def search_students():
    q = (request.args.get("q") or "").strip()

    if not q:
        return jsonify([s.to_dict() for s in StudentProfile.query.all()])
    like = f"%{q}%"
    filters = [StudentProfile.name.ilike(like), StudentProfile.phone.ilike(like)]
    if q.isdigit():
        filters.append(StudentProfile.id == int(q))
    students = StudentProfile.query.filter(db.or_(*filters)).all()
    return jsonify([s.to_dict() for s in students])

@admin_bp.get("/search")
@login_required
@role_required("admin")
def search():

    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"companies": [], "students": []})
    like = f"%{q}%"
    company_filters = [CompanyProfile.company_name.ilike(like), CompanyProfile.industry.ilike(like)]
    student_filters = [StudentProfile.name.ilike(like), StudentProfile.phone.ilike(like)]
    if q.isdigit():
        student_filters.append(StudentProfile.id == int(q))
    companies = CompanyProfile.query.filter(db.or_(*company_filters)).all()
    students = StudentProfile.query.filter(db.or_(*student_filters)).all()
    return jsonify({
        "companies": [c.to_dict() for c in companies],
        "students": [s.to_dict() for s in students],
    })