# HR Management System

A full-featured HR management platform for multi-company use, built with Flask, PostgreSQL, MongoDB, and Docker. Supports analytics, role-based access, PDF reporting, and secure authentication.

---

## Features
- Multi-company support: Isolated data per company
- Role-based access: Editor, Viewer, Admin, Developer, Master Key
- Employee management: Add, update, delete, view employees
- Professional info: Track salary, department, skills, performance
- Analytics: Salary, performance, department, experience, top earners, low performers, promotion candidates
- PDF reports: Download analytics and personnel reports
- Authentication: Secure login, signup, password reset, OTP verification
- Audit logging: Track changes and actions
- MongoDB integration: Personnel info, qualifications, city/state/gender analytics
- RESTful API endpoints
- Modern UI: Responsive templates

---

## Services Used
- **Flask**: Main backend web framework
- **PostgreSQL**: Relational database for core HR data
- **MongoDB**: NoSQL database for personnel analytics and flexible info
- **Docker**: Containerization for all services
- **Docker Compose**: Orchestration of multi-service setup
- **pdfkit**: PDF generation from HTML reports
- **Brevo (Sendinblue)**: Email service for notifications and OTP

---

## Project Structure
```
HR.mngr/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   └── utils/
├── db_init/
│   ├── accounts.sql
│   ├── company_schema.sql
│   ├── init_employee.sql
│   ├── professional_info.sql
│   └── reset_db.sql
├── backup/
│   ├── hrdb_schema_backup.sql
│   └── mongo_backup.md
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── Procfile
├── .env.example
└── README.md
```

---

## Environment Variables (.env)
Create a `.env` file in the root directory. Example:
```
# PostgreSQL
POSTGRES_USER=your_pg_user
POSTGRES_PASSWORD=your_pg_password
POSTGRES_DB=your_pg_db

# MongoDB
MONGO_USER=your_mongo_user
MONGO_PASSWORD=your_mongo_password
MONGO_DBNAME=your_mongo_db

# Flask
FLASK_ENV=production
SECRET_KEY=your_secret_key

# Brevo (Sendinblue)
BREVO_API_KEY=your_brevo_api_key
BREVO_EMAIL=your_email@example.com
```
- **BREVO_API_KEY**: Get from Brevo dashboard
- **BREVO_EMAIL**: Sender email for notifications/OTP

**BREVO_api_key_generation_steps**
🔹 Step 1: Log into Brevo

Go to https://app.brevo.com.

Sign in with your account (or create one if you don’t have it).

🔹 Step 2: Navigate to API Keys

Once logged in, click on your Profile icon (top-right corner).

Select SMTP & API from the dropdown menu.

This page contains settings for transactional email, SMTP, and API keys.

🔹 Step 3: Generate an API Key

On the SMTP & API page, locate the API Keys section.

Click Generate a new API key.

Enter a Name/Label for the key.

Example: My Django App, Currency Converter Project, or Production API.

This helps you identify which project is using which key.

Click Generate.

🔹 Step 4: Copy and Store the Key

Once generated, Brevo will display your API Key (a long alphanumeric string).

Important:

Copy the key immediately and store it securely (e.g., in .env file or secret manager).

You will not be able to see the full key again after closing the popup.

If lost, you’ll need to generate a new one.

---

## How to Run (Docker Compose)
1. Build and start all services:
   ```
   make up **only once at start**
   docker-compose up --build **after make up next time always use this**
   
   ```
2. Access the app at `http://localhost:5000`
3. PostgreSQL and MongoDB run in containers, preconfigured for the app
4. To reset the database, use SQL files in `db_init` or run the backup scripts

---

## Libraries Used
- Flask, SQLAlchemy, PyMongo, pdfkit, pytz, Brevo API, Jinja2, WTForms
- See `requirements.txt` for full list

---

## Adding Your Own .env
- Copy `.env.example` to `.env`
- Fill in your credentials and keys
- Restart Docker Compose to apply changes

---

## Contact & Support
For issues or feature requests, open an issue in this repo.
