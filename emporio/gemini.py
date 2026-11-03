"""Minimal Gemini REST client. Credentials are sent in a header, never a URL."""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_MODEL = "gemini-3.1-flash-lite"


class GeminiError(RuntimeError):
    """Safe, user-facing API failure without raw response or credentials."""


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()
        if not self.api_key:
            raise GeminiError("GEMINI_API_KEY não está configurada neste terminal.")
        if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+", self.model):
            raise GeminiError("GEMINI_MODEL tem formato inválido.")

    def generate(self, prompt: str) -> str:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 128},
        }
        return self.text(self.request(payload))

    @staticmethod
    def text(content: dict) -> str:
        parts = content["parts"]
        if any("functionCall" in part for part in parts):
            raise GeminiError("O modelo solicitou outra consulta em vez de responder.")
        text = "".join(part.get("text", "") for part in parts if not part.get("thought"))
        if not text.strip():
            raise GeminiError("O modelo não retornou uma resposta de texto.")
        return text.strip()

    def request(self, payload: dict) -> dict:
        """Return full model content, preserving function-call IDs and signatures."""
        request = Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
        except HTTPError as error:
            error.close()
            messages = {
                400: "Solicitação recusada; verifique a chave e a configuração do modelo.",
                401: "Autenticação recusada pela API.",
                403: "A chave não tem acesso à operação solicitada.",
                404: "Modelo não encontrado ou indisponível para esta chave.",
                429: "Limite de uso ou cota atingido; nenhuma repetição automática foi feita.",
            }
            raise GeminiError(messages.get(error.code, f"API indisponível (HTTP {error.code}).")) from None
        except (URLError, TimeoutError, OSError):
            raise GeminiError("Não foi possível conectar ao Gemini. Verifique rede, DNS e acesso HTTPS.") from None
        except (ValueError, UnicodeError):
            raise GeminiError("A API retornou uma resposta ilegível.") from None
        if not isinstance(result, dict):
            raise GeminiError("A API retornou uma estrutura inesperada.")
        candidates = result.get("candidates") or []
        if not candidates or not isinstance(candidates[0], dict):
            raise GeminiError("O modelo não retornou uma resposta de texto.")
        candidate = candidates[0]
        if candidate.get("finishReason") != "STOP":
            raise GeminiError("O modelo não concluiu uma resposta normal; saída parcial omitida.")
        content = candidate.get("content")
        if not isinstance(content, dict) or not isinstance(content.get("parts"), list) or not content["parts"]:
            raise GeminiError("O modelo não retornou conteúdo utilizável.")
        if any(not isinstance(part, dict) for part in content["parts"]):
            raise GeminiError("O modelo retornou conteúdo inesperado.")
        return content
