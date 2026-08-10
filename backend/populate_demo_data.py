from app import create_app
from extensions import db
from models import User, CompanyProfile, StudentProfile, PlacementDrive, Application
from datetime import date, timedelta

TODAY = date.today()

app = create_app()
with app.app_context():
    # 3 companies, 4 students, 3 drives then 4 applications (sample data is generated just for demo)
    company_users = [
        User(username="techcorp_hr", email="hr@techcorp.com", role="company"),
        User(username="innovatesoft_hr", email="hr@innovatesoft.com", role="company"),
        User(username="datasystems_hr", email="hr@datasystems.com", role="company"),
    ]
    for u in company_users:
        u.set_password("company123")
        db.session.add(u)
    db.session.flush()

    companies = [
        CompanyProfile(
            user_id=company_users[0].id, company_name="TechCorp", industry="IT Services",
            hr_contact="John Doe", hr_email="hr@techcorp.com", website="https://techcorp.com",
            location="Bangalore", approval_status="approved"
        ),
        CompanyProfile(
            user_id=company_users[1].id, company_name="InnovateSoft", industry="Fintech",
            hr_contact="Sarah Chen", hr_email="hr@innovatesoft.com", website="https://innovatesoft.com",
            location="Mumbai", approval_status="pending"
        ),
        CompanyProfile(
            user_id=company_users[2].id, company_name="DataSystems Inc", industry="Data Analytics",
            hr_contact="Mike Johnson", hr_email="hr@datasystems.com", website="https://datasystems.com",
            location="Pune", approval_status="approved"
        ),
    ]
    for c in companies:
        db.session.add(c)
    db.session.flush()

    student_users = [
        User(username="priya_sharma", email="priya@student.com", role="student"),
        User(username="raj_patel", email="raj@student.com", role="student"),
        User(username="anjali_kumar", email="anjali@student.com", role="student"),
        User(username="arjun_singh", email="arjun@student.com", role="student"),
    ]
    for u in student_users:
        u.set_password("student123")
        db.session.add(u)
    db.session.flush()

    students = [
        StudentProfile(
            user_id=student_users[0].id, name="Priya Sharma", department="CSE",
            skills="Python, SQL, React", cgpa=8.2, year=2026, phone="9876543210"
        ),
        StudentProfile(
            user_id=student_users[1].id, name="Raj Patel", department="IT",
            skills="Java, Spring Boot, MySQL", cgpa=7.9, year=2026, phone="9876543211"
        ),
        StudentProfile(
            user_id=student_users[2].id, name="Anjali Kumar", department="CSE",
            skills="Python, ML, TensorFlow", cgpa=8.5, year=2026, phone="9876543212"
        ),
        StudentProfile(
            user_id=student_users[3].id, name="Arjun Singh", department="IT",
            skills="C++, Data Structures, JavaScript", cgpa=7.5, year=2026, phone="9876543213"
        ),
    ]
    for s in students:
        db.session.add(s)
    db.session.flush()

    drives = [
        PlacementDrive(
            company_id=companies[0].id, job_title="Senior Software Engineer",
            job_description="Build scalable backend systems.",
            skills_required="Python, Go, Docker", experience_required="Fresher",
            benefits="Health insurance, relocation, stock options",
            eligibility_branch="CSE,IT", eligibility_cgpa=7.5, eligibility_year=2026,
            salary=1500000, location="Bangalore",
            application_deadline=TODAY + timedelta(days=15), status="approved"
        ),
        PlacementDrive(
            company_id=companies[0].id, job_title="Data Scientist",
            job_description="Analyze complex datasets, build ML models.",
            skills_required="Python, SQL, TensorFlow", experience_required="2+ years",
            benefits="Stock options, remote work",
            eligibility_branch="CSE,IT", eligibility_cgpa=8.0, eligibility_year=2026,
            salary=1200000, location="Bangalore",
            application_deadline=TODAY + timedelta(days=30), status="approved"
        ),
        PlacementDrive(
            company_id=companies[2].id, job_title="Backend Developer",
            job_description="Develop REST APIs, microservices.",
            skills_required="Java, Spring Boot, MySQL", experience_required="1+ years",
            benefits="Health insurance",
            eligibility_branch="IT", eligibility_cgpa=7.0, eligibility_year=2026,
            salary=1000000, location="Pune",
            application_deadline=TODAY + timedelta(days=45), status="approved"
        ),
    ]
    for d in drives:
        db.session.add(d)
    db.session.flush()


    applications = [
        Application(student_id=students[0].id, drive_id=drives[0].id, status="applied"),
        Application(student_id=students[1].id, drive_id=drives[1].id, status="shortlisted"),
        Application(student_id=students[2].id, drive_id=drives[2].id, status="rejected"),
        Application(student_id=students[3].id, drive_id=drives[0].id, status="applied"),
    ]
    for a in applications:
        db.session.add(a)

    db.session.commit()
    print("Demo data inserted!")
    print("\nSome such accounts:")
    print("Admin: admin / admin123")
    print("Company: techcorp_hr / company123")
    print("Student: priya_sharma / student123")