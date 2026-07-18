import hashlib
import hmac

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def mock_razorpay_order_creation(monkeypatch):
    counter = {"n": 0}

    def fake_create_order(amount_rupees, currency, receipt):
        counter["n"] += 1
        return {
            "id": f"order_TEST{counter['n']}",
            "amount": int(amount_rupees * 100),
            "currency": currency,
            "status": "created",
        }

    import app.services.payment_service as payment_service_module

    monkeypatch.setattr(payment_service_module, "create_razorpay_order", fake_create_order)


def _make_author_with_premium_chapter(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    headers = auth_headers(client, author["_email"], author["_password"])
    novel = client.post(
        "/api/v1/novels", json={"title": "Priced", "is_premium": True, "price": 3.99}, headers=headers
    ).json()
    chapter = client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Ch1", "content": "x", "is_premium": True, "price": 1.99},
        headers=headers,
    ).json()
    client.post(f"/api/v1/chapters/{chapter['id']}/publish", headers=headers)
    client.post(f"/api/v1/novels/{novel['id']}/publish", headers=headers)
    return novel, chapter


def _sign(order_id: str, payment_id: str) -> str:
    payload = f"{order_id}|{payment_id}".encode()
    return hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), payload, hashlib.sha256).hexdigest()


def test_cannot_purchase_a_non_premium_chapter(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    novel = client.post("/api/v1/novels", json={"title": "Free"}, headers=author_headers).json()
    chapter = client.post(
        f"/api/v1/novels/{novel['id']}/chapters", json={"title": "Ch1", "content": "x"}, headers=author_headers
    ).json()

    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])
    response = client.post(f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers)
    assert response.status_code == 400


def test_bad_signature_is_rejected_and_marks_payment_failed(client, register_user, auth_headers):
    _, chapter = _make_author_with_premium_chapter(client, register_user, auth_headers)
    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    order = client.post(
        f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers
    ).json()

    response = client.post(
        "/api/v1/payments/confirm",
        json={
            "razorpay_order_id": order["razorpay_order_id"],
            "razorpay_payment_id": "pay_fake",
            "razorpay_signature": "not-a-real-signature",
        },
        headers=reader_headers,
    )
    assert response.status_code == 400


def test_valid_signature_unlocks_the_chapter(client, register_user, auth_headers):
    novel, chapter = _make_author_with_premium_chapter(client, register_user, auth_headers)
    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    order = client.post(
        f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers
    ).json()
    payment_id = "pay_real1"
    signature = _sign(order["razorpay_order_id"], payment_id)

    response = client.post(
        "/api/v1/payments/confirm",
        json={
            "razorpay_order_id": order["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        },
        headers=reader_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"

    unlocked = client.get(f"/api/v1/novels/{novel['slug']}/chapters/1", headers=reader_headers)
    assert unlocked.json()["locked"] is False


def test_cannot_repurchase_an_owned_chapter(client, register_user, auth_headers):
    _, chapter = _make_author_with_premium_chapter(client, register_user, auth_headers)
    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    order = client.post(
        f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers
    ).json()
    payment_id = "pay_real2"
    signature = _sign(order["razorpay_order_id"], payment_id)
    client.post(
        "/api/v1/payments/confirm",
        json={
            "razorpay_order_id": order["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        },
        headers=reader_headers,
    )

    response = client.post(f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers)
    assert response.status_code == 400


def test_purchase_history_lists_the_purchase(client, register_user, auth_headers):
    _, chapter = _make_author_with_premium_chapter(client, register_user, auth_headers)
    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    order = client.post(
        f"/api/v1/payments/chapters/{chapter['id']}/initiate", headers=reader_headers
    ).json()
    payment_id = "pay_real3"
    signature = _sign(order["razorpay_order_id"], payment_id)
    client.post(
        "/api/v1/payments/confirm",
        json={
            "razorpay_order_id": order["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        },
        headers=reader_headers,
    )

    history = client.get("/api/v1/payments/me", headers=reader_headers).json()
    assert len(history) == 1
    assert history[0]["status"] == "SUCCESS"
