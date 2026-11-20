# AI-Powered Resume Parser & Email OTP Authentication

## Project Overview
A Python FastAPI-based application that automatically extracts candidate information from PDF and DOCX resumes and provides secure user onboarding through email OTP verification.

## Key Features
- PDF and DOCX resume parsing
- Automatic extraction of name, email, phone, skills, and experience
- User registration and login
- Secure password hashing using Argon2
- Email OTP verification
- JWT-based authentication
- Profile management and protected dashboard

## Technologies Used
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Argon2
- Gmail SMTP

## Run Locally

```bash
git clone https://github.com/amuthaanbarasi/ai-resume-parser-2fa.git
cd ai-resume-parser-2fa
python -m venv venv
```

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure the required environment variables in `.env`, then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API Documentation: http://127.0.0.1:8000/docs

## Author
**Anbarasi Kathirvel**