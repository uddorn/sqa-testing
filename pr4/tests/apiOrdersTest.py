import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store

ISBN = "123456789"


@pytest.fixture
def client(store_with_book):
    app.dependency_overrides[get_store] = lambda: store_with_book
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_order(client, customer_id=1, quantity=1):
    response = client.post(
        "/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"isbn": ISBN, "quantity": quantity}],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_api_orders_get_unique_ids(client):
    first = create_order(client)
    second = create_order(client)

    assert first["id"] != second["id"]


def test_api_order_contains_all_required_details(client):
    order = create_order(client, customer_id=7, quantity=2)

    assert order["customer_id"] == 7
    assert order["items"] == [{"isbn": ISBN, "quantity": 2}]
    assert order["status"] == "на обробці"


def test_api_get_order_by_id(client):
    order = create_order(client)

    response = client.get(f"/orders/{order['id']}")

    assert response.status_code == 200
    assert response.json() == order


def test_api_get_unknown_order_returns_404(client):
    assert client.get("/orders/999").status_code == 404


def test_api_order_status_can_be_changed(client):
    order = create_order(client)

    response = client.put(
        f"/orders/{order['id']}/status",
        json={"status": "відправлено"},
    )

    assert response.status_code == 200
    assert client.get(f"/orders/{order['id']}").json()["status"] == "відправлено"


def test_api_invalid_status_is_rejected(client):
    order = create_order(client)

    response = client.put(
        f"/orders/{order['id']}/status",
        json={"status": "оплачено"},
    )

    assert response.status_code == 422
    assert client.get(f"/orders/{order['id']}").json()["status"] == "на обробці"


def test_api_update_status_of_unknown_order_returns_404(client):
    response = client.put(
        "/orders/999/status",
        json={"status": "виконано"},
    )

    assert response.status_code == 404


def test_api_customer_sees_all_own_orders(client):
    first = create_order(client, customer_id=1)
    second = create_order(client, customer_id=1)
    create_order(client, customer_id=2)

    response = client.get("/customers/1/orders")

    assert response.status_code == 200
    assert [o["id"] for o in response.json()] == [first["id"], second["id"]]


def test_api_customer_without_orders_gets_empty_list(client):
    response = client.get("/customers/42/orders")

    assert response.status_code == 200
    assert response.json() == []