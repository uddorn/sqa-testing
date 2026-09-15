import unittest
from bookstore import Bookstore


class TestAddBook(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()

    def test_add_new_book(self):
        self.shop.add_book("1984", "George Orwell", 10.0, 5)
        result = self.shop.search_book("1984")
        self.assertEqual(result["author"], "George Orwell")
        self.assertEqual(result["price"], 10.0)
        self.assertEqual(result["quantity"], 5)

    def test_add_duplicate_book_increases_quantity(self):
        self.shop.add_book("1984", "George Orwell", 10.0, 5)
        self.shop.add_book("1984", "George Orwell", 10.0, 3)
        result = self.shop.search_book("1984")
        self.assertEqual(result["quantity"], 8)

    def test_add_book_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.shop.add_book("Тигролови", "Іван Багряний", -5.0, 1)

    def test_add_book_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.shop.add_book("Тигролови", "Іван Багряний", 5.0, -1)

    def test_add_book_empty_title_raises(self):
        with self.assertRaises(ValueError):
            self.shop.add_book("", "Іван Багряний", 5.0, 1)


class TestRemoveBook(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()
        self.shop.add_book("1984", "George Orwell", 10.0, 5)

    def test_remove_existing_book(self):
        self.shop.remove_book("1984")
        self.assertIsNone(self.shop.search_book("1984"))

    def test_remove_nonexistent_book_no_error(self):
        self.shop.remove_book("Fahrenheit 451")
        self.assertIsNone(self.shop.search_book("Fahrenheit 451"))


class TestSearchBook(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()
        self.shop.add_book("1984", "George Orwell", 10.0, 5)

    def test_search_existing_book_returns_correct_data(self):
        result = self.shop.search_book("1984")
        self.assertEqual(
            result,
            {"title": "1984", "author": "George Orwell", "price": 10.0, "quantity": 5},
        )

    def test_search_nonexistent_book_returns_none(self):
        self.assertIsNone(self.shop.search_book("Fahrenheit 451"))

    def test_search_empty_title_returns_none(self):
        self.assertIsNone(self.shop.search_book(""))

    def test_search_none_title_returns_none(self):
        self.assertIsNone(self.shop.search_book(None))


class TestPurchaseBook(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()
        self.shop.add_book("1984", "George Orwell", 10.0, 5)

    def test_purchase_book_success(self):
        total = self.shop.purchase_book("1984", 2)
        self.assertEqual(total, 20.0)
        self.assertEqual(self.shop.search_book("1984")["quantity"], 3)

    def test_purchase_more_than_available_raises(self):
        with self.assertRaises(ValueError):
            self.shop.purchase_book("1984", 100)
        self.assertEqual(self.shop.search_book("1984")["quantity"], 5)

    def test_purchase_nonexistent_book_raises(self):
        with self.assertRaises(ValueError):
            self.shop.purchase_book("Fahrenheit 451", 1)

    def test_purchase_zero_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.shop.purchase_book("1984", 0)

    def test_purchase_from_zero_stock_raises(self):
        self.shop.add_book("Місто", "Валер'ян Підмогильний", 5.0, 0)
        with self.assertRaises(ValueError):
            self.shop.purchase_book("Місто", 1)


class TestInventoryValue(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()

    def test_inventory_value_empty_shop(self):
        self.assertEqual(self.shop.inventory_value(), 0)

    def test_inventory_value_with_books(self):
        self.shop.add_book("1984", "George Orwell", 10.0, 5)
        self.shop.add_book("Dune", "Frank Herbert", 15.0, 2)
        self.assertEqual(self.shop.inventory_value(), 80.0)

    def test_inventory_value_updates_after_purchase(self):
        self.shop.add_book("1984", "George Orwell", 10.0, 5)
        self.shop.purchase_book("1984", 2)
        self.assertEqual(self.shop.inventory_value(), 30.0)


class TestDiscounts(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()
        self.shop.add_book("1984", "George Orwell", 10.0, 5)

    def test_apply_discount_reduces_purchase_price(self):
        self.shop.apply_discount("1984", 20)
        total = self.shop.purchase_book("1984", 2)
        self.assertAlmostEqual(total, 16.0)

    def test_purchase_without_discount_unaffected(self):
        total = self.shop.purchase_book("1984", 2)
        self.assertEqual(total, 20.0)

    def test_apply_discount_nonexistent_book_raises(self):
        with self.assertRaises(ValueError):
            self.shop.apply_discount("Fahrenheit 451", 10)

    def test_apply_discount_negative_percent_raises(self):
        with self.assertRaises(ValueError):
            self.shop.apply_discount("1984", -5)

    def test_apply_discount_over_100_percent_raises(self):
        with self.assertRaises(ValueError):
            self.shop.apply_discount("1984", 150)

    def test_remove_discount_restores_full_price(self):
        self.shop.apply_discount("1984", 50)
        self.shop.remove_discount("1984")
        total = self.shop.purchase_book("1984", 1)
        self.assertEqual(total, 10.0)

    def test_get_discount_default_is_zero(self):
        self.assertEqual(self.shop.get_discount("1984"), 0)

    def test_discount_cleared_when_book_removed(self):
        self.shop.apply_discount("1984", 30)
        self.shop.remove_book("1984")
        self.assertEqual(self.shop.get_discount("1984"), 0)


class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.shop = Bookstore()
        self.shop.add_book("1984", "George Orwell", 10.0, 5)

    def test_register_customer_success(self):
        self.shop.register_customer("reader_01", "reader01@bookmail.net")
        customer = self.shop.get_customer("reader01@bookmail.net")
        self.assertEqual(customer["name"], "reader_01")
        self.assertEqual(customer["purchase_history"], [])

    def test_register_duplicate_email_raises(self):
        self.shop.register_customer("reader_01", "reader01@bookmail.net")
        with self.assertRaises(ValueError):
            self.shop.register_customer("reader_02", "reader01@bookmail.net")

    def test_register_customer_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.shop.register_customer("", "reader01@bookmail.net")

    def test_register_customer_empty_email_raises(self):
        with self.assertRaises(ValueError):
            self.shop.register_customer("reader_01", "")

    def test_get_nonexistent_customer_returns_none(self):
        self.assertIsNone(self.shop.get_customer("unregistered@bookmail.net"))

    def test_get_customer_empty_email_returns_none(self):
        self.assertIsNone(self.shop.get_customer(""))

    def test_purchase_book_for_customer_records_history(self):
        self.shop.register_customer("reader_01", "reader01@bookmail.net")
        total = self.shop.purchase_book_for_customer("reader01@bookmail.net", "1984", 2)
        self.assertEqual(total, 20.0)
        history = self.shop.get_customer("reader01@bookmail.net")["purchase_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], {"title": "1984", "quantity": 2, "total": 20.0})

    def test_purchase_book_for_nonexistent_customer_raises(self):
        with self.assertRaises(ValueError):
            self.shop.purchase_book_for_customer("unregistered@bookmail.net", "1984", 1)


if __name__ == "__main__":
    unittest.main()