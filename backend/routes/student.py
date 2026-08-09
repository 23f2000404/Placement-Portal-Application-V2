import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db, cache
from models import StudentProfile, PlacementDrive, Application, Placement, CompanyProfile
from utils import role_required

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


def _get_student_or_404():
    return StudentProfile.query.filter_by(user_id=current_user.id).first_or_404()


@student_bp.get("/profile")
@login_required
@role_required("student")
def get_profile():
    return jsonify(_get_student_or_404().to_dict())


@student_bp.put("/profile")
@login_required
@role_required("student")
def update_profile():
    student = _get_student_or_404()
    data = request.get_json(force=True) or {}
    for field in ("name", "department", "phone", "skills"):
        if field in data:
            setattr(student, field, data[field])
    if "cgpa" in data:
        student.cgpa = float(data["cgpa"])
    if "year" in data:
        student.year = int(data["year"])
    db.session.commit()
    return jsonify(student.to_dict())

@student_bp.post("/profile/resume")
@login_required
@role_required("student")
def upload_resume():
    student = _get_student_or_404()
    if "resume" not in request.files:
        return jsonify({"error": "No file part named 'resume'"}), 400
    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_RESUME_EXTENSIONS"]:
        return jsonify({"error": "Only PDF, DOC, or DOCX files are allowed"}), 400

    filename = secure_filename(f"student_{student.id}_{file.filename}")
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    student.resume_filename = filename
    db.session.commit()
    return jsonify({"message": "Resume has been uploaded.", "resume_filename": filename})

@student_bp.get("/profile/resume")
@login_required
@role_required("student")
def download_own_resume():
    student = _get_student_or_404()
    if not student.resume_filename:
        return jsonify({"error": "No resume uploaded"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], student.resume_filename, as_attachment=True)

@student_bp.get("/drives")
@login_required
@role_required("student")
@cache.cached(timeout=30, query_string=True)
def list_available_drives():

    q = (request.args.get("q") or "").strip()
    only_eligible = request.args.get("eligible_only") == "true"

    query = PlacementDrive.query.filter_by(status="approved")
    if q:
        like = f"%{q}%"
        query = query.join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id).filter(
            db.or_(
                PlacementDrive.job_title.ilike(like),
                PlacementDrive.skills_required.ilike(like),
                CompanyProfile.company_name.ilike(like),
            )
        )
    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()

    if only_eligible:
        student = _get_student_or_404()
        drives = [d for d in drives if _is_eligible(student, d)]

    return jsonify([d.to_dict() for d in drives])


def _is_eligible(student, drive):
    if drive.eligibility_cgpa and student.cgpa < drive.eligibility_cgpa:
        return False
    if drive.eligibility_year and student.year and drive.eligibility_year != student.year:
        return False
    if drive.eligibility_branch and drive.eligibility_branch.lower() != "any":
        branches = [b.strip().lower() for b in drive.eligibility_branch.split(",")]
        if (student.department or "").lower() not in branches:
            return False
    return True


@student_bp.get("/drives/<int:drive_id>")
@login_required
@role_required("student")
def drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    return jsonify(drive.to_dict())


@student_bp.post("/drives/<int:drive_id>/apply")
@login_required
@role_required("student")
def apply_to_drive(drive_id):
    student = _get_student_or_404()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        return jsonify({"error": "You have already applied to this drive"}), 409

    if not _is_eligible(student, drive):
        return jsonify({"error": "You do not meet the eligibility criteria for this drive"}), 403

    
    from sqlalchemy.exc import IntegrityError
    application = Application(student_id=student.id, drive_id=drive.id, status="applied")
    db.session.add(application)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "You have already applied to this drive"}), 409
    return jsonify({"message": "Application got submitted", "application": application.to_dict()}), 201

@student_bp.get("/applications")
@login_required
@role_required("student")
def my_applications():
    student = _get_student_or_404()
    apps = Application.query.filter_by(student_id=student.id).order_by(
        Application.application_date.desc()).all()
    return jsonify([a.to_dict() for a in apps])


@student_bp.get("/history")
@login_required
@role_required("student")
def placement_history():
    """Complete placement history: every application and its final outcome."""
    student = _get_student_or_404()
    apps = Application.query.filter_by(student_id=student.id).all()
    return jsonify([a.to_dict() for a in apps])


@student_bp.get("/placements")
@login_required
@role_required("student")
def my_placements():
    """List of this student's final placement record(s), if any."""
    student = _get_student_or_404()
    placements = Placement.query.filter_by(student_id=student.id).all()
    return jsonify([p.to_dict() for p in placements])


@student_bp.get("/offer-letter/<int:application_id>")
@login_required
@role_required("student")
def download_offer_letter(application_id):
    from flask import Response
    student = _get_student_or_404()
    application = Application.query.filter_by(id=application_id, student_id=student.id).first_or_404()

    if application.status not in ("offer", "placed"):
        return jsonify({"error": "No offer/placement confirmation available for this application yet"}), 400

    drive = application.drive
    company = drive.company
    placement = Placement.query.filter_by(application_id=application.id).first()

    title = "Placement Confirmation" if application.status == "placed" else "Offer Letter"
    salary = (placement.salary if placement else drive.salary) or "As discussed"
    joining = placement.joining_date.isoformat() if placement and placement.joining_date else "To be communicated"
    position = (placement.position if placement else None) or drive.job_title

    html = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 40px; color:#2e1065;">
      <h1 style="color:#7c3aed;">{title}</h1>
      <p>Dear {student.name},</p>
      <p>We are pleased to inform you that you have been {application.status} for the position of
         <b>{position}</b> at <b>{company.company_name}</b> through the Placement Portal.</p>
      <table cellpadding="6">
        <tr><td><b>Position</b></td><td>{position}</td></tr>
        <tr><td><b>Company</b></td><td>{company.company_name}</td></tr>
        <tr><td><b>Location</b></td><td>{drive.location or 'N/A'}</td></tr>
        <tr><td><b>Salary</b></td><td>{salary}</td></tr>
        <tr><td><b>Joining Date</b></td><td>{joining}</td></tr>
      </table>
      <p>Congratulations, and we wish you the very best!</p>
      <p><i>This is a system-generated document from the Placement Portal.</i></p>
    </body></html>
    """
    filename = f"{title.replace(' ', '_')}_{student.id}_{drive.id}.html"
    return Response(
        html, mimetype="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@student_bp.post("/export-csv")
@login_required
@role_required("student")
def export_csv():

    from tasks import export_applications_csv_task
    student = _get_student_or_404()
    task = export_applications_csv_task.delay(student.id)
    return jsonify({"message": "export started", "task_id": task.id}), 202


@student_bp.get("/export-status/<task_id>")
@login_required
@role_required("student")
def export_status(task_id):
    from extensions import celery
    task = celery.AsyncResult(task_id)
    response = {"task_id": task_id, "state": task.state}
    if task.state == "SUCCESS":
        response["result"] = task.result
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
    return jsonify(response)


@student_bp.get("/export-download/<path:filename>")
@login_required
@role_required("student")
def export_download(filename):
    return send_from_directory(current_app.config["EXPORT_FOLDER"], filename, as_attachment=True)
