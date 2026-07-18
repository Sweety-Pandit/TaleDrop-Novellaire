import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.utils import (
    create_email_verification_token,
    create_password_reset_token,
    decode_special_token,
    hash_password,
    verify_password,
)


def register_user(db: Session, payload: UserCreate) -> tuple[User, str]:
    """Create a new user and return the user object along with an email verification token."""
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered"
        )

    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken"
        )

    user = User(
        username=payload.username,
        display_name=payload.display_name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role,
        is_verified=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    verification_token = create_email_verification_token(user.id)
    return user, verification_token


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Validate credentials and return the user, updating last_login on success."""
    user = db.query(User).filter(User.email == email).first()

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None or not verify_password(password, user.password):
        raise invalid_credentials

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def confirm_email_verification(db: Session, token: str) -> User:
    """Verify a user's email using a valid email_verification token."""
    user_id = decode_special_token(token, "email_verification")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def create_password_reset_request(db: Session, email: str) -> str | None:
    """Generate a password reset token for a user, if the email exists."""
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    return create_password_reset_token(user.id)


def reset_password(db: Session, token: str, new_password: str) -> User:
    """Reset a user's password using a valid password_reset token."""
    user_id = decode_special_token(token, "password_reset")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    """Fetch a user by id, raising 404 if not found. Used by the refresh-token flow."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
