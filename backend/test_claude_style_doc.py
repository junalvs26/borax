import os
import sys
import unittest
import docx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_wizard_engine import DocumentWizardEngine
from document_generator import convert_markdown_to_docx

class TestClaudeStyleDoc(unittest.TestCase):

    def setUp(self):
        self.wizard = DocumentWizardEngine()

    def test_01_claude_style_synthesis_and_no_raw_markers(self):
        print("\n[TESTE ESTILO CLAUDE 1/2] Validando redação fluida e ausência de marcadores brutos...")
        
        simulated_rag_context = """[knowledge_base]: A Lei nº 11.105/2005 (Lei de Biossegurança) regulamenta os incisos II, IV e V do § 1º do art. 225 da Constituição Federal, estabelece normas de segurança e mecanismos de fiscalização de atividades que envolvem organismos geneticamente modificados (OGM) e seus derivados.
[table_vendas]: A CTNBio (Comissão Técnica Nacional de Biossegurança) integra o Ministério da Ciência, Tecnologia e Inovação."""

        user_prefs = {
            "theme": "Legislação de Biossegurança e OGMs no Brasil",
            "sections": "Introdução, Histórico da Lei 11.105/2005, Papel da CTNBio, Conclusão",
            "document_type": "abnt",
            "tone": "scientific",
            "export_format": "docx",
            "filename": "biosseguranca_ogm_abnt.docx"
        }

        res = self.wizard.generate_custom_document(
            prompt="gerar docx",
            preferences=user_prefs,
            context_text=simulated_rag_context
        )

        self.assertEqual(res["status"], "success")
        doc_text = res["document_text"]

        # 1. Assert NO raw markers exist in synthesized text
        self.assertNotIn("[knowledge_base]:", doc_text)
        self.assertNotIn("[table_vendas]:", doc_text)
        self.assertNotIn("# DOCUMENTO PERSONALIZADO", doc_text)

        # 2. Assert text is fluid academic text
        self.assertIn("Biossegurança", doc_text)
        self.assertIn("INTRODUÇÃO", doc_text.upper())
        self.assertIn("CONCLUSÃO", doc_text.upper())

        print(" -> Redação fluida sem marcadores brutos validadas com sucesso (PASS)")

    def test_02_docx_abnt_formatting_validation(self):
        print("\n[TESTE ESTILO CLAUDE 2/2] Validando compilação .docx com formatação ABNT...")
        filepath = os.path.expanduser("~/.borax/exports/biosseguranca_ogm_abnt.docx")
        self.assertTrue(os.path.exists(filepath))
        self.assertGreater(os.path.getsize(filepath), 1000)

        # Inspect document paragraphs
        doc = docx.Document(filepath)
        self.assertGreater(len(doc.paragraphs), 4)
        
        # Verify margins (ABNT 3cm top/left, 2cm bottom/right)
        self.assertAlmostEqual(doc.sections[0].top_margin.cm, 3.0, places=1)
        self.assertAlmostEqual(doc.sections[0].left_margin.cm, 3.0, places=1)

        print(f" -> Arquivo .docx ABNT verificado em: {filepath} ({os.path.getsize(filepath)} bytes)")
        print(" -> TESTE ESTILO CLAUDE 2: OK (PASS)")

if __name__ == "__main__":
    unittest.main()
