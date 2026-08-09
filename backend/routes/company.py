from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from extensions import db, cache
from models import CompanyProfile, PlacementDrive, Application, Placement, APPLICATION_STATUSES
from utils import role_required

company_bp = Blueprint("company", __name__, url_prefix="/api/company")

def _get_company_or_404():
    return CompanyProfile.query.filter_by(user_id=current_user.id).first_or_404()
#plan: profiles, drives, then aro minute details like application status, interview, CSV

@company_bp.get("/profile")
@login_required
@role_required("company")
def get_profile():
    company = _get_company_or_404()
    return jsonify(company.to_dict())


@company_bp.put("/profile")
@login_required
@role_required("company")
def update_profile():
    company = _get_company_or_404()
    data = request.get_json(force=True) or {}
    for field in ("company_name", "industry", "hr_contact", "hr_email", "website", "location", "description"):
        if field in data:
            setattr(company, field, data[field])
    db.session.commit()
    cache.clear()
    return jsonify(company.to_dict())


@company_bp.get("/drives")
@login_required
@role_required("company")
def list_own_drives():
    company = _get_company_or_404()
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(
        PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict(include_company=False) for d in drives])


@company_bp.post("/drives")
@login_required
@role_required("company")
def create_drive():
    company = _get_company_or_404()
    if company.approval_status != "approved":
        return jsonify({"error": "company must be approved by admin before creating drives"}), 403

    data = request.get_json(force=True) or {}
    required = ("job_title", "application_deadline")
    if not all(data.get(f) for f in required):
        return jsonify({"error": f"required fields: {required}"}), 400

    try:
        deadline = datetime.strptime(data["application_deadline"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "application_deadline must be YYYY-MM-DD"}), 400

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data["job_title"],
        job_description=data.get("job_description"),
        skills_required=data.get("skills_required"),
        experience_required=data.get("experience_required"),
        benefits=data.get("benefits"),
        eligibility_branch=data.get("eligibility_branch", "Any"),
        eligibility_cgpa=float(data.get("eligibility_cgpa") or 0),
        eligibility_year=int(data["eligibility_year"]) if data.get("eligibility_year") else None,
        salary=float(data.get("salary")) if data.get("salary") else None,
        location=data.get("location"),
        application_deadline=deadline,
        status="pending",
    )
    db.session.add(drive)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "drive created, pending admin approval", "drive": drive.to_dict()}), 201


@company_bp.post("/drives/<int:drive_id>/complete")
@login_required
@role_required("company")
def mark_drive_complete(drive_id):
    company = _get_company_or_404()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    drive.status = "closed"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "drive marked as complete", "drive": drive.to_dict()})


@company_bp.get("/drives/<int:drive_id>/applications")
@login_required
@role_required("company")
def drive_applications(drive_id):
    company = _get_company_or_404()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()
    apps = Application.query.filter_by(drive_id=drive.id).all()
    return jsonify([a.to_dict() for a in apps])

@company_bp.get("/applications/<int:application_id>/resume")
@login_required
@role_required("company")
def download_applicant_resume(application_id):
    from flask import send_from_directory, current_app
    company = _get_company_or_404()
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "forbidden"}), 403
    student = application.student
    if not student or not student.resume_filename:
        return jsonify({"error": "this student hasn't uploaded a resume"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], student.resume_filename, as_attachment=True)

@company_bp.post("/applications/<int:application_id>/status")
@login_required
@role_required("company")
def update_application_status(application_id):
    company = _get_company_or_404()
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in APPLICATION_STATUSES:
        return jsonify({"error": f"invalid status, must be one of {APPLICATION_STATUSES}"}), 400

    application.status = new_status
    application.remark = data.get("remark", application.remark)
    application.feedback = data.get("feedback", application.feedback)

    if new_status == "placed":
        existing = Placement.query.filter_by(application_id=application.id).first()
        if not existing:
            drive = application.drive
            joining_date = None
            if data.get("joining_date"):
                try:
                    joining_date = datetime.strptime(data["joining_date"], "%Y-%m-%d").date()
                except ValueError:
                    pass
            placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                drive_id=drive.id,
                application_id=application.id,
                position=data.get("position", drive.job_title),
                salary=float(data.get("salary")) if data.get("salary") else drive.salary,
                joining_date=joining_date,
            )
            db.session.add(placement)

    db.session.commit()
    cache.clear()
    return jsonify({"message": "status updated", "application": application.to_dict()})


@company_bp.post("/applications/<int:application_id>/schedule-interview")
@login_required
@role_required("company")
def schedule_interview(application_id):
    company = _get_company_or_404()
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(force=True) or {}
    interview_date_raw = data.get("interview_date")  # expects "YYYY-MM-DDTHH:MM"
    if not interview_date_raw:
        return jsonify({"error": "interview_date is required"}), 400
    try:
        interview_date = datetime.strptime(interview_date_raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        return jsonify({"error": "interview_date must be in 'YYYY-MM-DDTHH:MM' format"}), 400

    application.interview_date = interview_date
    application.interview_mode = data.get("interview_mode", "Online")
    application.status = "interview"
    db.session.commit()
    return jsonify({"message": "interview scheduled", "application": application.to_dict()})


@company_bp.post("/export-csv")
@login_required
@role_required("company")
def export_csv():
    #ekhane celery use hobe, remember to add it in end me
    from tasks import export_company_applications_csv_task
    company = _get_company_or_404()
    task = export_company_applications_csv_task.delay(company.id)
    return jsonify({"message": "export started", "task_id": task.id}), 202


@company_bp.get("/export-status/<task_id>")
@login_required
@role_required("company")
def export_status(task_id):
    from extensions import celery
    task = celery.AsyncResult(task_id)
    response = {"task_id": task_id, "state": task.state}
    if task.state == "SUCCESS":
        response["result"] = task.result
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
    return jsonify(response)


@company_bp.get("/export-download/<path:filename>")
@login_required
@role_required("company")
def export_download(filename):
    from flask import send_from_directory, current_app
    return send_from_directory(current_app.config["EXPORT_FOLDER"], filename, as_attachment=True)
