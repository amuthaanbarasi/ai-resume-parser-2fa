
from fastapi import FastAPI, Depends
from app.routers.resume import router as resume_router
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.services.token_service import get_current_user

app = FastAPI(
    title="AI-Powered Resume Parser",
    description="Resume Parsing and Multi-Channel 2FA Onboarding Pipeline",
    version="1.0.0"
)


@app.get("/")
async def home():
    return {
        "message": "Welcome to AI-Powered Resume Parser",
        "status": "Application is running"
    }


@app.get("/dashboard/student")
async def student_dashboard(
    user_id: int = Depends(get_current_user)
):
    return {
        "message": "Welcome to Student Dashboard",
        "user_id": user_id,
        "features": [
            "View Profile",
            "Update Profile",
            "Upload Resume",
            "Parse Resume"
        ],
        "status": "Dashboard is active"
    }


app.include_router(resume_router)
app.include_router(auth_router)
app.include_router(profile_router)
