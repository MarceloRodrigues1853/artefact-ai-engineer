import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from emporio.gemini import GeminiClient, GeminiError


class GeminiTests(unittest.TestCase):
    def test_missing_key_has_actionable_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(GeminiError, "GEMINI_API_KEY"):
                GeminiClient()

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "gemini-3.1-flash-lite"})
    def test_generation_and_secret_transport(self):
        response = {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "Olá"}]}}]}
        with patch("emporio.gemini.urlopen", return_value=BytesIO(json.dumps(response).encode())) as request:
            self.assertEqual(GeminiClient().generate("Teste"), "Olá")
        sent = request.call_args.args[0]
        self.assertNotIn("test-key", sent.full_url)
        self.assertNotIn("test-key", sent.data.decode())
        self.assertEqual(sent.get_header("X-goog-api-key"), "test-key")

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_api_and_network_errors_do_not_expose_details(self):
        for error in (HTTPError("https://example.com", 429, "test-key", None, None), URLError("test-key")):
            with self.subTest(error=type(error).__name__), patch("emporio.gemini.urlopen", side_effect=error):
                with self.assertRaises(GeminiError) as caught:
                    GeminiClient().generate("Teste")
                self.assertNotIn("test-key", str(caught.exception))

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_blocked_and_truncated_answers_are_not_success(self):
        for response in ({}, {"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "partial"}]}}]}):
            with self.subTest(response=response), patch("emporio.gemini.urlopen", return_value=BytesIO(json.dumps(response).encode())):
                with self.assertRaises(GeminiError):
                    GeminiClient().generate("Teste")
