import os
import json
import zipfile
import tempfile
from knpack_manager import KNPackManager

def test_knpack_zip():
    print("--- [VERIFICAÇÃO DE ESTRUTURA DO .KNPACK] ---")
    temp_dir = tempfile.mkdtemp()
    pack_path = os.path.join(temp_dir, "teste_modulo.knpack")

    manifest_sample = {
        "module_name": "Modulo Tradutor PoC",
        "description": "Pacote vetorial de teste para verificacao ZIP",
        "system_prompt": "Voce e um assistente especialista neste pacote local.",
        "version": "1.0.0",
        "table_name": "knowledge_base",
        "created_at": "2026-08-03T08:30:00",
        "chunks_count": 5
    }

    vectors_sample = [
        {"id": "chunk-1", "text": "A IA local roda 100% offline.", "filename": "doc1.txt", "vector": [0.1, 0.2, 0.3]},
        {"id": "chunk-2", "text": "LanceDB armazena vetores com alta performance.", "filename": "doc2.pdf", "vector": [0.4, 0.5, 0.6]}
    ]

    with zipfile.ZipFile(pack_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("manifest.json", json.dumps(manifest_sample, indent=2))
        zipf.writestr("vectors.json", json.dumps(vectors_sample, indent=2))

    print(f"1. Arquivo .knpack criado em: {pack_path}")
    print(f"2. É um arquivo ZIP válido? -> {zipfile.is_zipfile(pack_path)}")

    with zipfile.ZipFile(pack_path, "r") as zipf:
        file_list = zipf.namelist()
        print(f"3. Conteúdo interno do arquivo .knpack (Zip): {file_list}")
        manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
        vectors_data = json.loads(zipf.read("vectors.json").decode("utf-8"))

        print("\n--- Conteúdo do manifest.json ---")
        print(json.dumps(manifest_data, indent=2, ensure_ascii=False))

        print(f"\n--- Chunks contidos em vectors.json ({len(vectors_data)} itens) ---")
        for item in vectors_data:
            print(f"- [{item['filename']}] {item['text']}")

if __name__ == "__main__":
    test_knpack_zip()
