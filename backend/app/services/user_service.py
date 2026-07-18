import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import Bookmark, Chapter, Novel, ReadingHistory, User
from app.schemas import UserUpdate
from app.utils import delete_local_static_file, hash_password, save_image_file, verify_password


# Profile
def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_user_by_username(db: Session, username: str) -> User:
    user = db.query(User).filter(User.username == username.lower()).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_profile(db: Session, user: User, payload: UserUpdate) -> User:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
    if not verify_password(current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user

# Avatar upload
async def update_avatar(db: Session, user: User, file: UploadFile) -> User:
    """Validate, save, and attach a new avatar image to the user's profile."""
    new_avatar_url = await save_image_file(
        file, subdirectory="avatars", max_size_mb=settings.AVATAR_MAX_SIZE_MB
    )
    delete_local_static_file(user.avatar, subdirectory="avatars")
    user.avatar = new_avatar_url
    db.commit()
    db.refresh(user)
    return user

# Reading History
def get_reading_history(
    db: Session, user: User, skip: int = 0, limit: int = 20
) -> List[ReadingHistory]:
    return (
        db.query(ReadingHistory)
        .options(joinedload(ReadingHistory.novel), joinedload(ReadingHistory.chapter))
        .filter(ReadingHistory.user_id == user.id)
        .order_by(desc(ReadingHistory.last_read_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def record_reading_progress(
    db: Session, user: User, novel_id: uuid.UUID, chapter_id: uuid.UUID
) -> ReadingHistory:
    """Create or update the reading-history row for this user + chapter."""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    chapter = (
        db.query(Chapter)
        .filter(Chapter.id == chapter_id, Chapter.novel_id == novel_id)
        .first()
    )
    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found for this novel"
        )

    entry = (
        db.query(ReadingHistory)
        .filter(ReadingHistory.user_id == user.id, ReadingHistory.chapter_id == chapter_id)
        .first()
    )

    if entry is None:
        entry = ReadingHistory(
            user_id=user.id,
            novel_id=novel_id,
            chapter_id=chapter_id,
            last_read_at=datetime.now(timezone.utc),
        )
        db.add(entry)
    else:
        entry.last_read_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(entry)
    return entry


# Library (novel-level bookmarks)
def get_library(db: Session, user: User, skip: int = 0, limit: int = 20) -> List[Bookmark]:
    return (
        db.query(Bookmark)
        .options(joinedload(Bookmark.novel))
        .filter(Bookmark.user_id == user.id, Bookmark.chapter_id.is_(None))
        .order_by(desc(Bookmark.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def add_to_library(db: Session, user: User, novel_id: uuid.UUID) -> Bookmark:
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == user.id,
            Bookmark.novel_id == novel_id,
            Bookmark.chapter_id.is_(None),
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Novel is already in your library"
        )

    bookmark = Bookmark(user_id=user.id, novel_id=novel_id, chapter_id=None)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def remove_from_library(db: Session, user: User, novel_id: uuid.UUID) -> None:
    bookmark = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == user.id,
            Bookmark.novel_id == novel_id,
            Bookmark.chapter_id.is_(None),
        )
        .first()
    )
    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Novel is not in your library"
        )
    db.delete(bookmark)
    db.commit()


# Chapter-level bookmarks 
def list_chapter_bookmarks(db: Session, user: User, skip: int = 0, limit: int = 20) -> List[Bookmark]:
    return (
        db.query(Bookmark)
        .options(joinedload(Bookmark.novel), joinedload(Bookmark.chapter))
        .filter(Bookmark.user_id == user.id, Bookmark.chapter_id.isnot(None))
        .order_by(desc(Bookmark.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def bookmark_chapter(db: Session, user: User, chapter_id: uuid.UUID) -> Bookmark:
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    existing = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user.id, Bookmark.chapter_id == chapter_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Chapter is already bookmarked"
        )

    bookmark = Bookmark(user_id=user.id, novel_id=chapter.novel_id, chapter_id=chapter_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def remove_chapter_bookmark(db: Session, user: User, chapter_id: uuid.UUID) -> None:
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user.id, Bookmark.chapter_id == chapter_id)
        .first()
    )
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
