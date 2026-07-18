import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_active_user,
    get_optional_current_user,
    require_roles,
)
from app.database import get_db
from app.models import ChapterStatus, NovelStatus, User, UserRole
from app.schemas import (
    ChangePasswordRequest,
    ChapterBookmarkOut,
    ChapterCreate,
    ChapterListItem,
    ChapterOut,
    ChapterUpdate,
    CommentCreate,
    AIAskRequest,
    AIAskResponse,
    AIReindexResponse,
    AISourceOut,
    AISummaryOut,
    CommentOut,
    CommentUpdate,
    ConfirmPaymentRequest,
    EmailVerificationConfirm,
    ForgotPasswordRequest,
    GenreCreate,
    GenreOut,
    LibraryItemOut,
    MessageResponse,
    NovelCreate,
    NovelListItem,
    NovelOut,
    NovelUpdate,
    PaymentOrderOut,
    PurchaseHistoryItemOut,
    ReadingHistoryOut,
    RecordReadingProgressRequest,
    RefreshTokenRequest,
    ResetPasswordConfirm,
    ReviewCreate,
    ReviewOut,
    ReviewUpdate,
    TagCreate,
    TagOut,
    Token,
    UserCreate,
    UserOut,
    UserPublicOut,
    UserUpdate,
)
from app.config import settings
from app.search import search_router
from app.services import (
    ai_service,
    auth_service,
    chapter_service,
    comment_service,
    novel_service,
    payment_service,
    user_service,
)
from app.utils import send_password_reset_email, send_verification_email

api_router = APIRouter()

# Auth routes
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user, verification_token = auth_service.register_user(db, payload)
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    return user


@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh", response_model=Token)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_payload = decode_token(payload.refresh_token)
    if token_payload is None or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    user = auth_service.get_user_by_id(db, uuid.UUID(token_payload["sub"]))
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    access_token = create_access_token(user.id, user.role)
    new_refresh_token = create_refresh_token(user.id)
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@auth_router.post("/logout", response_model=MessageResponse)
def logout():
    return MessageResponse(message="Logged out successfully")


@auth_router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: EmailVerificationConfirm, db: Session = Depends(get_db)):
    auth_service.confirm_email_verification(db, payload.token)
    return MessageResponse(message="Email verified successfully")


@auth_router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    reset_token = auth_service.create_password_reset_request(db, payload.email)
    if reset_token is not None:
        background_tasks.add_task(send_password_reset_email, payload.email, reset_token)
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent"
    )


@auth_router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordConfirm, db: Session = Depends(get_db)):
    auth_service.reset_password(db, payload.token, payload.new_password)
    return MessageResponse(message="Password reset successfully")


api_router.include_router(auth_router)


# User routes
user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@user_router.put("/me", response_model=UserOut)
def update_my_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return user_service.update_profile(db, current_user, payload)


@user_router.post("/me/avatar", response_model=UserOut)
async def upload_my_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return await user_service.update_avatar(db, current_user, file)


@user_router.put("/me/password", response_model=MessageResponse)
def change_my_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service.change_password(db, current_user, payload.current_password, payload.new_password)
    return MessageResponse(message="Password changed successfully")


@user_router.get("/me/reading-history", response_model=List[ReadingHistoryOut])
def get_my_reading_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    history = user_service.get_reading_history(db, current_user, skip=skip, limit=limit)
    return [ReadingHistoryOut.from_model(entry) for entry in history]


@user_router.post("/me/reading-history", response_model=ReadingHistoryOut)
def record_my_reading_progress(
    payload: RecordReadingProgressRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    entry = user_service.record_reading_progress(
        db, current_user, payload.novel_id, payload.chapter_id
    )
    return ReadingHistoryOut.from_model(entry)


@user_router.get("/me/library", response_model=List[LibraryItemOut])
def get_my_library(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    bookmarks = user_service.get_library(db, current_user, skip=skip, limit=limit)
    return [LibraryItemOut.from_model(bookmark) for bookmark in bookmarks]


@user_router.post(
    "/me/library/{novel_id}", response_model=LibraryItemOut, status_code=status.HTTP_201_CREATED
)
def add_novel_to_my_library(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    bookmark = user_service.add_to_library(db, current_user, novel_id)
    return LibraryItemOut.from_model(bookmark)


@user_router.delete("/me/library/{novel_id}", response_model=MessageResponse)
def remove_novel_from_my_library(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service.remove_from_library(db, current_user, novel_id)
    return MessageResponse(message="Novel removed from library")


@user_router.get("/me/bookmarks", response_model=List[ChapterBookmarkOut])
def get_my_chapter_bookmarks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    bookmarks = user_service.list_chapter_bookmarks(db, current_user, skip=skip, limit=limit)
    return [ChapterBookmarkOut.from_model(b) for b in bookmarks]


@user_router.post(
    "/me/bookmarks/{chapter_id}",
    response_model=ChapterBookmarkOut,
    status_code=status.HTTP_201_CREATED,
)
def bookmark_chapter(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    bookmark = user_service.bookmark_chapter(db, current_user, chapter_id)
    return ChapterBookmarkOut.from_model(bookmark)


@user_router.delete("/me/bookmarks/{chapter_id}", response_model=MessageResponse)
def remove_chapter_bookmark(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service.remove_chapter_bookmark(db, current_user, chapter_id)
    return MessageResponse(message="Bookmark removed")


@user_router.get("/{username}", response_model=UserPublicOut)
def get_public_profile(username: str, db: Session = Depends(get_db)):
    return user_service.get_user_by_username(db, username)


api_router.include_router(user_router)


# Novel routes
novel_router = APIRouter(prefix="/novels", tags=["novels"])


@novel_router.post(
    "",
    response_model=NovelOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.AUTHOR, UserRole.ADMIN))],
)
def create_novel(
    payload: NovelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.create_novel(db, current_user, payload)
    return NovelOut.from_model(novel)


@novel_router.get("", response_model=List[NovelListItem])
def browse_novels(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return novel_service.list_published_novels(
        db, skip=skip, limit=limit, search=search, genre_slug=genre, author_username=author
    )


@novel_router.get(
    "/me",
    response_model=List[NovelListItem],
    dependencies=[Depends(require_roles(UserRole.AUTHOR, UserRole.ADMIN))],
)
def get_my_novels(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return novel_service.list_my_novels(db, current_user, skip=skip, limit=limit)


@novel_router.get("/{slug}", response_model=NovelOut)
def get_novel(
    slug: str,
    viewer: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_slug_for_viewer(db, slug, viewer)
    return NovelOut.from_model(novel)


@novel_router.put("/{novel_id}", response_model=NovelOut)
def update_novel(
    novel_id: uuid.UUID,
    payload: NovelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = novel_service.update_novel(db, novel, current_user, payload)
    return NovelOut.from_model(updated)


@novel_router.delete("/{novel_id}", response_model=MessageResponse)
def delete_novel(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    novel_service.delete_novel(db, novel, current_user)
    return MessageResponse(message="Novel deleted successfully")


@novel_router.post("/{novel_id}/publish", response_model=NovelOut)
def publish_novel(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = novel_service.update_novel_status(db, novel, current_user, NovelStatus.PUBLISHED)
    return NovelOut.from_model(updated)


@novel_router.post("/{novel_id}/unpublish", response_model=NovelOut)
def unpublish_novel(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = novel_service.update_novel_status(db, novel, current_user, NovelStatus.DRAFT)
    return NovelOut.from_model(updated)


@novel_router.post("/{novel_id}/complete", response_model=NovelOut)
def complete_novel(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = novel_service.update_novel_status(db, novel, current_user, NovelStatus.COMPLETED)
    return NovelOut.from_model(updated)


@novel_router.post("/{novel_id}/cover", response_model=NovelOut)
async def upload_novel_cover(
    novel_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = await novel_service.update_cover_image(db, novel, current_user, file)
    return NovelOut.from_model(updated)


@novel_router.post("/{novel_id}/banner", response_model=NovelOut)
async def upload_novel_banner(
    novel_id: uuid.UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    updated = await novel_service.update_banner_image(db, novel, current_user, file)
    return NovelOut.from_model(updated)

# Review routes
@novel_router.get("/{novel_id}/reviews", response_model=List[ReviewOut])
def list_novel_reviews(
    novel_id: uuid.UUID, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """List reviews for a novel, most recent first. Public endpoint."""
    reviews = novel_service.list_reviews_for_novel(db, novel_id, skip=skip, limit=limit)
    return [ReviewOut.from_model(r) for r in reviews]


@novel_router.post("/{novel_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_or_update_my_review(
    novel_id: uuid.UUID,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    review = novel_service.create_or_update_review(db, novel_id, current_user, payload)
    return ReviewOut.from_model(review)


review_router = APIRouter(prefix="/reviews", tags=["reviews"])


@review_router.put("/{review_id}", response_model=ReviewOut)
def update_my_review(
    review_id: uuid.UUID,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    review = novel_service.get_review_by_id(db, review_id)
    updated = novel_service.update_review(db, review, current_user, payload)
    return ReviewOut.from_model(updated)


@review_router.delete("/{review_id}", response_model=MessageResponse)
def delete_my_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    review = novel_service.get_review_by_id(db, review_id)
    novel_service.delete_review(db, review, current_user)
    return MessageResponse(message="Review deleted successfully")


api_router.include_router(review_router)


# Comment routes
comment_novel_router = APIRouter(prefix="/novels", tags=["comments"])


@comment_novel_router.get("/{novel_id}/comments", response_model=List[CommentOut])
def list_novel_comments(
    novel_id: uuid.UUID,
    chapter_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    comments = comment_service.list_comments_for_novel(
        db, novel_id, chapter_id=chapter_id, skip=skip, limit=limit
    )
    return [CommentOut.from_model(c) for c in comments]


@comment_novel_router.post(
    "/{novel_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED
)
def create_comment(
    novel_id: uuid.UUID,
    payload: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    comment = comment_service.create_comment(db, novel, current_user, payload)
    return CommentOut.from_model(comment)


api_router.include_router(comment_novel_router)


comment_router = APIRouter(prefix="/comments", tags=["comments"])


@comment_router.put("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    comment = comment_service.get_comment_by_id(db, comment_id)
    updated = comment_service.update_comment(db, comment, current_user, payload)
    return CommentOut.from_model(updated)


@comment_router.delete("/{comment_id}", response_model=MessageResponse)
def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    comment = comment_service.get_comment_by_id(db, comment_id)
    comment_service.delete_comment(db, comment, current_user)
    return MessageResponse(message="Comment deleted successfully")


api_router.include_router(comment_router)


# Genre routes
genre_router = APIRouter(prefix="/genres", tags=["genres"])


@genre_router.get("", response_model=List[GenreOut])
def browse_genres(db: Session = Depends(get_db)):
    return novel_service.list_genres(db)


@genre_router.post(
    "",
    response_model=GenreOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_genre(payload: GenreCreate, db: Session = Depends(get_db)):
    return novel_service.create_genre(db, payload)


api_router.include_router(genre_router)


# Tag routes
tag_router = APIRouter(prefix="/tags", tags=["tags"])


@tag_router.get("", response_model=List[TagOut])
def browse_tags(db: Session = Depends(get_db)):
    return novel_service.list_tags(db)


@tag_router.post(
    "",
    response_model=TagOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag. Admin only."""
    return novel_service.create_tag(db, payload)


api_router.include_router(tag_router)


# Chapter routes
@novel_router.post(
    "/{novel_id}/chapters",
    response_model=ChapterListItem,
    status_code=status.HTTP_201_CREATED,
)
def create_chapter(
    novel_id: uuid.UUID,
    payload: ChapterCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    return chapter_service.create_chapter(db, novel, current_user, payload)


@novel_router.get("/{slug}/chapters", response_model=List[ChapterListItem])
def list_novel_chapters(
    slug: str,
    viewer: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_slug_for_viewer(db, slug, viewer)
    return chapter_service.list_chapters_for_novel(db, novel, viewer)


@novel_router.get("/{slug}/chapters/{chapter_number}", response_model=ChapterOut)
def read_chapter(
    slug: str,
    chapter_number: int,
    viewer: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_slug_for_viewer(db, slug, viewer)
    chapter = chapter_service.get_chapter_for_viewer(db, novel, chapter_number, viewer)
    locked = chapter_service.is_chapter_locked(db, novel, chapter, viewer)
    return ChapterOut.from_model(chapter, locked=locked)


api_router.include_router(novel_router)


chapter_router = APIRouter(prefix="/chapters", tags=["chapters"])

@chapter_router.put("/{chapter_id}", response_model=ChapterListItem)
def update_chapter(
    chapter_id: uuid.UUID,
    payload: ChapterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    chapter = chapter_service.get_chapter_by_id(db, chapter_id)
    novel = novel_service.get_novel_by_id(db, chapter.novel_id)
    return chapter_service.update_chapter(db, chapter, novel, current_user, payload)


@chapter_router.delete("/{chapter_id}", response_model=MessageResponse)
def delete_chapter(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a chapter. Owner or admin only."""
    chapter = chapter_service.get_chapter_by_id(db, chapter_id)
    novel = novel_service.get_novel_by_id(db, chapter.novel_id)
    chapter_service.delete_chapter(db, chapter, novel, current_user)
    return MessageResponse(message="Chapter deleted successfully")


@chapter_router.post("/{chapter_id}/publish", response_model=ChapterListItem)
def publish_chapter(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    chapter = chapter_service.get_chapter_by_id(db, chapter_id)
    novel = novel_service.get_novel_by_id(db, chapter.novel_id)
    return chapter_service.set_chapter_status(db, chapter, novel, current_user, ChapterStatus.PUBLISHED)


@chapter_router.post("/{chapter_id}/unpublish", response_model=ChapterListItem)
def unpublish_chapter(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    chapter = chapter_service.get_chapter_by_id(db, chapter_id)
    novel = novel_service.get_novel_by_id(db, chapter.novel_id)
    return chapter_service.set_chapter_status(db, chapter, novel, current_user, ChapterStatus.DRAFT)


api_router.include_router(chapter_router)


# Payment routes
payment_router = APIRouter(prefix="/payments", tags=["payments"])


def _to_order_response(payment, order: dict) -> PaymentOrderOut:
    return PaymentOrderOut(
        payment_id=payment.id,
        razorpay_order_id=order["id"],
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        amount=payment.amount,
        currency=payment.currency,
        novel_id=payment.novel_id,
        chapter_id=payment.chapter_id,
    )


@payment_router.post("/chapters/{chapter_id}/initiate", response_model=PaymentOrderOut)
def initiate_chapter_purchase(
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    payment, order = payment_service.initiate_chapter_purchase(db, current_user, chapter_id)
    return _to_order_response(payment, order)


@payment_router.post("/novels/{novel_id}/initiate", response_model=PaymentOrderOut)
def initiate_novel_purchase(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    payment, order = payment_service.initiate_novel_purchase(db, current_user, novel_id)
    return _to_order_response(payment, order)


@payment_router.post("/confirm", response_model=PurchaseHistoryItemOut)
def confirm_payment(
    payload: ConfirmPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    payment = payment_service.confirm_payment(
        db,
        current_user,
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature,
    )
    return PurchaseHistoryItemOut.from_model(payment)


@payment_router.get("/me", response_model=List[PurchaseHistoryItemOut])
def get_my_purchase_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List the currently authenticated user's purchase history, most recent first."""
    payments = payment_service.get_purchase_history(db, current_user, skip=skip, limit=limit)
    return [PurchaseHistoryItemOut.from_model(p) for p in payments]

api_router.include_router(payment_router)

# AI routes
ai_router = APIRouter(prefix="/novels", tags=["ai"])


@ai_router.get("/{novel_id}/ai/summary", response_model=AISummaryOut)
def get_novel_ai_summary(
    novel_id: uuid.UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    summary = ai_service.generate_novel_summary(db, novel, current_user)
    return AISummaryOut(novel_id=novel.id, summary=summary)


@ai_router.post("/{novel_id}/ai/reindex", response_model=AIReindexResponse)
def reindex_novel_for_ai(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    novel_service.assert_ownership(novel, current_user)
    chunks_indexed = ai_service.reindex_novel(db, novel)
    return AIReindexResponse(novel_id=novel.id, chunks_indexed=chunks_indexed)


@ai_router.post("/{novel_id}/ai/ask", response_model=AIAskResponse)
def ask_novel_question(
    novel_id: uuid.UUID,
    payload: AIAskRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    novel = novel_service.get_novel_by_id(db, novel_id)
    answer, sources = ai_service.answer_question_about_novel(
        db, novel, current_user, payload.question
    )
    return AIAskResponse(
        novel_id=novel.id,
        question=payload.question,
        answer=answer,
        sources=[AISourceOut(**s) for s in sources],
    )


api_router.include_router(ai_router)


user_ai_router = APIRouter(prefix="/users", tags=["ai"])


@user_ai_router.get("/me/recommendations", response_model=List[NovelListItem])
def get_my_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return ai_service.get_recommendations_for_user(db, current_user, limit=limit)


api_router.include_router(user_ai_router)

# Search routes
api_router.include_router(search_router)
