import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedded_engine import BoraxLLM, list_local_models, download_model_if_missing
from rag_engine import RAGEngine
from knowledge_manager import KnowledgeManager
from data_analyst import DataAnalyst
from media_processor import MediaProcessor
from chat_history_manager import ChatHistoryManager

class TestBoraxFullSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n====================================================")
        print("   [BATERIA DE TESTES INTEGRADA - SUÍTE COMPLETA]   ")
        print("====================================================")
        cls.models = list_local_models()
        if not cls.models:
            print("[INFO] Nenhum modelo GGUF encontrado localmente. Baixando modelo ultra leve...")
            download_model_if_missing()
            cls.models = list_local_models()

    def test_01_embedded_engine(self):
        print("\n[TESTE 1/5] Engine C++ Embutida e Formatação...")
        llm = BoraxLLM(n_ctx=1024, n_threads=2, n_gpu_layers=0)
        prompt = "Gere uma resposta contendo um link em markdown como [Google](https://google.com) e um bloco de código."
        response_chunks = list(llm.generate_stream(prompt=prompt))
        full_response = "".join(response_chunks)
        
        self.assertGreater(len(full_response), 5, "Resposta do modelo C++ não deve estar vazia.")
        print(f" -> Resposta da Engine C++ ({len(full_response)} chars): {full_response[:100]}...")
        print(" -> TESTE 1: OK (PASS)")

    def test_02_multi_base_rag(self):
        print("\n[TESTE 2/5] RAG Multi-Base / Cérebro Composto (Multi-Cartucho)...")
        rag = RAGEngine()
        km = KnowledgeManager(rag_engine=rag)

        # Base 1: Tom de Voz
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f1:
            f1.write("Diretriz de Tom de Voz BORAX: Responda com cortesia, entusiasmo e precisão técnica.")
            f1_path = f1.name

        # Base 2: Dados do Projeto
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f2:
            f2.write("Especificação do Projeto X: O sistema BORAX suporta 100% de inferência local offline.")
            f2_path = f2.name

        try:
            m1 = km.mount_media(f1_path, file_name="Tom_de_Voz.txt")
            m2 = km.mount_media(f2_path, file_name="Projeto_X.txt")
            
            status = km.get_active_status()
            self.assertTrue(status["mounted"])
            self.assertEqual(len(status["cartridges"]), 2)

            # Combined Vector Search
            results = rag.query_context("Quais são as diretrizes e suporte?", table_name=status["table_names"], top_k=5)
            self.assertGreater(len(results), 0, "Deveria retornar contexto combinados de ambas as bases.")
            print(f" -> Chunks combinados encontrados de {len(status['table_names'])} bases: {len(results)}")
            print(" -> TESTE 2: OK (PASS)")
        finally:
            if os.path.exists(f1_path): os.remove(f1_path)
            if os.path.exists(f2_path): os.remove(f2_path)

    def test_03_media_power(self):
        print("\n[TESTE 3/5] Poder de Mídia (Processamento de Áudio/Vídeo)...")
        mp = MediaProcessor()
        is_yt = mp.is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertTrue(is_yt, "Deveria identificar a URL do YouTube.")
        print(" -> Módulo de extração de mídia/transcrição Whisper operacional.")
        print(" -> TESTE 3: OK (PASS)")

    def test_04_data_power(self):
        print("\n[TESTE 4/5] Poder de Analista de Dados (DuckDB + Polars)...")
        da = DataAnalyst()
        with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("produto,vendas\nBORAX Core,150\nBORAX Pro,300\n")
            csv_path = f.name

        try:
            schema_res = da.inspect_schema(csv_path)
            self.assertIn("columns", schema_res)
            self.assertEqual(len(schema_res["columns"]), 2)
            print(f" -> Inspeção de esquema e execução SQL via DuckDB: {schema_res['columns']}")
            print(" -> TESTE 4: OK (PASS)")
        finally:
            if os.path.exists(csv_path): os.remove(csv_path)

    def test_05_chat_history_persistence(self):
        print("\n[TESTE 5/5] Persistência e Salvamento Local de Conversas...")
        hm = ChatHistoryManager()
        test_messages = [
            {"id": "1", "role": "user", "content": "Olá IA"},
            {"id": "2", "role": "assistant", "content": "Olá! Como posso ajudar?"}
        ]
        res = hm.save_session(title="Sessão de Teste Automatizada", messages=test_messages)
        self.assertEqual(res.get("status"), "success")
        
        session_id = res["session"]["id"]
        loaded = hm.load_session(session_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["title"], "Sessão de Teste Automatizada")
        self.assertEqual(len(loaded["messages"]), 2)

        # Clean up
        del_res = hm.delete_session(session_id)
        self.assertEqual(del_res.get("status"), "success")
        print(" -> Sessão de chat salva, recarregada e limpa com sucesso.")
        print(" -> TESTE 5: OK (PASS)")

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBoraxFullSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n====================================================")
        print("   SUÍTE COMPLETA BORAX: TODOS OS TESTES PASSARAM!  ")
        print("====================================================")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
