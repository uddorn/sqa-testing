import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store

ISBN = "123456789"


@pytest.fixture
def client(store_with_book):
    app.dependency_overrides[get_store] = lambda: store_with_book
    yield TestClient(app)
    app.dependency_overrides.clear()


def order_body(quantity, isbn=ISBN):
    return {"customer_id": 1, "items": [{"isbn": isbn, "quantity": quantity}]}


def test_api_purchase_succeeds_and_decreases_stock(client):
    response = client.post("/orders/", json=order_body(2))

    assert response.status_code == 201
    assert response.json()["status"] == "на обробці"
    assert client.get(f"/books/{ISBN}").json()["quantity"] == 3


def test_api_purchase_fails_when_not_enough_copies(client):
    response = client.post("/orders/", json=order_body(6))

    assert response.status_code == 400
    assert client.get(f"/books/{ISBN}").json()["quantity"] == 5


def test_api_purchase_fails_for_unknown_book(client):
    response = client.post("/orders/", json=order_body(1, isbn="000000000"))

    assert response.status_code == 404