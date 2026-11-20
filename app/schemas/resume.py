from pydantic import BaseModel, EmailStr
from typing import Optional


class ResumeParseResponse(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: list[str] = []
    experience: Optional[str] = None
    extracted_text: str