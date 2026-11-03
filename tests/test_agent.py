import unittest
from copy import deepcopy
from unittest.mock import Mock

from emporio.agent import StoreAgent
from emporio.gemini import GeminiClient, GeminiError


def tool(name, args):
    return {"role": "model", "parts": [{"functionCall": {"name": name, "args": args, "id": "call-1"}, "thoughtSignature": "opaque-signature"}]}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.text = GeminiClient.text
        self.agent = StoreAgent(client=self.client)

    def test_model_gets_real_price_before_answering(self):
        selection = tool("catalogo", {"query": "Takamine GD20"})
        self.client.request.side_effect = [selection, {"parts": [{"text": "Custa R$ 2.199,00."}]}]
        answer = self.agent.ask("Quanto custa o Takamine GD20?")
        self.assertIn("product_id=95", answer)
        self.assertIn("não são uma consulta em tempo real", answer)
        request = self.client.request.call_args_list[1].args[0]
        self.assertEqual(request["contents"][-2], selection)
        result = request["contents"][-1]["parts"][0]["functionResponse"]
        self.assertEqual(result["id"], "call-1")
        self.assertEqual(result["response"]["products"][0]["final_price_brl"], "2199.00")
        self.assertEqual(request["toolConfig"]["functionCallingConfig"]["mode"], "NONE")

    def test_budget_applies_promotion_before_model(self):
        result = self.agent._execute("catalogo", {"query": "Ohana CK-20", "max_price": 450, "available_only": True})
        self.assertEqual(result["products"][0]["final_price_brl"], "439.20")
        self.assertEqual(result["products"][0]["promotion"]["percent"], "20")

    def test_no_evidence_stops_without_generated_claim(self):
        self.client.request.return_value = tool("catalogo", {"query": "inexistente xyz"})
        answer = self.agent.ask("Tem o inexistente xyz?")
        self.assertIn("Não encontrei evidência", answer)
        self.assertEqual(self.client.request.call_count, 1)

    def test_private_data_and_out_of_scope_have_fixed_responses(self):
        for reason in ("dados_privados", "fora_do_escopo"):
            with self.subTest(reason=reason):
                self.client.reset_mock()
                self.client.request.return_value = tool("orientar", {"motivo": reason})
                answer = self.agent.ask("Teste")
                self.assertTrue(answer)
                self.assertEqual(self.client.request.call_count, 1)
                self.assertEqual(self.agent.last_trace[0]["sources"], [])

    def test_unknown_tools_and_wrong_argument_types_are_rejected(self):
        for name, args in (("executar_shell", {"query": "pwd"}), ("catalogo", {"query": "", "available_only": "false"}), ("catalogo", {"query": "", "max_price": True})):
            with self.subTest(name=name, args=args):
                self.client.request.return_value = tool(name, args)
                with self.assertRaises(GeminiError):
                    self.agent.ask("Teste")
                self.assertEqual(self.agent.history, [])

    def test_failed_final_call_does_not_commit_conversation(self):
        before = deepcopy(self.agent.history)
        self.client.request.side_effect = [tool("politicas", {"query": "parcelamento"}), GeminiError("Sem conexão")]
        with self.assertRaises(GeminiError):
            self.agent.ask("Posso parcelar?")
        self.assertEqual(self.agent.history, before)
        result = self.client.request.call_args_list[1].args[0]["contents"][-1]["parts"][0]["functionResponse"]["response"]
        self.assertTrue(result["cautions"])
        self.assertIn(3, [page["page"] for page in result["pages"]])

    def test_prior_turn_is_passed_to_followup(self):
        self.client.request.return_value = tool("orientar", {"motivo": "saudacao"})
        self.agent.ask("Oi")
        self.agent.ask("Quero um violão")
        contents = self.client.request.call_args.args[0]["contents"]
        self.assertEqual(contents[0]["parts"][0]["text"], "Oi")
        self.assertEqual(len(contents), 3)

    def test_generated_source_footer_is_replaced_with_actual_sources(self):
        self.client.request.side_effect = [tool("catalogo", {"query": "Takamine GD20"}),
                                           {"parts": [{"text": "Custa R$ 2.199,00.\n\nFontes consultadas: inventada.pdf, página 99."}]}]
        answer = self.agent.ask("Quanto custa?")
        self.assertNotIn("inventada.pdf", answer)
        self.assertEqual(answer.count("Fontes consultadas:"), 1)
        self.assertIn("product_id=95", answer)
