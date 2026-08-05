import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_wizard_engine import DocumentWizardEngine

class TestDocumentWizard(unittest.TestCase):

    def setUp(self):
        self.wizard = DocumentWizardEngine()

    def test_01_initiate_wizard(self):
        print("\n[TESTE WIZARD 1/2] Testando inicialização da moldagem de documento...")
        res = self.wizard.initiate_wizard("Crie um relatório acadêmico em ABNT sobre IA")
        self.assertEqual(res.get("status"), "success")
        self.assertTrue(res.get("wizard_active"))
        self.assertEqual(res["suggested_preferences"]["document_type"], "abnt")
        self.assertEqual(res["suggested_preferences"]["tone"], "scientific")
        print(" -> Sugestão de parâmetros de moldagem OK (PASS)")

    def test_02_generate_custom_document(self):
        print("\n[TESTE WIZARD 2/2] Testando geração de documento customizado ABNT Word (.docx)...")
        prefs = {
            "document_type": "abnt",
            "tone": "scientific",
            "export_format": "docx",
            "filename": "relatorio_abnt_custom.docx"
        }
        res = self.wizard.generate_custom_document(
            prompt="Elaborar estudo sobre infraestrutura local",
            preferences=prefs
        )
        self.assertEqual(res.get("status"), "success")
        self.assertIn("file", res)
        self.assertTrue(os.path.exists(res["file"]["filepath"]))
        print(f" -> Arquivo customizado gerado em: {res['file']['filepath']}")
        print(" -> TESTE WIZARD 2: OK (PASS)")

if __name__ == "__main__":
    unittest.main()
