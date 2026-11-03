"""Small, local lexical retriever. Returns evidence, never generated answers."""

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from emporio.catalog import DEFAULT_DATA_DIR, normalize


STOP_WORDS = set("a as o os de da das do dos e em no na nos nas um uma para por com que qual quais como posso pode meu minha voces loja politica politicas sobre tem se eu ate ao aos".split())
ALIASES = {
    "devolver": "devolucao", "devolucoes": "devolucao", "devolucao": "devolucao",
    "arrependi": "arrependimento", "trocar": "troca", "trocas": "troca",
    "horarios": "horario", "abre": "horario", "abrem": "horario",
    "parcelar": "parcelamento", "parcelas": "parcelamento",
    "pagar": "pagamento", "pagamentos": "pagamento",
    "entregas": "entrega", "promocoes": "promocao",
    "descontos": "desconto", "contatos": "contato",
}


def terms(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", normalize(text))
    return {ALIASES.get(token, token) for token in tokens if token not in STOP_WORDS and len(token) > 2}


@dataclass(frozen=True)
class PolicyPage:
    page: int
    text: str


class Policies:
    def __init__(self, path: Path | None = None):
        if path is None:
            paths = list(DEFAULT_DATA_DIR.glob("pol*.pdf"))
            if len(paths) != 1:
                raise ValueError("Expected exactly one policy PDF in data/")
            path = paths[0]
        self.path = Path(path)
        reader = PdfReader(self.path)
        pages = []
        for number, page in enumerate(reader.pages, 1):
            text = " ".join((page.extract_text() or "").split())
            if not text:
                raise ValueError(f"No extractable text on policy page {number}; OCR is not supported")
            # Repeated running headers should not influence retrieval.
            text = re.sub(r"^Empório da Música Manual de Políticas e Procedimentos\s*", "", text)
            text = re.sub(r"\s*Página \d+$", "", text)
            pages.append(PolicyPage(number, text))
        if not pages:
            raise ValueError("Empty policy PDF")
        self.pages = tuple(pages)

    def search(self, query: str, limit: int = 3) -> list[PolicyPage]:
        if not 1 <= limit <= 8:
            raise ValueError("Result limit must be between 1 and 8")
        query_terms = terms(query)
        scored = [(len(query_terms & terms(page.text)), page) for page in self.pages]
        scored.sort(key=lambda item: (-item[0], item[1].page))
        return [page for score, page in scored if score > 0][:limit]

    @staticmethod
    def cautions(query: str) -> list[str]:
        """Known source ambiguities identified during manual review, not a general detector."""
        tokens = terms(query)
        warnings = []
        if tokens & {"pagamento", "parcelamento", "credito", "juros"}:
            warnings.append("Parcelamento: a tabela e a seção 3.1 da página 3 trazem valores mínimos diferentes. Confirmar com a loja antes de assegurar uma condição.")
        if tokens & {"contato", "telefone", "whatsapp", "email", "mail"}:
            warnings.append("Contatos: as páginas 1–2 e 6 apresentam telefones diferentes; os e-mails das páginas 1–2 também diferem. Confirmar o canal correto com a loja.")
        if tokens & {"frete", "entrega"}:
            warnings.append("Frete local: a página 4 não define a regra para pedidos de exatamente R$ 500,00. Não inferir a cobrança nesse limite.")
        return warnings
