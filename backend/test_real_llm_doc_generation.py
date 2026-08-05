import os
import sys
import unittest
import docx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_generator import convert_markdown_to_docx
from document_wizard_engine import DocumentWizardEngine

class TestRealLLMDocGeneration(unittest.TestCase):

    def setUp(self):
        self.wizard = DocumentWizardEngine()

    def test_01_awaiting_wizard_interruption(self):
        print("\n[TESTE REAL LLM 1/3] Validando interrupção de requisitos (awaiting_wizard)...")
        res = self.wizard.initiate_wizard("gerar docx")
        self.assertEqual(res["status"], "awaiting_wizard")
        self.assertTrue(res["wizard_active"])
        self.assertIn("message", res)
        print(" -> Interrupção com status awaiting_wizard: OK (PASS)")

    def test_02_markdown_to_abnt_docx_converter(self):
        print("\n[TESTE REAL LLM 2/3] Validando conversor ABNT (convert_markdown_to_docx)...")
        test_markdown = """# ESTUDO DE IMPACTO DAS IAs LOCAIS

O presente estudo analisa de forma detalhada o impacto da adoção de modelos de linguagem locais.

## 1. INTRODUÇÃO E OBJETIVOS
A soberania dos dados e a privacidade representam pilares fundamentais.

- **Privacidade Total:** Processamento 100% offline no dispositivo.
- **Desempenho Estável:** Baixa latência sem dependência de APIs externas.

## 2. CONCLUSÃO
Conclui-se que a infraestrutura local garante eficiência e segurança.
"""
        target_path = os.path.expanduser("~/.borax/exports/test_abnt_conversion.docx")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        filepath = convert_markdown_to_docx(test_markdown, target_path)
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 1000)

        # Inspect DOCX elements and ABNT formatting
        doc = docx.Document(filepath)
        self.assertGreater(len(doc.paragraphs), 3)
        self.assertAlmostEqual(doc.sections[0].top_margin.cm, 3.0, places=1)
        self.assertAlmostEqual(doc.sections[0].left_margin.cm, 3.0, places=1)

        print(f" -> DOCX ABNT convertido e validado em: {filepath} ({os.path.getsize(filepath)} bytes)")
        print(" -> TESTE REAL LLM 2: OK (PASS)")

    def test_03_full_pipeline_llm_generation(self):
        print("\n[TESTE REAL LLM 3/3] Validando pipeline completa de geração via LLM e exportação...")
        user_prefs = {
            "theme": "Automação Industrial com Aprendizado de Máquina",
            "sections": "Introdução, Sensores IoT, Algoritmos Preditivos, Conclusão",
            "document_type": "abnt",
            "tone": "scientific",
            "export_format": "docx",
            "filename": "automacao_industrial_abnt.docx"
        }

        res = self.wizard.generate_custom_document(
            prompt="gerar docx",
            preferences=user_prefs
        )

        self.assertEqual(res["status"], "success")
        self.assertIn("file", res)
        filepath = res["file"]["filepath"]
        self.assertTrue(os.path.exists(filepath))
        
        print(f" -> Arquivo final gerado pela LLM em: {filepath}")
        print(" -> TESTE REAL LLM 3: OK (PASS)")

if __name__ == "__main__":
    unittest.main()
