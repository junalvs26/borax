import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedded_engine import download_model_if_missing, BoraxLLM, list_local_models

def main():
    print("====================================================")
    print("   [TESTE BORAX] Engine de Inferência C++ Embutida  ")
    print("====================================================\n")

    # 1. Download model if missing
    print("[1/3] Verificando/Baixando modelo GGUF leve (~1.1GB)...")
    model_path = download_model_if_missing(
        repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        filename="qwen2.5-1.5b-instruct-q4_k_m.gguf"
    )
    print(f"Modelo disponível em: {model_path}\n")

    # 2. List local GGUF models
    print("[2/3] Listando modelos locais em ~/.borax/models/...")
    models = list_local_models()
    for m in models:
        print(f" - {m['name']} ({m['size'] / (1024*1024):.1f} MB)")
    print()

    # 3. Instantiate BoraxLLM and generate chat response
    print("[3/3] Inicializando BoraxLLM e testando streaming de resposta...")
    llm = BoraxLLM(model_name_or_path=os.path.basename(model_path))

    prompt = "Explique em uma frase o que é o BORAX."
    print(f"\nUsuário: {prompt}")
    print("BORAX C++ Engine: ", end="", flush=True)

    for chunk in llm.generate_stream(prompt=prompt, system_prompt="Você é um assistente rápido e objetivo."):
        print(chunk, end="", flush=True)
    print("\n\n====================================================")
    print("   Teste C++ Embutido Concluído com Sucesso!        ")
    print("====================================================")

if __name__ == "__main__":
    main()
