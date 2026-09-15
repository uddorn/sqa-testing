class Bookstore:
    def __init__(self):
        self._inventory = {}
        self._discounts = {}
        self._customers = {}

    def add_book(self, title: str, author: str, price: float, quantity: int) -> None:
        if not title:
            raise ValueError("Назва книги не може бути порожньою")
        if price < 0:
            raise ValueError("Ціна книги не може бути негативною")
        if quantity < 0:
            raise ValueError("Кількість книг не може бути негативною")

        if title in self._inventory:
            self._inventory[title]["quantity"] += quantity
        else:
            self._inventory[title] = {
                "title": title,
                "author": author,
                "price": price,
                "quantity": quantity,
            }

    def remove_book(self, title: str) -> None:
        if title in self._inventory:
            del self._inventory[title]
        self._discounts.pop(title, None)

    def search_book(self, title: str):
        if not title:
            return None
        return self._inventory.get(title)

    def purchase_book(self, title: str, quantity: int) -> float:
        if title not in self._inventory:
            raise ValueError(f"Книгу '{title}' не знайдено в інвентарі")

        if quantity <= 0:
            raise ValueError("Кількість для покупки має бути позитивним числом")

        book = self._inventory[title]

        if quantity > book["quantity"]:
            raise ValueError(
                f"Недостатньо книг на складі. В наявності: {book['quantity']}, "
                f"запитано: {quantity}"
            )

        discount_percent = self._discounts.get(title, 0)
        unit_price = book["price"] * (1 - discount_percent / 100)

        book["quantity"] -= quantity
        return unit_price * quantity

    def inventory_value(self) -> float:
        return sum(book["price"] * book["quantity"] for book in self._inventory.values())

    def apply_discount(self, title: str, percent: float) -> None:
        if title not in self._inventory:
            raise ValueError(f"Книгу '{title}' не знайдено в інвентарі")
        if not (0 <= percent <= 100):
            raise ValueError("Розмір знижки має бути від 0 до 100 відсотків")
        self._discounts[title] = percent

    def remove_discount(self, title: str) -> None:
        self._discounts.pop(title, None)

    def get_discount(self, title: str) -> float:
        return self._discounts.get(title, 0)

    def register_customer(self, name: str, email: str) -> None:
        if not name:
            raise ValueError("Ім'я клієнта не може бути порожнім")
        if not email:
            raise ValueError("Email клієнта не може бути порожнім")
        if email in self._customers:
            raise ValueError(f"Клієнт з email '{email}' вже зареєстрований")

        self._customers[email] = {
            "name": name,
            "email": email,
            "purchase_history": [],
        }

    def get_customer(self, email: str) -> dict:
        if not email:
            return None
        return self._customers.get(email)

    def purchase_book_for_customer(self, email: str, title: str, quantity: int) -> float:
        if email not in self._customers:
            raise ValueError(f"Клієнта з email '{email}' не знайдено")

        total = self.purchase_book(title, quantity)
        self._customers[email]["purchase_history"].append(
            {"title": title, "quantity": quantity, "total": total}
        )
        return total