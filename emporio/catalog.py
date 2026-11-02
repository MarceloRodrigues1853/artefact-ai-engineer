"""Read-only catalog queries. No customer or order data is loaded."""

import csv
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "material"


def normalize(text: str) -> str:
    """Make searches case- and accent-insensitive, without fuzzy guesses."""
    return "".join(
        char for char in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(char)
    )


@dataclass(frozen=True)
class Promotion:
    promotion_id: str
    discount_percent: Decimal
    description: str


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    price: Decimal
    stock: int
    status: str
    promotion: Promotion | None = None

    @property
    def final_price(self) -> Decimal:
        discount = self.promotion.discount_percent if self.promotion else Decimal("0")
        return (self.price * (1 - discount / 100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def available(self) -> bool:
        return self.status == "active" and self.stock > 0


class Catalog:
    def __init__(self, data_dir: Path = DEFAULT_DATA_DIR):
        self.data_dir = Path(data_dir)
        categories = {row["category_id"]: row["name"] for row in self._read("categories")}
        promotions = {}
        for row in self._read("promotions"):
            if row["is_active"] not in {"0", "1"}:
                raise ValueError("Invalid promotion active flag")
            if row["is_active"] == "0":
                continue
            discount = Decimal(row["discount_percent"])
            if not discount.is_finite() or not 0 < discount <= 100:
                raise ValueError("Invalid active promotion discount")
            if row["product_id"] in promotions:
                raise ValueError(f"Multiple active promotions for product {row['product_id']}; store clarification required")
            promotions[row["product_id"]] = Promotion(row["promotion_id"], discount, row["description"])
        self.products = tuple(
            Product(
                product_id=row["product_id"], name=row["name"],
                category=categories[row["category_id"]],
                price=Decimal(row["price_brl"]), stock=int(row["stock_quantity"]),
                status=row["status"],
                promotion=promotions.get(row["product_id"]),
            )
            for row in self._read("products")
        )
        ids = [product.product_id for product in self.products]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product IDs in catalog")
        if promotions.keys() - set(ids):
            raise ValueError("Active promotion refers to an unknown product")
        for product in self.products:
            if not product.price.is_finite() or product.price < 0 or product.stock < 0:
                raise ValueError(f"Invalid price or stock for product {product.product_id}")

    def _read(self, table: str) -> list[dict[str, str]]:
        paths = list(self.data_dir.glob(f"* - {table}.csv"))
        if len(paths) != 1:
            raise ValueError(f"Expected exactly one {table} CSV in {self.data_dir}")
        with paths[0].open(encoding="utf-8-sig", newline="") as source:
            return list(csv.DictReader(source))

    def search(
        self, query: str = "", *, category: str | None = None,
        max_price: Decimal | None = None, available_only: bool = False,
    ) -> list[Product]:
        """Match all name terms; category must match a known category exactly."""
        if max_price is not None and (not max_price.is_finite() or max_price < 0):
            raise ValueError("Maximum price must be a finite non-negative number")
        terms = normalize(query).split()
        return sorted(
            (
                product for product in self.products
                if all(term in normalize(product.name) for term in terms)
                and (category is None or normalize(category) == normalize(product.category))
                and (max_price is None or product.final_price <= max_price)
                and (not available_only or product.available)
            ),
            key=lambda product: (product.final_price, product.product_id),
        )
