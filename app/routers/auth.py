
from app.schemas.auth import UserLoginRequest, UserLoginResponse
from app.services.auth_service import verify_password
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.schemas.auth import OTPVerifyRequest, OTPVerifyResponse
from app.services.otp_service import verify_otp

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.otp_challenge import OTPChallenge
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    OTPRequest,
    OTPResponse
)
from app.services.auth_service import hash_password
from app.services.otp_service import generate_otp, hash_otp, get_otp_expiry
from app.services.email_service import send_email_otp

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserRegisterResponse)
async def register_user(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password),
        is_verified=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserRegisterResponse(
        message="Registration successful. Please complete email OTP verification.",
        user_id=new_user.id,
        email=new_user.email
    )


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    otp_data: OTPRequest,
    db: AsyncSession = Depends(get_db)
):
    if otp_data.channel != "email":
        raise HTTPException(
            status_code=400,
            detail="Only email OTP is supported"
        )

    result = await db.execute(
        select(User).where(User.id == otp_data.user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User is already verified"
        )

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    challenge = OTPChallenge(
        user_id=user.id,
        channel="email",
        otp_hash=otp_hash,
        expires_at=get_otp_expiry()
    )

    db.add(challenge)
    await db.commit()

    try:
        send_email_otp(user.email, otp)

    except Exception:
        await db.delete(challenge)
        await db.commit()

        raise HTTPException(
            status_code=500,
            detail="Unable to send OTP email. Please try again."
        )

    return OTPResponse(
        message="OTP sent successfully to your registered email.",
        user_id=user.id,
        channel="email"
    )
@router.post("/verify-2fa", response_model=OTPVerifyResponse)
async def verify_user_otp(
    otp_data: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == otp_data.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User is already verified"
        )

    result = await db.execute(
        select(OTPChallenge)
        .where(
            OTPChallenge.user_id == user.id,
            OTPChallenge.channel == "email",
            OTPChallenge.is_verified == False
        )
        .order_by(OTPChallenge.created_at.desc())
    )
    challenge = result.scalars().first()

    if not challenge:
        raise HTTPException(
            status_code=400,
            detail="OTP challenge not found"
        )

    if datetime.now(timezone.utc) > challenge.expires_at:
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Request a new OTP."
        )

    if not verify_otp(otp_data.otp, challenge.otp_hash):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    challenge.is_verified = True
    user.is_verified = True

    access_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc).timestamp()
            + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    await db.commit()

    return OTPVerifyResponse(
        message="Email OTP verified successfully. Account activated.",
        user_id=user.id,
        is_verified=True,
        access_token=access_token,
        token_type="bearer"
    )
@router.post("/login", response_model=UserLoginResponse)
async def login(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first"
        )

    access_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }
