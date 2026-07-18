import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import ChapterStatus, NovelStatus, UserRole

# User schemas
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    display_name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.READER

    @field_validator("role")
    @classmethod
    def restrict_public_role(cls, value: UserRole) -> UserRole:
        if value == UserRole.ADMIN:
            raise ValueError("Cannot self-register with the ADMIN role")
        return value

    @field_validator("username")
    @classmethod
    def username_alnum(cls, value: str) -> str:
        if not value.replace("_", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, and underscores")
        return value.lower()


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: UserRole
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserUpdate(BaseModel):

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=2000)


class UserPublicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: UserRole
    created_at: datetime


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class EmailVerificationConfirm(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


# Reading History 
class ReadingHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    chapter_id: uuid.UUID
    last_read_at: datetime
    novel_title: str
    novel_slug: str
    novel_cover_image: Optional[str] = None
    chapter_title: str
    chapter_number: int

    @classmethod
    def from_model(cls, entry) -> "ReadingHistoryOut":
        """Build the flattened response from a ReadingHistory ORM row."""
        return cls(
            id=entry.id,
            novel_id=entry.novel_id,
            chapter_id=entry.chapter_id,
            last_read_at=entry.last_read_at,
            novel_title=entry.novel.title,
            novel_slug=entry.novel.slug,
            novel_cover_image=entry.novel.cover_image,
            chapter_title=entry.chapter.title,
            chapter_number=entry.chapter.chapter_number,
        )


class RecordReadingProgressRequest(BaseModel):
    novel_id: uuid.UUID
    chapter_id: uuid.UUID


# Library 
class LibraryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    novel_title: str
    novel_slug: str
    novel_cover_image: Optional[str] = None
    novel_status: str
    created_at: datetime

    @classmethod
    def from_model(cls, bookmark) -> "LibraryItemOut":
        """Build the flattened response from a novel-level Bookmark ORM row."""
        return cls(
            id=bookmark.id,
            novel_id=bookmark.novel_id,
            novel_title=bookmark.novel.title,
            novel_slug=bookmark.novel.slug,
            novel_cover_image=bookmark.novel.cover_image,
            novel_status=bookmark.novel.status.value,
            created_at=bookmark.created_at,
        )


# Genre
class GenreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class GenreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


class TagCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


# Novel schemas
class AuthorBrief(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str
    avatar: Optional[str] = None


class NovelCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    language: str = Field(default="en", max_length=30)
    is_premium: bool = False
    price: float = Field(default=0.0, ge=0)
    genre_ids: List[uuid.UUID] = Field(default_factory=list)
    tag_ids: List[uuid.UUID] = Field(default_factory=list)

    @field_validator("price")
    @classmethod
    def price_requires_premium(cls, value: float, info) -> float:
        if value > 0 and not info.data.get("is_premium", False):
            raise ValueError("price can only be set when is_premium is true")
        return value


class NovelUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    language: Optional[str] = Field(default=None, max_length=30)
    is_premium: Optional[bool] = None
    price: Optional[float] = Field(default=None, ge=0)
    genre_ids: Optional[List[uuid.UUID]] = None
    tag_ids: Optional[List[uuid.UUID]] = None


class NovelListItem(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    cover_image: Optional[str] = None
    language: str
    status: NovelStatus
    is_premium: bool
    average_rating: float
    views: int
    author: AuthorBrief
    updated_at: datetime


class NovelOut(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    banner_image: Optional[str] = None
    language: str
    status: NovelStatus
    is_premium: bool
    price: float
    views: int
    likes: int
    average_rating: float
    author: AuthorBrief
    genres: List[GenreOut]
    tags: List[TagOut]
    chapter_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, novel) -> "NovelOut":
        """Build the response, flattening genre links and chapter_count from a Novel row."""
        return cls(
            id=novel.id,
            title=novel.title,
            slug=novel.slug,
            description=novel.description,
            cover_image=novel.cover_image,
            banner_image=novel.banner_image,
            language=novel.language,
            status=novel.status,
            is_premium=novel.is_premium,
            price=novel.price,
            views=novel.views,
            likes=novel.likes,
            average_rating=novel.average_rating,
            author=AuthorBrief.model_validate(novel.author),
            genres=[GenreOut.model_validate(link.genre) for link in novel.genre_links],
            tags=[TagOut.model_validate(link.tag) for link in novel.tag_links],
            chapter_count=len(novel.chapters),
            created_at=novel.created_at,
            updated_at=novel.updated_at,
        )

# Chapter schemas
class ChapterCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, description="Chapter body as Markdown")
    chapter_number: Optional[int] = Field(
        default=None, ge=1, description="Auto-assigned as (max existing + 1) if omitted"
    )
    is_premium: bool = False
    price: float = Field(default=0.0, ge=0)

    @field_validator("price")
    @classmethod
    def price_requires_premium(cls, value: float, info) -> float:
        if value > 0 and not info.data.get("is_premium", False):
            raise ValueError("price can only be set when is_premium is true")
        return value


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, min_length=1)
    chapter_number: Optional[int] = Field(default=None, ge=1)
    is_premium: Optional[bool] = None
    price: Optional[float] = Field(default=None, ge=0)


class ChapterListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    chapter_number: int
    title: str
    is_premium: bool
    price: float
    views: int
    status: ChapterStatus
    created_at: datetime


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    chapter_number: int
    title: str
    content: Optional[str] = None
    is_premium: bool
    price: float
    views: int
    status: ChapterStatus
    locked: bool = False
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, chapter, locked: bool) -> "ChapterOut":
        return cls(
            id=chapter.id,
            novel_id=chapter.novel_id,
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            content=None if locked else chapter.content,
            is_premium=chapter.is_premium,
            price=chapter.price,
            views=chapter.views,
            status=chapter.status,
            locked=locked,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at,
        )

# Review schemas
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = Field(default=None, max_length=5000)


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    content: Optional[str] = Field(default=None, max_length=5000)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    user: UserPublicOut
    rating: int
    content: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, review) -> "ReviewOut":
        return cls(
            id=review.id,
            novel_id=review.novel_id,
            user=UserPublicOut.model_validate(review.user),
            rating=review.rating,
            content=review.content,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


# Comment schemas
class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=3000)
    chapter_id: Optional[uuid.UUID] = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=3000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    user: UserPublicOut
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, comment) -> "CommentOut":
        return cls(
            id=comment.id,
            novel_id=comment.novel_id,
            chapter_id=comment.chapter_id,
            user=UserPublicOut.model_validate(comment.user),
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )


class ChapterBookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: uuid.UUID
    novel_title: str
    novel_slug: str
    chapter_id: uuid.UUID
    chapter_title: str
    chapter_number: int
    created_at: datetime

    @classmethod
    def from_model(cls, bookmark) -> "ChapterBookmarkOut":
        return cls(
            id=bookmark.id,
            novel_id=bookmark.novel_id,
            novel_title=bookmark.novel.title,
            novel_slug=bookmark.novel.slug,
            chapter_id=bookmark.chapter_id,
            chapter_title=bookmark.chapter.title,
            chapter_number=bookmark.chapter.chapter_number,
            created_at=bookmark.created_at,
        )


# Search schemas
class AuthorSearchResult(UserPublicOut):

    pass

# Payment schemas
class PaymentOrderOut(BaseModel):

    payment_id: uuid.UUID
    razorpay_order_id: str
    razorpay_key_id: str
    amount: float
    currency: str
    novel_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None


class ConfirmPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PurchaseHistoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    novel_id: Optional[uuid.UUID] = None
    novel_title: str
    novel_slug: Optional[str] = None
    chapter_id: Optional[uuid.UUID] = None
    chapter_title: Optional[str] = None
    amount: float
    currency: str
    status: str
    created_at: datetime

    @classmethod
    def from_model(cls, payment) -> "PurchaseHistoryItemOut":
        return cls(
            id=payment.id,
            novel_id=payment.novel_id,
            novel_title=payment.novel.title if payment.novel else "",
            novel_slug=payment.novel.slug if payment.novel else None,
            chapter_id=payment.chapter_id,
            chapter_title=payment.chapter.title if payment.chapter else None,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            created_at=payment.created_at,
        )

# AI schemas
class AISummaryOut(BaseModel):
    novel_id: uuid.UUID
    summary: str


class AIAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AISourceOut(BaseModel):
    chapter_id: uuid.UUID
    chapter_number: int
    chapter_title: str
    snippet: str


class AIAskResponse(BaseModel):
    novel_id: uuid.UUID
    question: str
    answer: str
    sources: List[AISourceOut]


class AIReindexResponse(BaseModel):
    novel_id: uuid.UUID
    chunks_indexed: int
