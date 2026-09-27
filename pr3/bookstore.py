from collections import Counter
from dataclasses import dataclass
from typing import Optional


class BookstoreError(Exception):
    pass


class DuplicateISBNError(BookstoreError):
    pass


class InsufficientStockError(BookstoreError):
    pass


class OrderNotFoundError(BookstoreError):
    pass


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    price: float
    stock: int


@dataclass
class Order:
    order_id: int
    customer_name: str
    contact_info: str
    items: list[dict]
    total_amount: float
    status: str


@dataclass
class Review:
    review_id: int
    isbn: str
    author_name: str
    text: str
    rating: int
    status: str = "на модерації"


class Bookstore:
    VALID_STATUSES = frozenset({"в обробці", "відправлено", "доставлено"})

    def __init__(self) -> None:
        self._inventory: dict[str, Book] = {}
        self.purchase_history: list[dict] = []
        self._orders: dict[int, Order] = {}
        self._next_order_id: int = 1
        self._reviews: dict[int, Review] = {}
        self._next_review_id: int = 1

    @property
    def orders(self) -> dict[int, Order]:
        return self._orders

    def add_book(self, book: Book) -> None:
        if book.isbn in self._inventory:
            raise DuplicateISBNError(f"Книга з ISBN '{book.isbn}' вже існує в інвентарі.")
        self._inventory[book.isbn] = book

    def get_book(self, isbn: str) -> Optional[Book]:
        return self._inventory.get(isbn)

    def purchase_book(self, isbn: str, quantity: int) -> float:
        book = self.get_book(isbn)
        if not book:
            raise InsufficientStockError(f"Книгу з ISBN '{isbn}' не знайдено в інвентарі.")
        if book.stock < quantity:
            raise InsufficientStockError(
                f"Недостатньо книг на складі. В наявності: {book.stock}, запитано: {quantity}"
            )

        book.stock -= quantity
        total_cost = round(book.price * quantity, 2)

        self.purchase_history.append({
            "isbn": isbn,
            "title": book.title,
            "quantity": quantity,
            "price_per_item": book.price,
            "total_cost": total_cost,
        })
        return total_cost

    def create_order(self, customer_name: str, contact_info: str, items: list[dict]) -> Order:
        for item in items:
            book = self.get_book(item["isbn"])
            if not book or book.stock < item["quantity"]:
                raise InsufficientStockError(
                    f"Недостатньо примірників книги з ISBN '{item['isbn']}' на складі."
                )

        total_amount = 0.0
        for item in items:
            book = self.get_book(item["isbn"])
            book.stock -= item["quantity"]
            total_amount += book.price * item["quantity"]

        order = Order(
            order_id=self._next_order_id,
            customer_name=customer_name,
            contact_info=contact_info,
            items=items,
            total_amount=round(total_amount, 2),
            status="в обробці",
        )
        self._orders[self._next_order_id] = order
        self._next_order_id += 1
        return order

    def update_order_status(self, order_id: int, new_status: str) -> None:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Неприпустимий статус замовлення: {new_status}")
        order = self._orders.get(order_id)
        if not order:
            raise KeyError(f"Замовлення з ID {order_id} не знайдено.")
        order.status = new_status

    def get_order(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_recommendations(self, limit: int = 3) -> list[Book]:
        if limit <= 0:
            raise ValueError("Ліміт рекомендацій повинен бути більшим за нуль.")

        sales = Counter()
        for purchase in self.purchase_history:
            sales[purchase["isbn"]] += purchase["quantity"]

        recommended = [
            self._inventory[isbn]
            for isbn, _ in sales.most_common()
            if isbn in self._inventory
        ]

        for isbn, book in self._inventory.items():
            if len(recommended) >= limit:
                break
            if book not in recommended:
                recommended.append(book)

        return recommended[:limit]

    def add_review(self, isbn: str, author_name: str, text: str, rating: int) -> Optional[Review]:
        pass

    def moderate_review(self, review_id: int, approved: bool) -> None:
        pass

    def get_approved_reviews(self, isbn: str) -> list[Review]:
        return []

