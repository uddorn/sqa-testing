STATUSES = ("на обробці", "відправлено", "виконано")
DEFAULT_STATUS = STATUSES[0]

UPDATABLE_FIELDS = {"price", "quantity", "description"}


class DuplicateBookError(ValueError):
    pass


class InsufficientStockError(ValueError):
    pass


class BookNotFoundError(LookupError):
    pass


class OrderNotFoundError(LookupError):
    pass


class Bookstore:
    def __init__(self):
        self._books: dict[str, dict] = {}
        self._orders: dict[int, dict] = {}
        self._next_order_id = 1

    def add_book(self, isbn, title, author, price=0.0, quantity=0, description=""):
        if isbn in self._books:
            raise DuplicateBookError(f"Книга з ISBN {isbn} вже існує")
        if price < 0 or quantity < 0:
            raise ValueError("Ціна та кількість не можуть бути від'ємними")

        book = {
            "isbn": isbn,
            "title": title,
            "author": author,
            "price": price,
            "quantity": quantity,
            "description": description,
        }

        self._books[isbn] = book
        return dict(book)

    def get_book(self, isbn):
        if isbn not in self._books:
            raise BookNotFoundError(f"Книгу з ISBN {isbn} не знайдено")
        return dict(self._books[isbn])

    def get_all_books(self):
        return [dict(b) for b in self._books.values()]

    def update_book(self, isbn, /, **fields):
        if isbn not in self._books:
            raise BookNotFoundError(f"Книгу з ISBN {isbn} не знайдено")
        if "isbn" in fields:
            raise ValueError("ISBN змінювати не можна")

        unknown = set(fields) - UPDATABLE_FIELDS
        if unknown:
            raise ValueError(f"Ці поля змінювати не можна: {sorted(unknown)}")

        if fields.get("price", 0) < 0 or fields.get("quantity", 0) < 0:
            raise ValueError("Ціна та кількість не можуть бути від'ємними")

        self._books[isbn].update(fields)
        return dict(self._books[isbn])

    def delete_book(self, isbn):
        """Повертає True, якщо книгу видалено, і False, якщо її не було."""
        return self._books.pop(isbn, None) is not None

    def place_order(self, customer_id, items):
        if not items:
            raise ValueError("Замовлення не може бути порожнім")

        needed: dict[str, int] = {}

        for item in items:
            isbn = item["isbn"]
            qty = item["quantity"]
            if qty <= 0:
                raise ValueError("Кількість у замовленні має бути більшою за 0")
            needed[isbn] = needed.get(isbn, 0) + qty

        # Спочатку перевіряємо все, і лише потім списуємо зі складу
        for isbn, qty in needed.items():
            book = self._books.get(isbn)

            if book is None:
                raise BookNotFoundError(f"Книгу з ISBN {isbn} не знайдено")

            if book["quantity"] < qty:
                raise InsufficientStockError(
                    f"Недостатньо примірників {isbn}: є {book['quantity']}, потрібно {qty}"
                )

        for isbn, qty in needed.items():
            self._books[isbn]["quantity"] -= qty

        order_id = self._next_order_id
        self._next_order_id += 1

        order = {
            "id": order_id,
            "customer_id": customer_id,
            "items": [
                {"isbn": i["isbn"], "quantity": i["quantity"]}
                for i in items
            ],
            "status": DEFAULT_STATUS,
        }

        self._orders[order_id] = order
        return dict(order)

    def get_order(self, order_id):
        if order_id not in self._orders:
            raise OrderNotFoundError(f"Замовлення {order_id} не знайдено")
        return dict(self._orders[order_id])

    def update_order_status(self, order_id, status):
        if order_id not in self._orders:
            raise OrderNotFoundError(f"Замовлення {order_id} не знайдено")

        if status not in STATUSES:
            raise ValueError(f"Невідомий статус: {status}")

        self._orders[order_id]["status"] = status
        return dict(self._orders[order_id])

    def get_customer_orders(self, customer_id):
        return [
            dict(o)
            for o in self._orders.values()
            if o["customer_id"] == customer_id
        ]