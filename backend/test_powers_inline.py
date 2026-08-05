import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_power_executor import generate_downloadable_file, ChatPowerExecutor, BORAX_EXPORTS_DIR
from rag_engine import RAGEngine
from knowledge_manager import KnowledgeManager
from media_processor import MediaProcessor
from data_analyst import DataAnalyst

class TestPowersInline(unittest.TestCase):

    def test_01_generate_docx_file(self):
        print("\n[TESTE INLINE 1/3] Gerando arquivo .docx...")
        res = generate_downloadable_file(
            content="Este é um relatório de teste sobre a Plataforma BORAX.",
            file_format="docx",
            filename="relatorio_teste.docx"
        )
        self.assertEqual(res.get("status"), "success")
        self.assertTrue(os.path.exists(res.get("filepath")))
        print(f" -> Arquivo gerado em: {res['filepath']}")
        print(" -> TESTE INLINE 1: OK (PASS)")

    def test_02_generate_txt_file(self):
        print("\n[TESTE INLINE 2/3] Gerando arquivo .txt...")
        res = generate_downloadable_file(
            content="Conteúdo do arquivo TXT exportado.",
            file_format="txt",
            filename="export_teste.txt"
        )
        self.assertEqual(res.get("status"), "success")
        self.assertTrue(os.path.exists(res.get("filepath")))
        print(f" -> Arquivo TXT gerado em: {res['filepath']}")
        print(" -> TESTE INLINE 2: OK (PASS)")

    def test_03_inline_executor_power(self):
        print("\n[TESTE INLINE 3/3] Executando Poder @gerar-documento no ChatPowerExecutor...")
        rag = RAGEngine()
        km = KnowledgeManager(rag_engine=rag)
        mp = MediaProcessor(rag_engine=rag)
        da = DataAnalyst()
        executor = ChatPowerExecutor(rag_engine=rag, knowledge_manager=km, media_processor=mp, data_analyst=da)

        res = executor.execute_inline(
            power_trigger="@gerar-documento",
            text_input="Relatório de Desempenho de IA Local.",
            file_format="docx",
            file_name="desempenho.docx"
        )
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("power"), "@gerar-documento")
        self.assertIn("file", res)
        print(" -> Retorno do Poder Inline OK:", res['status'])
        print(" -> TESTE INLINE 3: OK (PASS)")

if __name__ == "__main__":
    unittest.main()
