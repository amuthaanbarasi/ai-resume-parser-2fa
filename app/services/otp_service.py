import secrets
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

otp_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    return otp_context.hash(otp)


def verify_otp(otp: str, otp_hash: str) -> bool:
    return otp_context.verify(otp, otp_hash)


def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=5)