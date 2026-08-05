import os
import json
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from rag_engine import RAGEngine, DEFAULT_TABLE

class KNPackManager:
    def __init__(self, rag_engine: Optional[RAGEngine] = None):
        self.rag_engine = rag_engine or RAGEngine()

    def export_knpack(
        self,
        module_name: str,
        system_prompt: str,
        table_name: str = DEFAULT_TABLE,
        description: str = "",
        output_dir: Optional[str] = None
    ) -> str:
        """Export LanceDB table vectors and module prompt into a compressed .knpack file."""
        records = self.rag_engine.get_all_records(table_name)
        if not records:
            raise ValueError(f"A tabela '{table_name}' está vazia ou não existe no LanceDB.")

        out_dir = output_dir or tempfile.gettempdir()
        filename_safe = module_name.lower().replace(" ", "_")
        pack_filename = f"{filename_safe}.knpack"
        pack_filepath = os.path.join(out_dir, pack_filename)

        manifest = {
            "module_name": module_name,
            "description": description or f"Módulo de Conhecimento {module_name}",
            "system_prompt": system_prompt,
            "version": "1.0.0",
            "table_name": table_name,
            "created_at": datetime.now().isoformat(),
            "chunks_count": len(records)
        }

        with zipfile.ZipFile(pack_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 1. Manifest metadatos
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            # 2. Dados dos vetores e textos
            zipf.writestr("vectors.json", json.dumps(records, indent=2, ensure_ascii=False))

        return pack_filepath

    def import_knpack(self, knpack_path: str) -> Dict[str, Any]:
        """Import a .knpack file, extract manifest metadata, and restore table into LanceDB."""
        if not os.path.exists(knpack_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {knpack_path}")

        if not zipfile.is_zipfile(knpack_path):
            raise ValueError("O arquivo fornecido não é um pacote .knpack (ZIP) válido.")

        with zipfile.ZipFile(knpack_path, "r") as zipf:
            names = zipf.namelist()
            if "manifest.json" not in names or "vectors.json" not in names:
                raise ValueError("Estrutura .knpack inválida. Faltam 'manifest.json' ou 'vectors.json'.")

            manifest_content = zipf.read("manifest.json").decode("utf-8")
            vectors_content = zipf.read("vectors.json").decode("utf-8")

            manifest = json.loads(manifest_content)
            records = json.loads(vectors_content)

        table_name = manifest.get("table_name", DEFAULT_TABLE)
        table = self.rag_engine._ensure_table(table_name)

        if records:
            table.add(records)

        return {
            "status": "success",
            "message": f"Módulo '{manifest.get('module_name')}' importado com sucesso!",
            "manifest": manifest,
            "table_name": table_name,
            "chunks_imported": len(records)
        }
