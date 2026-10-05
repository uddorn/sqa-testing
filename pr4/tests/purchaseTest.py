import pytest

from app.service import BookNotFoundError, InsufficientStockError

ISBN = "123456789"


def buy(store, quantity, isbn=ISBN, customer_id=1):
    return store.place_order(customer_id, [{"isbn": isbn, "quantity": quantity}])


def test_purchase_succeeds_when_book_in_stock(store_with_book):
    order = buy(store_with_book, 2)

    assert order["items"] == [{"isbn": ISBN, "quantity": 2}]
    assert order["customer_id"] == 1
    assert order["status"] == "на обробці"


def test_purchase_fails_when_book_not_in_inventory(store_with_book):
    with pytest.raises(BookNotFoundError):
        buy(store_with_book, 1, isbn="000000000")


def test_purchase_fails_when_not_enough_copies(store_with_book):
    with pytest.raises(InsufficientStockError):
        buy(store_with_book, 6)


@pytest.mark.parametrize("quantity", [0, -1])
def test_purchase_fails_for_non_positive_quantity(store_with_book, quantity):
    with pytest.raises(ValueError):
        buy(store_with_book, quantity)


def test_purchase_fails_for_empty_order(store_with_book):
    with pytest.raises(ValueError):
        store_with_book.place_order(1, [])


def test_quantity_decreases_after_purchase(store_with_book):
    buy(store_with_book, 2)

    assert store_with_book.get_book(ISBN)["quantity"] == 3


def test_quantity_unchanged_after_failed_purchase(store_with_book):
    with pytest.raises(InsufficientStockError):
        buy(store_with_book, 6)

    assert store_with_book.get_book(ISBN)["quantity"] == 5


def test_can_buy_exactly_all_copies(store_with_book):
    buy(store_with_book, 5)

    assert store_with_book.get_book(ISBN)["quantity"] == 0


def test_cannot_buy_after_stock_is_sold_out(store_with_book):
    buy(store_with_book, 5)

    with pytest.raises(InsufficientStockError):
        buy(store_with_book, 1)


def test_same_book_twice_in_one_order_counts_together(store_with_book):
    items = [{"isbn": ISBN, "quantity": 3}, {"isbn": ISBN, "quantity": 3}]

    with pytest.raises(InsufficientStockError):
        store_with_book.place_order(1, items)

    assert store_with_book.get_book(ISBN)["quantity"] == 5