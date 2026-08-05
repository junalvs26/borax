import os
import shutil
import tempfile
import unittest
from rag_engine import RAGEngine
from knpack_manager import KNPackManager

class TestRAGEngineAndKNPack(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test LanceDB
        self.test_dir = tempfile.mkdtemp()
        self.rag_engine = RAGEngine(db_dir=self.test_dir)
        self.knpack_mgr = KNPackManager(self.rag_engine)

        # Create a sample test document
        self.sample_txt_path = os.path.join(self.test_dir, "documento_teste.txt")
        self.sample_text = (
            "A Plataforma de IA Local Modular permite executar modelos LLM inteiramente offline. "
            "Ela utiliza o LanceDB como banco de dados vetorial local de alta performance. "
            "O arquivo .knpack armazena a base compilada com metadados e prompt do sistema. "
            "A ingestão suporta arquivos nos formatos TXT, PDF e DOCX com chunking de 500 a 1000 caracteres."
        )
        with open(self.sample_txt_path, "w", encoding="utf-8") as f:
            f.write(self.sample_text)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_file_ingestion(self):
        print("\n--- [TESTE 1] Ingestão de Arquivo ---")
        result = self.rag_engine.process_file(self.sample_txt_path, table_name="test_table")
        print(f"Resultado Ingestão: {result}")
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["chunks_count"], 0)

    def test_02_vector_query(self):
        print("\n--- [TESTE 2] Consulta Vetorial RAG ---")
        self.rag_engine.process_file(self.sample_txt_path, table_name="test_table")
        contexts = self.rag_engine.query_context("O que é o LanceDB?", table_name="test_table", top_k=2)
        print(f"Contextos encontrados: {len(contexts)}")
        for i, ctx in enumerate(contexts):
            print(f"[{i+1}] {ctx['text']}")
        self.assertGreater(len(contexts), 0)
        self.assertIn("LanceDB", contexts[0]["text"])

    def test_03_export_import_knpack(self):
        print("\n--- [TESTE 3] Exportação e Importação de .knpack ---")
        # Ingest first
        self.rag_engine.process_file(self.sample_txt_path, table_name="module_alpha")
        
        # Export
        pack_path = self.knpack_mgr.export_knpack(
            module_name="Modulo Alpha",
            system_prompt="Você é um tutor especialista no Módulo Alpha.",
            table_name="module_alpha",
            description="Test Pack Alpha",
            output_dir=self.test_dir
        )
        print(f"Pacote gerado em: {pack_path}")
        self.assertTrue(os.path.exists(pack_path))
        self.assertTrue(pack_path.endswith(".knpack"))

        # Create a clean RAGEngine in a second directory to test import
        second_dir = tempfile.mkdtemp()
        try:
            second_rag = RAGEngine(db_dir=second_dir)
            second_knpack_mgr = KNPackManager(second_rag)

            import_result = second_knpack_mgr.import_knpack(pack_path)
            print(f"Resultado da Importação: {import_result}")
            self.assertEqual(import_result["status"], "success")
            self.assertEqual(import_result["table_name"], "module_alpha")

            # Verify query works on imported LanceDB instance
            imported_contexts = second_rag.query_context("O que é o .knpack?", table_name="module_alpha")
            self.assertGreater(len(imported_contexts), 0)
            print(f"Consulta pós-importação retornou {len(imported_contexts)} chunks com sucesso.")
        finally:
            if os.path.exists(second_dir):
                shutil.rmtree(second_dir)

if __name__ == "__main__":
    unittest.main()
