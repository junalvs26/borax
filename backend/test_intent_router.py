import unittest
from intent_router import detect_intent, IntentType

class TestIntentRouter(unittest.TestCase):

    def test_01_chat_only_layer3(self):
        print("\n[TESTE ROTEADOR 1/4] Validando mensagens normais como CHAT_ONLY (Camada 3)...")
        queries = [
            "Olá, tudo bem?",
            "Me explique o que é Python e para que serve?",
            "Como funciona a fotossíntese?",
            "Resuma o conceito de inteligência artificial local."
        ]
        for q in queries:
            res = detect_intent(message=q)
            self.assertEqual(res["intent"], IntentType.CHAT_ONLY, f"Deveria ser CHAT_ONLY: '{q}'")
            self.assertEqual(res["layer"], 3)
        print(" -> Todas as conversas normais foram classificadas como CHAT_ONLY (PASS)")

    def test_02_layer1_manual_override(self):
        print("\n[TESTE ROTEADOR 2/4] Validando gatilhos manuais @ e / (Camada 1)...")
        self.assertEqual(detect_intent(message="@criar-base Meu projeto")["intent"], IntentType.MOUNT_CARTRIDGE)
        self.assertEqual(detect_intent(message="@transcrever áudio")["intent"], IntentType.TRANSCRIBE_MEDIA)
        self.assertEqual(detect_intent(message="@gerar-documento Relatório")["intent"], IntentType.GENERATE_DOCUMENT)
        self.assertEqual(detect_intent(message="@analisar-dados CSV")["intent"], IntentType.ANALYZE_DATA)
        print(" -> Gatilhos manuais validados (PASS)")

    def test_03_layer2_file_attachments(self):
        print("\n[TESTE ROTEADOR 3/4] Validando anexos determinísticos (Camada 2)...")
        self.assertEqual(detect_intent(file_name="aula.mp3")["intent"], IntentType.TRANSCRIBE_MEDIA)
        self.assertEqual(detect_intent(file_name="vendas.csv")["intent"], IntentType.ANALYZE_DATA)
        self.assertEqual(detect_intent(file_name="pacote.knpack")["intent"], IntentType.MOUNT_CARTRIDGE)
        self.assertEqual(detect_intent(file_name="manual.pdf")["intent"], IntentType.INGEST_FILE)
        print(" -> Anexos de arquivo validados (PASS)")

    def test_04_layer2_keywords_and_urls(self):
        print("\n[TESTE ROTEADOR 4/4] Validando palavras-chave e URLs do YouTube (Camada 2)...")
        yt_res = detect_intent(message="Transcreva esse vídeo https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(yt_res["intent"], IntentType.TRANSCRIBE_MEDIA)

        doc_res = detect_intent(message="Crie um arquivo Word com o resumo da reunião")
        self.assertEqual(doc_res["intent"], IntentType.GENERATE_DOCUMENT)
        print(" -> Palavras-chave e URLs validadas (PASS)")

if __name__ == "__main__":
    unittest.main()
