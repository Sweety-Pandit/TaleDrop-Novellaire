def _make_author(client, register_user, auth_headers):
    user = register_user(client, role="AUTHOR")
    headers = auth_headers(client, user["_email"], user["_password"])
    return user, headers


def test_reader_cannot_create_novel(client, register_user, auth_headers):
    user = register_user(client)  # default role READER
    headers = auth_headers(client, user["_email"], user["_password"])
    response = client.post("/api/v1/novels", json={"title": "Should Fail"}, headers=headers)
    assert response.status_code == 403


def test_author_can_create_and_fetch_own_draft_novel(client, register_user, auth_headers):
    _, headers = _make_author(client, register_user, auth_headers)
    response = client.post("/api/v1/novels", json={"title": "The Last Ember"}, headers=headers)
    assert response.status_code == 201
    novel = response.json()
    assert novel["status"] == "DRAFT"
    assert novel["slug"] == "the-last-ember"


def test_duplicate_titles_get_unique_slugs(client, register_user, auth_headers):
    _, headers = _make_author(client, register_user, auth_headers)
    first = client.post("/api/v1/novels", json={"title": "Twins"}, headers=headers).json()
    second = client.post("/api/v1/novels", json={"title": "Twins"}, headers=headers).json()
    assert first["slug"] != second["slug"]


def test_non_owner_cannot_edit_novel(client, register_user, auth_headers):
    _, owner_headers = _make_author(client, register_user, auth_headers)
    _, other_headers = _make_author(client, register_user, auth_headers)
    novel = client.post("/api/v1/novels", json={"title": "Owned"}, headers=owner_headers).json()

    response = client.put(
        f"/api/v1/novels/{novel['id']}", json={"title": "Hijacked"}, headers=other_headers
    )
    assert response.status_code == 403


def test_publish_requires_at_least_one_chapter(client, register_user, auth_headers):
    _, headers = _make_author(client, register_user, auth_headers)
    novel = client.post("/api/v1/novels", json={"title": "Empty Novel"}, headers=headers).json()

    response = client.post(f"/api/v1/novels/{novel['id']}/publish", headers=headers)
    assert response.status_code == 400

    client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Ch1", "content": "Hello."},
        headers=headers,
    )
    response = client.post(f"/api/v1/novels/{novel['id']}/publish", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "PUBLISHED"


def test_chapter_numbers_auto_increment_and_reject_collisions(client, register_user, auth_headers):
    _, headers = _make_author(client, register_user, auth_headers)
    novel = client.post("/api/v1/novels", json={"title": "Serial"}, headers=headers).json()

    ch1 = client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Ch1", "content": "x"},
        headers=headers,
    ).json()
    ch2 = client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Ch2", "content": "x"},
        headers=headers,
    ).json()
    assert ch1["chapter_number"] == 1
    assert ch2["chapter_number"] == 2

    collision = client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Dup", "content": "x", "chapter_number": 1},
        headers=headers,
    )
    assert collision.status_code == 400


def test_draft_novel_is_hidden_from_public(client, register_user, auth_headers):
    _, headers = _make_author(client, register_user, auth_headers)
    novel = client.post("/api/v1/novels", json={"title": "Secret Draft"}, headers=headers).json()

    response = client.get(f"/api/v1/novels/{novel['slug']}")
    assert response.status_code == 404


def test_premium_chapter_locks_until_purchased(client, register_user, auth_headers, db_session):
    import uuid as uuid_module
    from app.models import Payment, PaymentStatus

    _, author_headers = _make_author(client, register_user, auth_headers)
    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    novel = client.post(
        "/api/v1/novels", json={"title": "Paywalled", "is_premium": True, "price": 2.99}, headers=author_headers
    ).json()
    chapter = client.post(
        f"/api/v1/novels/{novel['id']}/chapters",
        json={"title": "Locked", "content": "Secret content.", "is_premium": True, "price": 1.99},
        headers=author_headers,
    ).json()
    client.post(f"/api/v1/chapters/{chapter['id']}/publish", headers=author_headers)
    client.post(f"/api/v1/novels/{novel['id']}/publish", headers=author_headers)

    # Locked before purchase
    response = client.get(f"/api/v1/novels/{novel['slug']}/chapters/1", headers=reader_headers)
    assert response.status_code == 200
    assert response.json()["locked"] is True
    assert response.json()["content"] is None

    # Simulate a successful purchase directly (Razorpay flow is covered in test_payments.py)
    reader_id = client.get("/api/v1/users/me", headers=reader_headers).json()["id"]
    db_session.add(
        Payment(
            user_id=uuid_module.UUID(reader_id),
            novel_id=uuid_module.UUID(novel["id"]),
            chapter_id=uuid_module.UUID(chapter["id"]),
            amount=1.99,
            status=PaymentStatus.SUCCESS,
        )
    )
    db_session.commit()

    # Unlocked after purchase
    response = client.get(f"/api/v1/novels/{novel['slug']}/chapters/1", headers=reader_headers)
    assert response.json()["locked"] is False
    assert response.json()["content"] == "Secret content."
