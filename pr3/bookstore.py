from dataclasses import dataclass
from typing import Optional


class BookstoreError(Exception):
    pass


class DuplicateISBNError(BookstoreError):
    pass


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    price: float
    stock: int


class Bookstore:
    def __init__(self) -> None:
        self._inventory: dict[str, Book] = {}

    def add_book(self, book: Book) -> None:
        if book.isbn in self._inventory:
            raise DuplicateISBNError(f"Книга з ISBN '{book.isbn}' вже існує в інвентарі.")
        self._inventory[book.isbn] = book

    def get_book(self, isbn: str) -> Optional[Book]:
        return self._inventory.get(isbn)