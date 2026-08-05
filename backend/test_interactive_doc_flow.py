import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_wizard_engine import DocumentWizardEngine

class TestInteractiveDocFlow(unittest.TestCase):

    def setUp(self):
        self.wizard = DocumentWizardEngine()

    def test_01_requirements_interruption(self):
        print("\n[TESTE INTERATIVO 1/2] Validando interrupção para coleta de requisitos...")
        res = self.wizard.initiate_wizard("gerar docx")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["wizard_active"])
        self.assertIn("suggested_preferences", res)
        print(" -> Interrupção obrigatória OK (PASS)")

    def test_02_llm_articulated_generation(self):
        print("\n[TESTE INTERATIVO 2/2] Validando redação articulada pela LLM e compilação .docx...")
        user_prefs = {
            "theme": "Impacto da Inteligência Artificial Local na Medicina Diagnóstica",
            "sections": "Introdução, Tecnologias de Imagem, Ética e Privacidade, Conclusão",
            "document_type": "abnt",
            "tone": "scientific",
            "export_format": "docx",
            "filename": "trabalho_ia_medicina.docx"
        }

        res = self.wizard.generate_custom_document(
            prompt="gerar docx",
            preferences=user_prefs
        )

        self.assertEqual(res["status"], "success")
        self.assertIn("file", res)
        filepath = res["file"]["filepath"]
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 1000)

        print(f" -> Documento articulado ABNT gerado no disco: {filepath} ({res['file']['size_bytes']} bytes)")
        print(" -> TESTE INTERATIVO 2: OK (PASS)")

if __name__ == "__main__":
    unittest.main()
