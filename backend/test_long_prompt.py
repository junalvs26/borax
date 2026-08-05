import httpx
import json

def test_chat():
    url = "http://127.0.0.1:8000/api/query"
    payload = {
        "query": "Responda em detalhes sobre o universo: " + ("teste " * 300),
        "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "use_rag": False,
        "messages": [
            {"role": "user", "content": "Olá, me dê um resumo sobre física quântica. " + ("histórico " * 200)}
        ]
    }
    
    print("Enviando requisição longa para o backend...")
    try:
        with httpx.stream("POST", url, json=payload, timeout=30.0) as response:
            print(f"Status HTTP: {response.status_code}")
            full_resp = ""
            for chunk in response.iter_text():
                full_resp += chunk
                print(chunk, end="", flush=True)
            print("\n--- FIM ---")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_chat()
