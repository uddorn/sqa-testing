import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store

ISBN = "123456789"

NEW_BOOK = {
    "isbn": "111111111",
    "title": "Clean Code",
    "author": "Robert Martin",
    "price": 12.5,
    "quantity": 3,
    "description": "A handbook",
}


@pytest.fixture
def client(store_with_book):
    app.dependency_overrides[get_store] = lambda: store_with_book
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_api_add_book_is_saved(client):
    response = client.post("/books/", json=NEW_BOOK)

    assert response.status_code == 201
    assert client.get("/books/111111111").json() == NEW_BOOK
    assert len(client.get("/books/").json()) == 2


def test_api_duplicate_isbn_is_rejected(client):
    duplicate = {**NEW_BOOK, "isbn": ISBN}

    response = client.post("/books/", json=duplicate)

    assert response.status_code == 409
    assert len(client.get("/books/").json()) == 1


def test_api_invalid_book_is_rejected(client):
    response = client.post("/books/", json={**NEW_BOOK, "price": -5})

    assert response.status_code == 422


def test_api_get_unknown_book_returns_404(client):
    assert client.get("/books/000000000").status_code == 404


def test_api_update_book(client):
    body = {"price": 20.0, "quantity": 7, "description": "Updated"}

    response = client.put(f"/books/{ISBN}", json=body)

    assert response.status_code == 200
    book = client.get(f"/books/{ISBN}").json()
    assert book["price"] == 20.0
    assert book["quantity"] == 7
    assert book["description"] == "Updated"
    assert book["title"] == "Python Programming"


def test_api_isbn_cannot_be_changed(client):
    response = client.put(f"/books/{ISBN}", json={"isbn": "999999999"})

    assert response.status_code == 422
    assert client.get(f"/books/{ISBN}").status_code == 200
    assert client.get("/books/999999999").status_code == 404


def test_api_update_unknown_book_returns_404(client):
    response = client.put("/books/000000000", json={"price": 5.0})

    assert response.status_code == 404


def test_api_delete_book(client):
    response = client.delete(f"/books/{ISBN}")

    assert response.status_code == 200
    assert client.get(f"/books/{ISBN}").status_code == 404


def test_api_delete_unknown_book_returns_404_not_server_error(client):
    response = client.delete("/books/000000000")

    assert response.status_code == 404