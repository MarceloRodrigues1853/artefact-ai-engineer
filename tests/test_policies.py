import unittest

from emporio.policies import Policies


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policies = Policies()

    def test_returns_page_with_online_return_conditions(self):
        pages = self.policies.search("Posso devolver minha compra online?")
        self.assertEqual(pages[0].page, 4)
        self.assertIn("7 (sete) dias corridos após o recebimento", pages[0].text)
        self.assertIn("Compras Online", pages[0].text)

    def test_opening_hours(self):
        pages = self.policies.search("Qual o horário de funcionamento?")
        self.assertEqual(pages[0].page, 2)
        self.assertIn("Domingo e Feriados Fechado", pages[0].text)

    def test_absent_evidence(self):
        self.assertEqual(self.policies.search("astronomia plutao galaxia"), [])
        self.assertEqual(self.policies.search(""), [])

    def test_discount_combination_rule_is_preserved(self):
        pages = self.policies.search("desconto PIX cumulatividade")
        self.assertEqual(pages[0].page, 6)
        self.assertIn("não se aplica sobre preços já promocionais", pages[0].text)

    def test_known_conflicts_are_flagged(self):
        self.assertTrue(Policies.cautions("Posso parcelar?"))
        self.assertTrue(Policies.cautions("Qual o WhatsApp?"))
        self.assertTrue(Policies.cautions("Qual o frete?"))
        self.assertEqual(Policies.cautions("horário"), [])


if __name__ == "__main__":
    unittest.main()
