"""
Authentication utilities - password hashing and JWT token management.
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "teamshadow-wedding-crm-secret-key-2024-very-secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    if '$' not in hashed:
        return False
    salt, pwd_hash = hashed.split('$', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == pwd_hash


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)})
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None