import uuid
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models import Genre, Novel, NovelGenre, NovelStatus, NovelTag, Review, Tag, User, UserRole
from app.schemas import GenreCreate, NovelCreate, NovelUpdate, ReviewCreate, ReviewUpdate, TagCreate
from app.utils import delete_local_static_file, save_image_file, slugify

_NOVEL_LOAD_OPTIONS = (
    joinedload(Novel.author),
    joinedload(Novel.genre_links).joinedload(NovelGenre.genre),
    joinedload(Novel.tag_links).joinedload(NovelTag.tag),
    joinedload(Novel.chapters),
)


# Internal helpers
def _generate_unique_slug(db: Session, title: str, exclude_novel_id: Optional[uuid.UUID] = None) -> str:
    base_slug = slugify(title) or "novel"
    slug = base_slug
    suffix = 1
    while True:
        query = db.query(Novel).filter(Novel.slug == slug)
        if exclude_novel_id is not None:
            query = query.filter(Novel.id != exclude_novel_id)
        if query.first() is None:
            return slug
        suffix += 1
        slug = f"{base_slug}-{suffix}"


def assert_ownership(novel: Novel, user: User) -> None:
    """Raise 403 unless the user owns this novel or is an admin. Public: reusable by other services."""
    if novel.author_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this novel",
        )


def _assert_ownership(novel: Novel, user: User) -> None:
    assert_ownership(novel, user)


def _validate_genre_ids(db: Session, genre_ids: List[uuid.UUID]) -> None:
    if not genre_ids:
        return
    found_ids = {g.id for g in db.query(Genre.id).filter(Genre.id.in_(genre_ids)).all()}
    missing = set(genre_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown genre id(s): {missing}"
        )


def _validate_tag_ids(db: Session, tag_ids: List[uuid.UUID]) -> None:
    if not tag_ids:
        return
    found_ids = {t.id for t in db.query(Tag.id).filter(Tag.id.in_(tag_ids)).all()}
    missing = set(tag_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown tag id(s): {missing}"
        )


def _set_novel_genres(db: Session, novel: Novel, genre_ids: List[uuid.UUID]) -> None:
    _validate_genre_ids(db, genre_ids)
    db.query(NovelGenre).filter(NovelGenre.novel_id == novel.id).delete()
    for genre_id in genre_ids:
        db.add(NovelGenre(novel_id=novel.id, genre_id=genre_id))


def _set_novel_tags(db: Session, novel: Novel, tag_ids: List[uuid.UUID]) -> None:
    _validate_tag_ids(db, tag_ids)
    db.query(NovelTag).filter(NovelTag.novel_id == novel.id).delete()
    for tag_id in tag_ids:
        db.add(NovelTag(novel_id=novel.id, tag_id=tag_id))


def _reload(db: Session, novel_id: uuid.UUID) -> Novel:
    return db.query(Novel).options(*_NOVEL_LOAD_OPTIONS).filter(Novel.id == novel_id).first()


# Fetching
def get_novel_by_id(db: Session, novel_id: uuid.UUID) -> Novel:
    """Plain fetch by id, no visibility rules applied. 404 if missing."""
    novel = _reload(db, novel_id)
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


def get_novel_by_slug_for_viewer(db: Session, slug: str, viewer: Optional[User]) -> Novel:
    """Fetch by slug, applying visibility rules for the given viewer (or None for anonymous)."""
    novel = (
        db.query(Novel).options(*_NOVEL_LOAD_OPTIONS).filter(Novel.slug == slug).first()
    )
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    is_owner_or_admin = viewer is not None and (
        viewer.id == novel.author_id or viewer.role == UserRole.ADMIN
    )
    if novel.status == NovelStatus.DRAFT and not is_owner_or_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    if novel.status != NovelStatus.DRAFT:
        novel.views += 1
        db.commit()
        db.refresh(novel)

    return novel


def list_published_novels(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    genre_slug: Optional[str] = None,
    author_username: Optional[str] = None,
) -> List[Novel]:
    query = (
        db.query(Novel)
        .options(*_NOVEL_LOAD_OPTIONS)
        .filter(Novel.status.in_([NovelStatus.PUBLISHED, NovelStatus.COMPLETED]))
    )

    if author_username:
        query = query.join(User, User.id == Novel.author_id).filter(
            User.username == author_username.lower()
        )

    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(Novel.title.ilike(like_pattern), Novel.description.ilike(like_pattern))
        )

    if genre_slug:
        query = (
            query.join(NovelGenre, NovelGenre.novel_id == Novel.id)
            .join(Genre, Genre.id == NovelGenre.genre_id)
            .filter(Genre.slug == genre_slug)
        )

    return query.order_by(Novel.updated_at.desc()).offset(skip).limit(limit).all()


def list_my_novels(db: Session, author: User, skip: int = 0, limit: int = 20) -> List[Novel]:
    return (
        db.query(Novel)
        .options(*_NOVEL_LOAD_OPTIONS)
        .filter(Novel.author_id == author.id)
        .order_by(Novel.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# Mutations
def create_novel(db: Session, author: User, payload: NovelCreate) -> Novel:
    slug = _generate_unique_slug(db, payload.title)

    novel = Novel(
        title=payload.title,
        slug=slug,
        description=payload.description,
        language=payload.language,
        is_premium=payload.is_premium,
        price=payload.price,
        status=NovelStatus.DRAFT,
        author_id=author.id,
    )
    db.add(novel)
    db.flush()  # assign novel.id before creating association rows

    _set_novel_genres(db, novel, payload.genre_ids)
    _set_novel_tags(db, novel, payload.tag_ids)

    db.commit()
    return _reload(db, novel.id)


def update_novel(db: Session, novel: Novel, current_user: User, payload: NovelUpdate) -> Novel:
    _assert_ownership(novel, current_user)

    update_data = payload.model_dump(exclude_unset=True, exclude={"genre_ids", "tag_ids"})

    if "title" in update_data and update_data["title"] != novel.title:
        novel.slug = _generate_unique_slug(db, update_data["title"], exclude_novel_id=novel.id)

    for field, value in update_data.items():
        setattr(novel, field, value)

    if payload.genre_ids is not None:
        _set_novel_genres(db, novel, payload.genre_ids)
    if payload.tag_ids is not None:
        _set_novel_tags(db, novel, payload.tag_ids)

    db.commit()
    return _reload(db, novel.id)


def delete_novel(db: Session, novel: Novel, current_user: User) -> None:
    _assert_ownership(novel, current_user)
    delete_local_static_file(novel.cover_image, subdirectory="covers")
    delete_local_static_file(novel.banner_image, subdirectory="banners")
    db.delete(novel)
    db.commit()


def update_novel_status(
    db: Session, novel: Novel, current_user: User, new_status: NovelStatus
) -> Novel:
    _assert_ownership(novel, current_user)

    if new_status == NovelStatus.PUBLISHED and not novel.chapters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add at least one chapter before publishing a novel",
        )

    novel.status = new_status
    db.commit()
    return _reload(db, novel.id)


async def update_cover_image(
    db: Session, novel: Novel, current_user: User, file: UploadFile
) -> Novel:
    _assert_ownership(novel, current_user)
    new_url = await save_image_file(file, subdirectory="covers")
    delete_local_static_file(novel.cover_image, subdirectory="covers")
    novel.cover_image = new_url
    db.commit()
    return _reload(db, novel.id)


async def update_banner_image(
    db: Session, novel: Novel, current_user: User, file: UploadFile
) -> Novel:
    _assert_ownership(novel, current_user)
    new_url = await save_image_file(file, subdirectory="banners")
    delete_local_static_file(novel.banner_image, subdirectory="banners")
    novel.banner_image = new_url
    db.commit()
    return _reload(db, novel.id)


# Genres
def list_genres(db: Session) -> List[Genre]:
    return db.query(Genre).order_by(Genre.name).all()


def create_genre(db: Session, payload: GenreCreate) -> Genre:
    slug = slugify(payload.name)
    if db.query(Genre).filter(Genre.slug == slug).first() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Genre already exists")
    genre = Genre(name=payload.name, slug=slug)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


# Tags
def list_tags(db: Session) -> List[Tag]:
    return db.query(Tag).order_by(Tag.name).all()


def create_tag(db: Session, payload: TagCreate) -> Tag:
    slug = slugify(payload.name)
    if db.query(Tag).filter(Tag.slug == slug).first() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    tag = Tag(name=payload.name, slug=slug)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# Reviews
def _recalculate_average_rating(db: Session, novel_id: uuid.UUID) -> None:
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        return
    ratings = [r[0] for r in db.query(Review.rating).filter(Review.novel_id == novel_id).all()]
    novel.average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
    db.commit()


def list_reviews_for_novel(db: Session, novel_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[Review]:
    return (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.novel_id == novel_id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_or_update_review(db: Session, novel_id: uuid.UUID, user: User, payload: ReviewCreate) -> Review:
    novel = get_novel_by_id(db, novel_id)

    existing = (
        db.query(Review).filter(Review.novel_id == novel.id, Review.user_id == user.id).first()
    )
    if existing is not None:
        existing.rating = payload.rating
        existing.content = payload.content
        review = existing
    else:
        review = Review(
            novel_id=novel.id, user_id=user.id, rating=payload.rating, content=payload.content
        )
        db.add(review)

    db.commit()
    db.refresh(review)
    _recalculate_average_rating(db, novel.id)
    db.refresh(review)
    return review


def update_review(db: Session, review: Review, current_user: User, payload: ReviewUpdate) -> Review:
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own review"
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    _recalculate_average_rating(db, review.novel_id)
    db.refresh(review)
    return review


def delete_review(db: Session, review: Review, current_user: User) -> None:
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own review"
        )
    novel_id = review.novel_id
    db.delete(review)
    db.commit()
    _recalculate_average_rating(db, novel_id)


def get_review_by_id(db: Session, review_id: uuid.UUID) -> Review:
    review = (
        db.query(Review).options(joinedload(Review.user)).filter(Review.id == review_id).first()
    )
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review
