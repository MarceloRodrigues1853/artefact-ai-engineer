"""Inspect the same catalog tool the LLM will use."""

import argparse
from decimal import Decimal, InvalidOperation

from emporio.catalog import Catalog


def money(value: Decimal) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta local ao catálogo do Empório da Música")
    parser.add_argument("query", nargs="?", default="", help="Nome ou parte do nome do produto")
    parser.add_argument("--category", help="Categoria exata, por exemplo: Violões")
    parser.add_argument("--max-price", help="Preço máximo após promoção ativa, por exemplo: 1000.00")
    parser.add_argument("--available-only", action="store_true")
    args = parser.parse_args()
    try:
        products = Catalog().search(
            args.query, category=args.category,
            max_price=Decimal(args.max_price) if args.max_price is not None else None,
            available_only=args.available_only,
        )
    except (ValueError, InvalidOperation, OSError, KeyError) as error:
        parser.exit(2, f"Não foi possível consultar o catálogo: {error}\n")
    if not products:
        print("Não encontrei produtos para esses filtros no catálogo fornecido.")
        return
    for product in products:
        availability = "disponível" if product.available else "indisponível para venda"
        print(f"[{product.product_id}] {product.name} — {money(product.price)} (preço-base); {availability}")
        print(f"  Fonte: products.csv, product_id={product.product_id}; status={product.status}; estoque={product.stock}")
        if product.promotion:
            promotion = product.promotion
            print(f"  Promoção ativa: {promotion.description}; desconto de {promotion.discount_percent}%; preço final: {money(product.final_price)}")
            print(f"  Fonte: promotions.csv, promotion_id={promotion.promotion_id}; is_active=1")
        else:
            print("  Sem promoção ativa no arquivo fornecido.")
    print("Valores e promoções dos arquivos fornecidos; datas de validade não informadas.")


if __name__ == "__main__":
    main()
