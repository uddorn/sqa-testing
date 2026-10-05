import pytest

from app.service import BookNotFoundError, DuplicateBookError

ISBN = "123456789"


def test_add_new_book(store):
    result = store.add_book(ISBN, "Python Programming", "John Doe")

    assert result
    assert store.get_book(ISBN)["title"] == "Python Programming"


def test_added_book_is_saved_with_all_fields(store):
    store.add_book(
        ISBN, "Python Programming", "John Doe",
        price=25.5, quantity=4, description="Intro book",
    )

    assert store.get_book(ISBN) == {
        "isbn": ISBN,
        "title": "Python Programming",
        "author": "John Doe",
        "price": 25.5,
        "quantity": 4,
        "description": "Intro book",
    }
    assert len(store.get_all_books()) == 1


def test_duplicate_isbn_is_rejected(store):
    store.add_book(ISBN, "Python Programming", "John Doe")

    with pytest.raises(ValueError):
        store.add_book(ISBN, "Another Book", "Jane Doe")


def test_duplicate_isbn_does_not_overwrite_existing_book(store):
    store.add_book(ISBN, "Python Programming", "John Doe")

    with pytest.raises(DuplicateBookError):
        store.add_book(ISBN, "Another Book", "Jane Doe")

    assert store.get_book(ISBN)["title"] == "Python Programming"
    assert len(store.get_all_books()) == 1


@pytest.mark.parametrize("fields", [{"price": -1}, {"quantity": -1}])
def test_add_book_with_negative_values_is_rejected(store, fields):
    with pytest.raises(ValueError):
        store.add_book(ISBN, "Python Programming", "John Doe", **fields)

    assert store.get_all_books() == []


def test_get_unknown_book_raises(store):
    with pytest.raises(BookNotFoundError):
        store.get_book("000000000")


def test_book_info_can_be_updated(store_with_book):
    updated = store_with_book.update_book(
        ISBN, price=15.5, quantity=10, description="New description"
    )

    assert updated["price"] == 15.5
    assert updated["quantity"] == 10
    assert updated["description"] == "New description"
    assert store_with_book.get_book(ISBN) == updated


def test_update_keeps_other_fields_unchanged(store_with_book):
    store_with_book.update_book(ISBN, price=99.0)

    book = store_with_book.get_book(ISBN)
    assert book["title"] == "Python Programming"
    assert book["author"] == "John Doe"
    assert book["quantity"] == 5


def test_isbn_cannot_be_changed(store_with_book):
    with pytest.raises(ValueError):
        store_with_book.update_book(ISBN, isbn="999999999")

    assert store_with_book.get_book(ISBN)["isbn"] == ISBN
    with pytest.raises(BookNotFoundError):
        store_with_book.get_book("999999999")


def test_title_cannot_be_updated(store_with_book):
    with pytest.raises(ValueError):
        store_with_book.update_book(ISBN, title="Hacked")

    assert store_with_book.get_book(ISBN)["title"] == "Python Programming"


def test_update_unknown_book_raises(store):
    with pytest.raises(BookNotFoundError):
        store.update_book("000000000", price=1.0)


def test_book_can_be_deleted_by_isbn(store_with_book):
    assert store_with_book.delete_book(ISBN) is True

    with pytest.raises(BookNotFoundError):
        store_with_book.get_book(ISBN)
    assert store_with_book.get_all_books() == []


def test_delete_nonexistent_book_does_not_raise(store):
    assert store.delete_book("000000000") is False


def test_delete_same_book_twice_does_not_raise(store_with_book):
    assert store_with_book.delete_book(ISBN) is True
    assert store_with_book.delete_book(ISBN) is False