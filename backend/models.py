from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from extensions import db

APPLICATION_STATUSES = (
    "applied", "shortlisted", "interview", #when company's deciding
    "offer", "rejected", "placed" #after
)

class User(db.Model, UserMixin):    
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active_flag = db.Column(db.Boolean, default=True) #kabhi is_active will be needed a func, confuse na hoi tai flag
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False,
                                       cascade="all, delete-orphan")
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False,
                                       cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # flask-login expects `is_active` property
    @property
    def is_active(self):
        return self.is_active_flag and not self.is_blacklisted

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active_flag,
            "is_blacklisted": self.is_blacklisted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(120))
    hr_contact = db.Column(db.String(120))
    hr_email = db.Column(db.String(120))  # gotta remember to use this for every company's monthly reports
    website = db.Column(db.String(200))
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default="pending")  # pending/approved/rejected

    drives = db.relationship("PlacementDrive", backref="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "hr_contact": self.hr_contact,
            "hr_email": self.hr_email,
            "website": self.website,
            "location": self.location,
            "description": self.description,
            "approval_status": self.approval_status,
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
        }


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120))
    skills = db.Column(db.String(255))
    cgpa = db.Column(db.Float, default=0.0)
    year = db.Column(db.Integer) #grad yr
    phone = db.Column(db.String(20))
    resume_filename = db.Column(db.String(255))

    applications = db.relationship("Application", backref="student", cascade="all, delete-orphan")
    placements = db.relationship("Placement", backref="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "department": self.department,
            "skills": self.skills,
            "cgpa": self.cgpa,
            "year": self.year,
            "phone": self.phone,
            "resume_filename": self.resume_filename,
            "is_blacklisted": self.user.is_blacklisted if self.user else False,
        }


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    skills_required = db.Column(db.String(255))
    experience_required = db.Column(db.String(120))
    benefits = db.Column(db.String(255))
    eligibility_branch = db.Column(db.String(150))  
    eligibility_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.Integer)
    salary = db.Column(db.Float)
    location = db.Column(db.String(120))
    application_deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default="pending")  # pending/approved/rejected/closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="drive", cascade="all, delete-orphan")
    placements = db.relationship("Placement", backref="drive", cascade="all, delete-orphan")

    def to_dict(self, include_company=True):
        d = {
            "id": self.id,
            "company_id": self.company_id,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "skills_required": self.skills_required,
            "experience_required": self.experience_required,
            "benefits": self.benefits,
            "eligibility_branch": self.eligibility_branch,
            "eligibility_cgpa": self.eligibility_cgpa,
            "eligibility_year": self.eligibility_year,
            "salary": self.salary,
            "location": self.location,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "status": self.status,
            "applicant_count": len(self.applications),
        }
        if include_company and self.company:
            d["company_name"] = self.company.company_name
        return d


class Application(db.Model):

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="applied")
    remark = db.Column(db.String(255))
    feedback = db.Column(db.Text)  # company's feedback shown to student or college

    #Interview scheduling
    interview_date = db.Column(db.DateTime)
    interview_mode = db.Column(db.String(50))  # Online, In-person type

    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "drive_id": self.drive_id,
            "drive_title": self.drive.job_title if self.drive else None,
            "company_name": self.drive.company.company_name if self.drive and self.drive.company else None,
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "status": self.status,
            "remark": self.remark,
            "feedback": self.feedback,
            "interview_date": self.interview_date.isoformat() if self.interview_date else None,
            "interview_mode": self.interview_mode,
            "resume_filename": self.student.resume_filename if self.student else None,
        }


class Placement(db.Model):
    #final placement record is created once an application is marked as placed
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=True)
    position = db.Column(db.String(150))
    salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("CompanyProfile", backref="placements")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "company_id": self.company_id,
            "company_name": self.company.company_name if self.company else None,
            "drive_id": self.drive_id,
            "position": self.position,
            "salary": self.salary,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
