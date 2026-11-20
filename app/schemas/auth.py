from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class UserRegisterResponse(BaseModel):
    message: str
    user_id: int
    email: EmailStr
class OTPRequest(BaseModel):
    user_id: int
    channel: str = Field(pattern="^(email|whatsapp|totp)$")
class OTPResponse(BaseModel):
    message: str
    user_id: int
    channel: str
class OTPVerifyRequest(BaseModel):
    user_id: int
    otp: str = Field(min_length=6, max_length=6, pattern="^[0-9]{6}$")


class OTPVerifyResponse(BaseModel):
    message: str
    user_id: int
    is_verified: bool
    access_token: str
    token_type: str = "bearer"
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"