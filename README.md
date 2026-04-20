# Smart Academic Management System (SAMS)

A production-ready Django project implementing RBAC-based Academic Management with three roles:
- Admin
- Teacher
- Student

## 1) Tech Stack
- Backend: Django (MVT)
- Database (dev): SQLite
- Database (prod): PostgreSQL via `DATABASE_URL`
- Server: Gunicorn
- Static Files: WhiteNoise
- Frontend: HTML + CSS

## 2) Project Structure
- `core/` - project config (settings, urls, wsgi)
- `accounts/` - authentication, custom user, core academic models
- `admin_panel/` - admin module dashboards/workflows
- `teacher/` - teacher workflows (marks, attendance, assignments)
- `student/` - student dashboard and reports
- `templates/`, `static/`, `media/`

## 3) Key Features
- Django auth login/logout + session management
- Custom User model with role field (`ADMIN`, `TEACHER`, `STUDENT`)
- Role-based route protection using decorators
- Admin:
  - Create/delete users
  - Create/delete teacher/student profiles
  - Create classes and subjects
  - Assign teachers to subjects
  - View analytics
- Teacher:
  - Restricted to assigned subjects/students
  - Add/update marks with grade + percentage
  - Add/update daily attendance
  - Upload assignments
- Student:
  - View profile, marks, grade, attendance percentage
  - Download assignment files

## 4) Local Setup
1. Create and activate virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Seed sample data:
   ```bash
   python manage.py seed_sample_data
   ```
5. Run server:
   ```bash
   python manage.py runserver
   ```
6. Login with sample users:
   - Admin: `admin1` / `admin12345`
   - Teacher: `teacher1` / `teacher12345`
   - Student: `student1` / `student12345`

## 5) Environment Variables
Create `.env` or configure in host panel:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `ALLOWED_HOSTS` (comma-separated; default `*`)
- `EMAIL_BACKEND` (default SMTP backend)
- `EMAIL_HOST` (example: `smtp.gmail.com`)
- `EMAIL_PORT` (example: `587`)
- `EMAIL_USE_TLS` (`True` for Gmail/most SMTP)
- `EMAIL_HOST_USER` (SMTP username/email)
- `EMAIL_HOST_PASSWORD` (SMTP password/app password)
- `DEFAULT_FROM_EMAIL` (sender address) 

## 5.1) OTP via Email
- OTP is now sent to user email during:
  - Registration verification
  - Login verification
- Registration requires email.
- Login OTP requires an email linked to the account.
- Resend OTP is available on the OTP verification page.
- Security limits:
  - Maximum 3 OTP requests per 10 minutes (per user and OTP purpose)
  - 60-second cooldown between OTP requests

For Gmail SMTP:
1. Enable 2-step verification in Google account.
2. Create an App Password.
3. Set:
   - `EMAIL_HOST=smtp.gmail.com`
   - `EMAIL_PORT=587`
   - `EMAIL_USE_TLS=True`
   - `EMAIL_HOST_USER=<your gmail>`
   - `EMAIL_HOST_PASSWORD=<app password>`
   - `DEFAULT_FROM_EMAIL=<your gmail>`

## 6) Render Deployment (Step by Step)
1. Push project to GitHub.
2. Create a new Web Service in Render and connect the repository.
3. Create a PostgreSQL database in Render.
4. Add environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL=<Render PostgreSQL Internal URL>`
5. Build command:
   ```bash
   ./build.sh
   ```
6. Start command:
   ```bash
   gunicorn core.wsgi:application
   ```
7. Deploy and open service URL.

If using `render.yaml`, Render can auto-provision the web service and DB.

## 7) Security Practices Included
- Password hashing via Django auth
- CSRF middleware enabled
- ORM-based queries (SQL injection prevention)
- Role-based access checks on every module view
- Secret and database credentials from environment variables

## 8) Viva Questions & Answers
1. **Why custom user model?**  
   To store `role` inside auth identity and apply RBAC cleanly.

2. **How is RBAC implemented?**  
   Through a reusable `role_required` decorator and role-based redirects.

3. **How does app switch DB between dev/prod?**  
   SQLite by default; uses `DATABASE_URL` for PostgreSQL when provided.

4. **Why WhiteNoise on Render?**  
   To serve static files directly from Django app without separate static server.

5. **How are marks and grades calculated?**  
   `Mark` model computes percentage and grade using model properties.

6. **How is teacher access restricted?**  
   Teacher can only access subjects listed in `TeacherSubjectAssignment`.

7. **How is attendance tracked?**  
   Per student, subject, date with present/absent status and monthly reporting support.

8. **What is MVT in this project?**  
   Models in app `models.py`, views in `views.py`, templates in `templates/`.
"# SMART-MANAGEMENT" 
