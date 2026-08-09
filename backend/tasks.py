import os
import csv
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from flask import current_app

from extensions import celery, db
from models import StudentProfile, PlacementDrive, Application, CompanyProfile, Placement

logger = logging.getLogger("placement_portal.tasks")
logging.basicConfig(level=logging.INFO) #fall back: console logging

#jobs - scheduled(reminders and reports), user-trigg(exports) 

# Notification helpers

def _send_gchat_message(text):
    webhook = current_app.config.get("GCHAT_WEBHOOK_URL")
    if not webhook:
        logger.info("[GCHAT-SIM] %s", text)
        return
    try:
        requests.post(webhook, json={"text": text}, timeout=5)
    except Exception as e:
        logger.warning("Failed to send Google Chat webhook: %s", e) #being extra cautious here cuz first time implementing webhook usage


def _send_email(to_addr, subject, html_body): # sending an email using the configured SMTP server
    server = current_app.config.get("MAIL_SERVER")

    if not server or not to_addr: #if any crucial email info is missing, that's handled
        logger.info("[EMAIL-SIM] To: %s | Subject: %s\n%s", to_addr, subject, html_body)
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = current_app.config["MAIL_SENDER"]
        msg["To"] = to_addr

        msg.attach(MIMEText(html_body, "html")) 
        with smtplib.SMTP(server, current_app.config["MAIL_PORT"]) as smtp: #standard pattern yehi hai, needed help here ngl
            smtp.starttls()
            smtp.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            smtp.sendmail(msg["From"], [to_addr], msg.as_string())

    except Exception as e:
        logger.warning("Failed to send email: %s", e)


# Deadline reminders
@celery.task(name="tasks.send_daily_reminders") # wrapped s.t. this function runs as a background Celery task
def send_daily_reminders():
    today = datetime.utcnow().date()
    upcoming_cutoff = today + timedelta(days=3)

    drives = PlacementDrive.query.filter(
        PlacementDrive.status == "approved",
        PlacementDrive.application_deadline >= today,
        PlacementDrive.application_deadline <= upcoming_cutoff,
    ).all()

    if not drives:
        logger.info("No drives closing in the next 3 days. No reminders sent.")
        return {"reminders_sent": 0}

    students = StudentProfile.query.all()
    count = 0
    for student in students:
        already_applied_ids = {a.drive_id for a in student.applications}
        relevant = [d for d in drives if d.id not in already_applied_ids]
        if not relevant:
            continue
        lines = "\n".join(
            f"- {d.job_title} ({d.company.company_name}) closes on {d.application_deadline}"
            for d in relevant
        )
        text = (f"Hi {student.name}, you have {len(relevant)} placement drive(s) closing soon:\n{lines}\n"
                f"Log in to the Placement Portal to apply before the deadline.")
        _send_gchat_message(text)
        count += 1

    logger.info("Daily deadline reminders sent to %s students.", count)
    return {"reminders_sent": count}

# Interview reminders
@celery.task(name="tasks.send_interview_reminders")
def send_interview_reminders():
    now = datetime.utcnow()
    window_end = now + timedelta(hours=24)

    upcoming = Application.query.filter(
        Application.status == "interview",
        Application.interview_date.isnot(None),
        Application.interview_date >= now,
        Application.interview_date <= window_end,
    ).all()

    count = 0
    for application in upcoming:
        student = application.student
        drive = application.drive
        if not student or not drive:
            continue
        text = (f"Hi {student.name}, reminder: you have an interview for '{drive.job_title}' "
                f"at {drive.company.company_name} on {application.interview_date} "
                f"({application.interview_mode or 'mode not specified'}). Good luck!")
        _send_gchat_message(text)
        count += 1

    logger.info("Interview reminders sent for %s upcoming interviews.", count)
    return {"interview_reminders_sent": count}

# Monthly reports

def _month_bounds():
    now = datetime.utcnow()
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)
    return first_of_last_month, first_of_this_month


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():

    first_of_last_month, first_of_this_month = _month_bounds()

    drives_last_month = PlacementDrive.query.filter(
        PlacementDrive.created_at >= first_of_last_month,
        PlacementDrive.created_at < first_of_this_month,
    ).all()
    applications_last_month = Application.query.filter(
        Application.application_date >= first_of_last_month,
        Application.application_date < first_of_this_month,
    ).all()
    placed_last_month = Placement.query.filter(
        Placement.created_at >= first_of_last_month,
        Placement.created_at < first_of_this_month,
    ).all()

    month_label = first_of_last_month.strftime("%B %Y")
    html = f"""
    <html><body style="font-family: Arial, sans-serif; color:#333;">
      <h2 style="color:#7c3aed;">Placement Portal - Monthly Activity Report ({month_label})</h2>
      <ul>
        <li><b>Drives conducted:</b> {len(drives_last_month)}</li>
        <li><b>Students applied:</b> {len(applications_last_month)}</li>
        <li><b>Students placed:</b> {len(placed_last_month)}</li>
      </ul>
      <h3>Drives</h3>
      <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
        <tr style="background:#ede9fe;"><th>Job Title</th><th>Company</th><th>Status</th></tr>
        {''.join(f"<tr><td>{d.job_title}</td><td>{d.company.company_name}</td><td>{d.status}</td></tr>" for d in drives_last_month)}
      </table>
    </body></html>
    """

    admin_email = current_app.config.get("ADMIN_EMAIL")
    _send_email(admin_email, f"Monthly Placement Report - {month_label}", html)

    reports_dir = current_app.config["EXPORT_FOLDER"]
    os.makedirs(reports_dir, exist_ok=True)
    filepath = os.path.join(reports_dir, f"monthly_report_admin_{first_of_last_month.strftime('%Y_%m')}.html")
    with open(filepath, "w") as f:
        f.write(html)

    logger.info("Admin monthly report generated for %s and emailed to %s", month_label, admin_email)
    return {"month": month_label, "drives": len(drives_last_month),
            "applications": len(applications_last_month), "placed": len(placed_last_month)}


@celery.task(name="tasks.generate_company_monthly_reports")
def generate_company_monthly_reports():
    first_of_last_month, first_of_this_month = _month_bounds()
    month_label = first_of_last_month.strftime("%B %Y")

    reports_dir = current_app.config["EXPORT_FOLDER"]
    os.makedirs(reports_dir, exist_ok=True)

    companies = CompanyProfile.query.filter_by(approval_status="approved").all()
    generated = 0

    for company in companies:
        drive_ids = [d.id for d in company.drives]
        applications = Application.query.filter(Application.drive_id.in_(drive_ids)).filter(
            Application.application_date >= first_of_last_month,
            Application.application_date < first_of_this_month,
        ).all() if drive_ids else []
        placements = [p for p in company.placements
                      if first_of_last_month <= p.created_at < first_of_this_month]

        status_counts = {}
        for a in applications:
            status_counts[a.status] = status_counts.get(a.status, 0) + 1

        html = f"""
        <html><body style="font-family: Arial, sans-serif; color:#333;">
          <h2 style="color:#7c3aed;">{company.company_name} - Monthly Placement Report ({month_label})</h2>
          <p><b>Total applications received:</b> {len(applications)}</p>
          <p><b>Students placed:</b> {len(placements)}</p>
          <h3>Application status breakdown</h3>
          <ul>
            {''.join(f"<li>{status}: {count}</li>" for status, count in status_counts.items()) or '<li>No applications this month.</li>'}
          </ul>
        </body></html>
        """
        filepath = os.path.join(
            reports_dir, f"monthly_report_company_{company.id}_{first_of_last_month.strftime('%Y_%m')}.html"
        )
        with open(filepath, "w") as f:
            f.write(html)

        _send_email(company.hr_email, f"Monthly Placement Report - {month_label}", html)
        generated += 1

    logger.info("Generated %s per-company monthly reports for %s", generated, month_label)
    return {"month": month_label, "reports_generated": generated}


# Student CSV export
@celery.task(name="tasks.export_applications_csv_task")
def export_applications_csv_task(student_id):
    student = StudentProfile.query.get(student_id)
    if not student:
        raise ValueError("Student not found!")

    export_dir = current_app.config["EXPORT_FOLDER"]
    os.makedirs(export_dir, exist_ok=True)
    filename = f"applications_student_{student_id}_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    applications = Application.query.filter_by(student_id=student_id).all()
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Company Name", 
                         "Drive Title", "Application Status",
                          "Application Date"]) #debugging might be easier, date formats cause issues ltr sometimes
        for a in applications:
            writer.writerow([
                student_id,
                a.drive.company.company_name if a.drive and a.drive.company else "",
                a.drive.job_title if a.drive else "",
                a.status,
                a.application_date.strftime("%Y-%m-%d") if a.application_date else "",
            ])

    # sends an alert once done
    _send_gchat_message(f"Hi {student.name}, your application history export is ready: {filename}")
    logger.info("CSV export ready for student %s: %s", student_id, filename)
    return {"filename": filename, "download_url": f"/api/student/export-download/{filename}"}

# Company CSV export
@celery.task(name="tasks.export_company_applications_csv_task")
def export_company_applications_csv_task(company_id):
    company = CompanyProfile.query.get(company_id)
    if not company:
        raise ValueError("Company not found!")

    export_dir = current_app.config["EXPORT_FOLDER"]
    os.makedirs(export_dir, exist_ok=True)
    filename = f"applications_company_{company_id}_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    drive_ids = [d.id for d in company.drives]
    applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all() if drive_ids else []

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student Name", "Drive Title", "Application Status", "Application Date"])
        for a in applications:
            writer.writerow([
                a.student.name if a.student else "",
                a.drive.job_title if a.drive else "",
                a.status,
                a.application_date.strftime("%Y-%m-%d") if a.application_date else "",
            ])

    _send_gchat_message(f"Hi {company.company_name}, your application history export is ready: {filename}")
    logger.info("CSV export ready for company %s: %s", company_id, filename)
    return {"filename": filename, "download_url": f"/api/company/export-download/{filename}"}
