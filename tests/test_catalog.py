import unittest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal

from emporio.catalog import Catalog, Product, Promotion


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()

    def test_known_product_price(self):
        result = self.catalog.search("takamine gd20")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].price, Decimal("2199"))

    def test_available_guitars_within_budget(self):
        result = self.catalog.search(category="Violoes", max_price=Decimal("1000"), available_only=True)
        self.assertIn("81", {product.product_id for product in result})
        self.assertTrue(result)
        self.assertTrue(all(product.available and product.final_price <= 1000 and product.category == "Violões" for product in result))

    def test_active_promotion_and_budget_use_discounted_price(self):
        product = next(p for p in self.catalog.products if p.product_id == "90")
        self.assertEqual(product.promotion.discount_percent, Decimal("18"))
        self.assertEqual(product.final_price, (product.price * Decimal("0.82")).quantize(Decimal("0.01")))
        result = self.catalog.search(product.name, max_price=product.final_price)
        self.assertEqual(result, [product])
        self.assertEqual(self.catalog.search(product.name, max_price=product.final_price - Decimal("0.01")), [])

    def test_inactive_promotion_does_not_change_price(self):
        product = self.catalog.search("takamine gd20")[0]
        self.assertIsNone(product.promotion)
        self.assertEqual(product.final_price, Decimal("2199.00"))

    def test_money_rounds_half_cent_up(self):
        product = Product("test", "Test", "Test", Decimal("10.05"), 1, "active", Promotion("test", Decimal("10"), "Test"))
        self.assertEqual(product.final_price, Decimal("9.05"))

    def test_conflicting_active_promotions_are_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "test - categories.csv").write_text("category_id,name\n1,Test\n", encoding="utf-8")
            with (root / "test - promotions.csv").open("w", encoding="utf-8", newline="") as source:
                writer = csv.writer(source)
                writer.writerow(["promotion_id", "product_id", "discount_percent", "description", "is_active"])
                writer.writerows([["1", "1", "10", "First", "1"], ["2", "1", "20", "Second", "1"]])
            with self.assertRaisesRegex(ValueError, "Multiple active promotions"):
                Catalog(root)

    def test_stock_and_status_both_required(self):
        available_ids = {product.product_id for product in self.catalog.search(available_only=True)}
        for product_id in ("96", "113", "130", "136"):
            with self.subTest(product_id=product_id):
                self.assertNotIn(product_id, available_ids)
                self.assertTrue(any(product.product_id == product_id for product in self.catalog.products))

    def test_unknown_product_does_not_fabricate_match(self):
        self.assertEqual(self.catalog.search("produto inexistente xyz"), [])

    def test_invalid_budget_is_rejected(self):
        for price in ("-1", "NaN", "Infinity"):
            with self.subTest(price=price), self.assertRaises(ValueError):
                self.catalog.search(max_price=Decimal(price))


if __name__ == "__main__":
    unittest.main()
