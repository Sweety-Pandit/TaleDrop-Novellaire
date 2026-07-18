import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger("taledrop.mail")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# Special-purpose tokens (email verification / password reset)
def _create_special_token(subject: uuid.UUID, token_type: str, expires_minutes: int) -> str:
    """Create a short-lived JWT carrying a `type` claim used to scope its purpose."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": str(subject), "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_email_verification_token(user_id: uuid.UUID) -> str:
    return _create_special_token(
        user_id, "email_verification", settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
    )


def create_password_reset_token(user_id: uuid.UUID) -> str:
    return _create_special_token(
        user_id, "password_reset", settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )


def decode_special_token(token: str, expected_type: str) -> Optional[uuid.UUID]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

    if payload.get("type") != expected_type:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None

    try:
        return uuid.UUID(subject)
    except ValueError:
        return None


# Slug helper
def slugify(value: str) -> str:
    """Convert a string into a URL-safe slug."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value)
    return value.strip("-")

# Image upload 
def _local_dir_for(subdirectory: str) -> str:
    path = os.path.join(settings.UPLOAD_DIR, subdirectory)
    os.makedirs(path, exist_ok=True)
    return path


async def save_image_file(
    file: UploadFile, subdirectory: str, max_size_mb: Optional[int] = None
) -> str:
    if file.content_type not in settings.ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {file.content_type}",
        )

    contents = await file.read()
    limit_mb = max_size_mb or settings.AVATAR_MAX_SIZE_MB
    max_bytes = limit_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image must be smaller than {limit_mb}MB",
        )

    extension = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4()}{extension}"
    filepath = os.path.join(_local_dir_for(subdirectory), filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    return f"{settings.STATIC_URL_PREFIX}/{subdirectory}/{filename}"


def delete_local_static_file(url_path: Optional[str], subdirectory: str) -> None:
    if not url_path or not url_path.startswith(f"{settings.STATIC_URL_PREFIX}/{subdirectory}/"):
        return

    filename = url_path.rsplit("/", 1)[-1]
    filepath = os.path.join(_local_dir_for(subdirectory), filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


# Email sending
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    # Bounds worst-case hang time if the mail server is slow/unreachable —
    # without this, an unresponsive SMTP server can stall the background
    # task (and, since BackgroundTasks run before the ASGI response cycle
    # completes, the request that triggered it) far longer than any
    # reasonable UX allows.
    TIMEOUT=10,
)


async def _send_email(subject: str, recipient: str, body: str) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.html,
    )
    try:
        fm = FastMail(mail_config)
        await fm.send_message(message)
    except Exception as exc:  # noqa: BLE001 - intentionally broad for background email delivery
        logger.warning("Failed to send email to %s: %s", recipient, exc)


async def send_verification_email(email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    body = (
        f"<p>Welcome to {settings.PROJECT_NAME}!</p>"
        f"<p>Please verify your email by clicking the link below:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        f"<p>This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>"
    )
    await _send_email(f"Verify your {settings.PROJECT_NAME} account", email, body)


async def send_password_reset_email(email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    body = (
        f"<p>We received a request to reset your {settings.PROJECT_NAME} password.</p>"
        f"<p>Click the link below to choose a new password:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        f"<p>This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes. "
        f"If you did not request this, you can safely ignore this email.</p>"
    )
    await _send_email(f"Reset your {settings.PROJECT_NAME} password", email, body)
