import unittest
from bookstore import Book, Bookstore, DuplicateISBNError


class TestBookstoreInventory(unittest.TestCase):
    def setUp(self):
        self.store = Bookstore()
        self.book1 = Book(title="1984", author="George Orwell", isbn="12345", price=300.0, stock=5)

    def test_add_new_book_success(self):
        self.store.add_book(self.book1)
        retrieved_book = self.store.get_book("12345")
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.title, "1984")
        self.assertEqual(retrieved_book.stock, 5)

    def test_add_duplicate_isbn_raises_error(self):
        self.store.add_book(self.book1)
        duplicate_book = Book(title="Animal Farm", author="George Orwell", isbn="12345", price=250.0, stock=3)

        # Очікуємо, що система викине DuplicateISBNError
        with self.assertRaises(DuplicateISBNError):
            self.store.add_book(duplicate_book)


if __name__ == "__main__":
    unittest.main()