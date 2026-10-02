# Task 4: Job Board Platform

CodeAlpha Backend Development Internship project built with **Django**, **SQLite** and **Tailwind CSS**.

## Features
- Two roles: **Employer** and **Candidate** (chosen at sign up)
- Employers: post, edit, close and delete jobs; view applicants; update application status; dashboard with counts
- Candidates: search jobs, upload resumes (PDF/DOC/DOCX, max 5 MB), apply with a cover letter, track application status
- Job search with filters: keyword, location, job type, plus pagination
- Notifications: employer is notified of new applications, candidate is notified when the status changes
- Resume files are private: only the owner, the employer who received it, or staff can download
- Django admin panel for all models
- JSON API endpoints

## Setup
```bash
cd task4_job_board
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # optional: demo accounts and sample jobs
python manage.py runserver
```
Open http://127.0.0.1:8000

Demo logins (after `seed_demo`): `demo_employer` / `demo12345` and `demo_candidate` / `demo12345`.

Admin panel: run `python manage.py createsuperuser`, then open http://127.0.0.1:8000/admin

Tailwind CSS is loaded from the Tailwind CDN in `jobs/templates/base.html`, so an internet connection is needed to see the styling.

## API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/?q=&location=&type=` | Search open jobs (type: full_time, part_time, contract, internship) |
| GET | `/api/jobs/<id>/` | Job details |
| GET | `/api/my-applications/` | Logged-in candidate's applications and statuses |

## Project structure
```
task4_job_board/
  manage.py
  jobboard/            project settings and root urls
  jobs/
    models.py          Employer, Candidate, Resume, Job, Application, Notification
    views.py           pages, search, apply flow, status updates, JSON API
    forms.py           forms styled with Tailwind classes
    urls.py
    admin.py
    templates/         Tailwind HTML templates
    management/commands/seed_demo.py
```
