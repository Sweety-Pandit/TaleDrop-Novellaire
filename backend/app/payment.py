import hashlib
import hmac
from typing import Optional

import razorpay
from fastapi import HTTPException, status

from app.config import settings

_client: Optional[razorpay.Client] = None


def get_razorpay_client() -> razorpay.Client:
    """Lazily construct a single shared Razorpay client instance."""
    global _client
    if _client is None:
        _client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    return _client


def rupees_to_paise(amount: float) -> int:
    """Razorpay amounts are in the smallest currency unit (paise for INR)."""
    return int(round(amount * 100))


def create_razorpay_order(amount_rupees: float, currency: str, receipt: str) -> dict:
    client = get_razorpay_client()
    try:
        return client.order.create(
            {
                "amount": rupees_to_paise(amount_rupees),
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1,
            }
        )
    except Exception as exc: 
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to create Razorpay order: {exc}",
        )


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify the signature sent by Razorpay to ensure the payment is legitimate."""
    payload = f"{order_id}|{payment_id}".encode("utf-8")
    secret = settings.RAZORPAY_KEY_SECRET.encode("utf-8")
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
