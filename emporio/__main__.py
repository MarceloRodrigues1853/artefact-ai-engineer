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
    parser.add_argument("--policy", action="store_true", help="Buscar páginas do manual em vez de produtos")
    parser.add_argument("--check-model", action="store_true", help="Enviar uma mensagem curta de diagnóstico ao Gemini")
    parser.add_argument("--ask", metavar="PERGUNTA", help="Perguntar ao atendente usando as ferramentas da loja")
    parser.add_argument("--chat", action="store_true", help="Conversar com contexto temporário; digite sair para encerrar")
    parser.add_argument("--trace", action="store_true", help="Mostrar ferramentas e fontes consultadas no atendimento")
    args = parser.parse_args()
    if args.ask is not None or args.chat:
        if (args.ask is not None and args.chat) or args.query or args.policy or args.check_model or args.category is not None or args.max_price is not None or args.available_only:
            parser.error("Use --ask PERGUNTA ou --chat, opcionalmente com --trace, sem filtros de consulta direta.")
        from emporio.gemini import GeminiError
        try:
            from emporio.agent import StoreAgent
            agent = StoreAgent()
        except ImportError:
            parser.exit(2, "Instale a dependência do PDF: python -m pip install -r requirements.txt\n")
        except (GeminiError, ValueError, OSError, KeyError) as error:
            parser.exit(2, f"Não foi possível iniciar o atendimento: {error}\n")

        def respond(question):
            try:
                answer = agent.ask(question)
                if args.trace:
                    for trace in agent.last_trace:
                        print(f"[consulta] {trace['tool']}: {len(trace['sources'])} referências retornadas")
                print(f"Empório: {answer}")
                return True
            except (GeminiError, ValueError, OSError) as error:
                print(f"Não foi possível responder: {error}")
                return False

        if args.ask is not None:
            if not respond(args.ask):
                parser.exit(2)
            return
        print("Atendimento iniciado. Digite sair para encerrar. Contexto mantido apenas nesta sessão.")
        print("As mensagens e os resultados consultados são enviados ao Gemini. Não informe dados pessoais.")
        try:
            while True:
                question = input("Você: ").strip()
                if question.casefold() in {"sair", "exit", "quit"}:
                    break
                if question:
                    respond(question)
        except (EOFError, KeyboardInterrupt):
            print("\nAtendimento encerrado.")
        return
    if args.trace:
        parser.error("Use --trace com --ask ou --chat.")
    if args.check_model:
        if args.query or args.policy or args.category is not None or args.max_price is not None or args.available_only:
            parser.error("Use --check-model sozinho.")
        from emporio.gemini import GeminiClient, GeminiError
        try:
            client = GeminiClient()
            print(f"Teste de conexão e geração com {client.model}; sem dados da loja.")
            print(client.generate("Responda apenas com esta frase: Conexão com o Gemini funcionando."))
        except GeminiError as error:
            parser.exit(2, f"Não foi possível concluir o teste: {error}\n")
        return
    if args.policy:
        if args.category is not None or args.max_price is not None or args.available_only:
            parser.error("Não combine --policy com filtros de produtos.")
        try:
            from emporio.policies import Policies
            policies = Policies()
            pages = policies.search(args.query)
            if not pages:
                print("Não encontrei evidência para esses termos no manual. Tente reformular ou confirme com a loja.")
                return
            for warning in policies.cautions(args.query):
                print(f"Atenção: {warning}")
            for page in pages:
                print(f"\nFonte: {policies.path.name}, página {page.page}\n{page.text}")
            print("\nBusca por palavras: estes trechos são evidências candidatas, não uma resposta ou aprovação de solicitação. Algumas regras continuam na página seguinte.")
        except ImportError:
            parser.exit(2, "Instale a dependência do PDF: python -m pip install -r requirements.txt\n")
        except (ValueError, OSError) as error:
            parser.exit(2, f"Não foi possível consultar as políticas: {error}\n")
        return
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
