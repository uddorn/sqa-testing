import pytest

from app.service import OrderNotFoundError

ISBN = "123456789"


def place(store, customer_id=1, quantity=1):
    return store.place_order(customer_id, [{"isbn": ISBN, "quantity": quantity}])


def test_orders_get_unique_ids(store_with_book):
    ids = {place(store_with_book)["id"] for _ in range(3)}

    assert len(ids) == 3


def test_order_contains_all_required_details(store_with_book):
    order = place(store_with_book, customer_id=7, quantity=2)

    assert "id" in order
    assert order["customer_id"] == 7
    assert order["items"] == [{"isbn": ISBN, "quantity": 2}]
    assert order["status"] == "на обробці"


def test_created_order_can_be_fetched_by_id(store_with_book):
    order = place(store_with_book)

    assert store_with_book.get_order(order["id"]) == order


def test_get_unknown_order_raises(store):
    with pytest.raises(OrderNotFoundError):
        store.get_order(999)


def test_order_status_can_be_changed(store_with_book):
    order = place(store_with_book)

    store_with_book.update_order_status(order["id"], "відправлено")
    assert store_with_book.get_order(order["id"])["status"] == "відправлено"

    store_with_book.update_order_status(order["id"], "виконано")
    assert store_with_book.get_order(order["id"])["status"] == "виконано"


def test_invalid_status_is_rejected(store_with_book):
    order = place(store_with_book)

    with pytest.raises(ValueError):
        store_with_book.update_order_status(order["id"], "оплачено")

    assert store_with_book.get_order(order["id"])["status"] == "на обробці"


def test_update_status_of_unknown_order_raises(store):
    with pytest.raises(OrderNotFoundError):
        store.update_order_status(999, "відправлено")


def test_customer_sees_all_own_orders(store_with_book):
    first = place(store_with_book, customer_id=1)
    second = place(store_with_book, customer_id=1)
    other = place(store_with_book, customer_id=2)

    orders = store_with_book.get_customer_orders(1)

    assert [o["id"] for o in orders] == [first["id"], second["id"]]
    assert all(o["customer_id"] == 1 for o in orders)
    assert other["id"] not in [o["id"] for o in orders]


def test_customer_without_orders_gets_empty_list(store_with_book):
    place(store_with_book, customer_id=1)

    assert store_with_book.get_customer_orders(2) == []


def test_status_change_is_visible_in_customer_orders(store_with_book):
    order = place(store_with_book, customer_id=1)

    store_with_book.update_order_status(order["id"], "відправлено")

    assert store_with_book.get_customer_orders(1)[0]["status"] == "відправлено"