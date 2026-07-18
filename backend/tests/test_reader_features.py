def _publish_novel_with_chapter(client, headers, title="Novel"):
    novel = client.post("/api/v1/novels", json={"title": title}, headers=headers).json()
    chapter = client.post(
        f"/api/v1/novels/{novel['id']}/chapters", json={"title": "Ch1", "content": "x"}, headers=headers
    ).json()
    client.post(f"/api/v1/chapters/{chapter['id']}/publish", headers=headers)
    client.post(f"/api/v1/novels/{novel['id']}/publish", headers=headers)
    return novel, chapter


def test_add_and_remove_from_library(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    novel, _ = _publish_novel_with_chapter(client, author_headers)

    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    add = client.post(f"/api/v1/users/me/library/{novel['id']}", headers=reader_headers)
    assert add.status_code == 201

    duplicate = client.post(f"/api/v1/users/me/library/{novel['id']}", headers=reader_headers)
    assert duplicate.status_code == 400

    library = client.get("/api/v1/users/me/library", headers=reader_headers).json()
    assert len(library) == 1

    remove = client.delete(f"/api/v1/users/me/library/{novel['id']}", headers=reader_headers)
    assert remove.status_code == 200
    assert client.get("/api/v1/users/me/library", headers=reader_headers).json() == []


def test_review_upsert_recalculates_average_rating(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    novel, _ = _publish_novel_with_chapter(client, author_headers)

    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    client.post(f"/api/v1/novels/{novel['id']}/reviews", json={"rating": 3}, headers=reader_headers)
    fetched = client.get(f"/api/v1/novels/{novel['slug']}").json()
    assert fetched["average_rating"] == 3.0

    # Re-reviewing updates the existing review rather than creating a second one.
    client.post(f"/api/v1/novels/{novel['id']}/reviews", json={"rating": 5}, headers=reader_headers)
    reviews = client.get(f"/api/v1/novels/{novel['id']}/reviews").json()
    assert len(reviews) == 1
    fetched = client.get(f"/api/v1/novels/{novel['slug']}").json()
    assert fetched["average_rating"] == 5.0


def test_only_review_author_or_admin_can_delete_review(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    novel, _ = _publish_novel_with_chapter(client, author_headers)

    reviewer = register_user(client)
    reviewer_headers = auth_headers(client, reviewer["_email"], reviewer["_password"])
    review = client.post(
        f"/api/v1/novels/{novel['id']}/reviews", json={"rating": 4}, headers=reviewer_headers
    ).json()

    other_reader = register_user(client)
    other_headers = auth_headers(client, other_reader["_email"], other_reader["_password"])
    response = client.delete(f"/api/v1/reviews/{review['id']}", headers=other_headers)
    assert response.status_code == 403


def test_comments_can_be_filtered_by_chapter(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    novel, chapter = _publish_novel_with_chapter(client, author_headers)

    reader = register_user(client)
    reader_headers = auth_headers(client, reader["_email"], reader["_password"])

    client.post(
        f"/api/v1/novels/{novel['id']}/comments", json={"content": "Great novel!"}, headers=reader_headers
    )
    client.post(
        f"/api/v1/novels/{novel['id']}/comments",
        json={"content": "Great chapter!", "chapter_id": chapter["id"]},
        headers=reader_headers,
    )

    all_comments = client.get(f"/api/v1/novels/{novel['id']}/comments").json()
    assert len(all_comments) == 2

    chapter_comments = client.get(
        f"/api/v1/novels/{novel['id']}/comments", params={"chapter_id": chapter["id"]}
    ).json()
    assert len(chapter_comments) == 1
    assert chapter_comments[0]["content"] == "Great chapter!"


def test_search_novels_by_title(client, register_user, auth_headers):
    author = register_user(client, role="AUTHOR")
    author_headers = auth_headers(client, author["_email"], author["_password"])
    _publish_novel_with_chapter(client, author_headers, title="The Last Ember")
    _publish_novel_with_chapter(client, author_headers, title="Unrelated Story")

    response = client.get("/api/v1/search/novels", params={"q": "Ember"})
    assert response.status_code == 200
    titles = [n["title"] for n in response.json()]
    assert titles == ["The Last Ember"]
