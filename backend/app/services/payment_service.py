import uuid
from typing import List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import Chapter, Novel, Payment, PaymentStatus, User
from app.payment import create_razorpay_order, verify_payment_signature


def _assert_chapter_not_already_purchased(db: Session, user: User, chapter: Chapter) -> None:
    existing = (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == PaymentStatus.SUCCESS,
            (Payment.chapter_id == chapter.id) | (Payment.novel_id == chapter.novel_id),
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You already own this chapter"
        )


def _assert_novel_not_already_purchased(db: Session, user: User, novel: Novel) -> None:
    existing = (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == PaymentStatus.SUCCESS,
            Payment.novel_id == novel.id,
            Payment.chapter_id.is_(None),
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You already own this novel"
        )


def initiate_chapter_purchase(
    db: Session, user: User, chapter_id: uuid.UUID
) -> Tuple[Payment, dict]:
    """Create a PENDING payment + Razorpay order for a single premium chapter."""
    chapter = (
        db.query(Chapter).options(joinedload(Chapter.novel)).filter(Chapter.id == chapter_id).first()
    )
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    if not chapter.is_premium or chapter.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This chapter is not a paid chapter"
        )

    _assert_chapter_not_already_purchased(db, user, chapter)

    order = create_razorpay_order(chapter.price, "INR", receipt=f"chapter:{chapter.id}")

    payment = Payment(
        user_id=user.id,
        novel_id=chapter.novel_id,
        chapter_id=chapter.id,
        amount=chapter.price,
        currency="INR",
        razorpay_order_id=order["id"],
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment, order


def initiate_novel_purchase(db: Session, user: User, novel_id: uuid.UUID) -> Tuple[Payment, dict]:
    """Create a PENDING payment + Razorpay order for whole-novel premium access."""
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    if not novel.is_premium or novel.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This novel is not a paid novel"
        )

    _assert_novel_not_already_purchased(db, user, novel)

    order = create_razorpay_order(novel.price, "INR", receipt=f"novel:{novel.id}")

    payment = Payment(
        user_id=user.id,
        novel_id=novel.id,
        chapter_id=None,
        amount=novel.price,
        currency="INR",
        razorpay_order_id=order["id"],
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment, order


def confirm_payment(
    db: Session,
    user: User,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
) -> Payment:
    payment = (
        db.query(Payment)
        .filter(Payment.razorpay_order_id == razorpay_order_id, Payment.user_id == user.id)
        .first()
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment order not found")

    if payment.status == PaymentStatus.SUCCESS:
        return payment

    is_valid = verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = PaymentStatus.SUCCESS if is_valid else PaymentStatus.FAILED
    db.commit()
    db.refresh(payment)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature"
        )

    return payment


def get_purchase_history(db: Session, user: User, skip: int = 0, limit: int = 20) -> List[Payment]:
    return (
        db.query(Payment)
        .options(joinedload(Payment.novel), joinedload(Payment.chapter))
        .filter(Payment.user_id == user.id)
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
