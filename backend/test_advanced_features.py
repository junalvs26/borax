import os
import shutil
import tempfile
import unittest
from data_analyst import DataAnalyst
from media_processor import MediaProcessor

class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.test_dir, "vendas_teste.csv")
        
        # Sample CSV dataset content
        csv_data = (
            "id,produto,categoria,quantidade,preco_unitario,venda_total\n"
            "1,Notebook Pro,Eletronicos,3,4500.00,13500.00\n"
            "2,Mouse Sem Fio,Acessorios,10,120.00,1200.00\n"
            "3,Teclado Mecanico,Acessorios,5,350.00,1750.00\n"
            "4,Monitor 4K,Eletronicos,2,2200.00,4400.00\n"
            "5,Cadeira Ergonomica,Mobiliario,4,1100.00,4400.00\n"
        )
        with open(self.csv_path, "w", encoding="utf-8") as f:
            f.write(csv_data)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_duckdb_data_analyst(self):
        print("\n--- [TESTE DUCKDB & POLARS DATA ANALYST] ---")
        analyst = DataAnalyst()
        schema_info = analyst.inspect_schema(self.csv_path)
        print(f"Esquema das Colunas: {schema_info['columns']}")
        self.assertIn("produto", schema_info["columns"])
        self.assertIn("venda_total", schema_info["columns"])

        # Execute direct SQL aggregation query
        result = analyst.query_data(self.csv_path, user_query="Qual a soma da venda_total por categoria?")
        print(f"Resultado da Consulta SQL ({result['status']}): {result['results']}")
        self.assertIn(result["status"], ["success", "partial_success"])
        self.assertGreater(len(result["results"]), 0)

    def test_02_media_processor_url_check(self):
        print("\n--- [TESTE MEDIA PROCESSOR URL CHECK] ---")
        processor = MediaProcessor()
        yt_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        local_path = "meu_video.mp4"
        
        self.assertTrue(processor.is_youtube_url(yt_url))
        self.assertFalse(processor.is_youtube_url(local_path))
        print("Validação de URL de mídia do YouTube realizada com sucesso.")

if __name__ == "__main__":
    unittest.main()
