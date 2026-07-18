import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import Chapter, Comment, Novel, User, UserRole
from app.schemas import CommentCreate, CommentUpdate


def get_comment_by_id(db: Session, comment_id: uuid.UUID) -> Comment:
    comment = (
        db.query(Comment)
        .options(joinedload(Comment.user))
        .filter(Comment.id == comment_id)
        .first()
    )
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


def list_comments_for_novel(
    db: Session,
    novel_id: uuid.UUID,
    chapter_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Comment]:
    query = (
        db.query(Comment).options(joinedload(Comment.user)).filter(Comment.novel_id == novel_id)
    )
    if chapter_id is not None:
        query = query.filter(Comment.chapter_id == chapter_id)
    return query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()


def create_comment(
    db: Session, novel: Novel, user: User, payload: CommentCreate
) -> Comment:
    if payload.chapter_id is not None:
        chapter = (
            db.query(Chapter)
            .filter(Chapter.id == payload.chapter_id, Chapter.novel_id == novel.id)
            .first()
        )
        if chapter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found for this novel"
            )

    comment = Comment(
        novel_id=novel.id,
        chapter_id=payload.chapter_id,
        user_id=user.id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(
    db: Session, comment: Comment, current_user: User, payload: CommentUpdate
) -> Comment:
    if comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comment"
        )
    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment, current_user: User) -> None:
    if comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comment"
        )
    db.delete(comment)
    db.commit()
