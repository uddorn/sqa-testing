import pytest

from app.service import Bookstore

ISBN = "123456789"


@pytest.fixture
def store():
    return Bookstore()


@pytest.fixture
def store_with_book(store):
    store.add_book(ISBN, "Python Programming", "John Doe", price=10.0, quantity=5)
    return store