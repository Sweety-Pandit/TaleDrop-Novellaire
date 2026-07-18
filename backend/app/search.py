from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import AuthorSearchResult, NovelListItem
from app.services import novel_service

search_router = APIRouter(prefix="/search", tags=["search"])


def search_novels(db: Session, query: str, skip: int = 0, limit: int = 20):
    return novel_service.list_published_novels(db, skip=skip, limit=limit, search=query)


def search_authors(db: Session, query: str, skip: int = 0, limit: int = 20) -> List[User]:
    like_pattern = f"%{query.strip()}%"
    return (
        db.query(User)
        .filter(
            User.role == UserRole.AUTHOR,
            User.is_active.is_(True),
            (User.username.ilike(like_pattern) | User.display_name.ilike(like_pattern)),
        )
        .order_by(User.display_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


@search_router.get("/novels", response_model=List[NovelListItem])
def search_novels_endpoint(
    q: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    return search_novels(db, q, skip=skip, limit=limit)


@search_router.get("/authors", response_model=List[AuthorSearchResult])
def search_authors_endpoint(
    q: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    return search_authors(db, q, skip=skip, limit=limit)
