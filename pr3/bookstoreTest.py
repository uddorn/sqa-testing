import unittest
from bookstore import (
    Book,
    Bookstore,
    DuplicateISBNError,
    InsufficientStockError,
    Order,
    Review,
)

class TestBookstoreInventory(unittest.TestCase):
    def setUp(self):
        self.store = Bookstore()
        self.book1 = Book(
            title="1984",
            author="George Orwell",
            isbn="12345",
            price=300.0,
            stock=5
        )

    def test_add_new_book_success(self):
        self.store.add_book(self.book1)
        retrieved_book = self.store.get_book("12345")
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.title, "1984")
        self.assertEqual(retrieved_book.stock, 5)

    def test_add_duplicate_isbn_raises_error(self):
        self.store.add_book(self.book1)
        duplicate_book = Book(
            title="Animal Farm",
            author="George Orwell",
            isbn="12345",
            price=250.0,
            stock=3
        )
        with self.assertRaises(DuplicateISBNError):
            self.store.add_book(duplicate_book)

    def test_purchase_book_updates_stock_and_logs(self):
        self.store.add_book(self.book1)
        total_cost = self.store.purchase_book("12345", quantity=2)

        self.assertEqual(self.store.get_book("12345").stock, 3)
        self.assertEqual(total_cost, 600.0)
        self.assertEqual(len(self.store.purchase_history), 1)
        self.assertEqual(self.store.purchase_history[0]["isbn"], "12345")
        self.assertEqual(self.store.purchase_history[0]["quantity"], 2)

    def test_purchase_insufficient_stock_raises_error(self):
        self.store.add_book(self.book1)
        with self.assertRaises(InsufficientStockError):
            self.store.purchase_book("12345", quantity=10)

    def test_create_order_for_customer_success(self):
        self.store.add_book(self.book1)
        order = self.store.create_order(
            customer_name="Іван Франко",
            contact_info="franko@example.com",
            items=[{"isbn": "12345", "quantity": 2}],
        )

        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, "Іван Франко")
        self.assertEqual(order.total_amount, 600.0)
        self.assertEqual(order.status, "в обробці")
        self.assertEqual(self.store.get_book("12345").stock, 3)

    def test_update_order_status_success_and_invalid_status_raises(self):
        self.store.add_book(self.book1)
        order = self.store.create_order(
            customer_name="Леся Українка",
            contact_info="+380501234567",
            items=[{"isbn": "12345", "quantity": 1}],
        )

        self.store.update_order_status(order.order_id, "відправлено")
        updated_order = self.store.get_order(order.order_id)
        self.assertEqual(updated_order.status, "відправлено")

        with self.assertRaises(ValueError):
            self.store.update_order_status(order.order_id, "невідомий_статус")

    def test_get_recommendations_by_popularity_success(self):
        book2 = Book(
            title="Колгосп тварин",
            author="Дж. Орвелл",
            isbn="54321",
            price=200.0,
            stock=10
        )
        self.store.add_book(self.book1)
        self.store.add_book(book2)

        self.store.purchase_book("12345", quantity=1)
        self.store.purchase_book("54321", quantity=3)

        recommendations = self.store.get_recommendations(limit=2)
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0].isbn, "54321")
        self.assertEqual(recommendations[1].isbn, "12345")

    def test_get_recommendations_invalid_limit_raises(self):
        with self.assertRaises(ValueError):
            self.store.get_recommendations(limit=0)
        with self.assertRaises(ValueError):
            self.store.get_recommendations(limit=-5)

    def test_add_review_pending_by_default(self):
        self.store.add_book(self.book1)
        review = self.store.add_review(
            "12345",
            "Олена",
            "Чудова антиутопія!",
            5
        )
        self.assertIsNotNone(review)
        self.assertEqual(review.status, "на модерації")
        self.assertEqual(len(self.store.get_approved_reviews("12345")), 0)

    def test_moderate_review_and_get_approved_reviews(self):
        self.store.add_book(self.book1)
        review1 = self.store.add_review(
            "12345",
            "Олена",
            "Чудово!",
            5
        )
        review2 = self.store.add_review(
            "12345",
            "Тарас",
            "Спам",
            1
        )

        self.store.moderate_review(review1.review_id, approved=True)
        self.store.moderate_review(review2.review_id, approved=False)

        approved_list = self.store.get_approved_reviews("12345")
        self.assertEqual(len(approved_list), 1)
        self.assertEqual(approved_list[0].author_name, "Олена")
        self.assertEqual(approved_list[0].status, "схвалено")


if __name__ == "__main__":
    unittest.main()