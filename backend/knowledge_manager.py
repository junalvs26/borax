import os
import json
import shutil
import zipfile
import tempfile
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from rag_engine import RAGEngine, DEFAULT_TABLE
from knpack_manager import KNPackManager

DEFAULT_CARTRIDGE = {
    "id": "default",
    "mounted": False,
    "name": "Nenhum Cartucho Montado",
    "type": "default",
    "table_name": DEFAULT_TABLE,
    "vectors_count": 0,
    "size_bytes": 0,
    "system_prompt": "Você é um assistente de IA local especialista da plataforma BORAX.",
    "files_list": [],
    "mounted_at": None,
    "cover_color": "#2B2443"
}

class KnowledgeManager:
    def __init__(self, rag_engine: Optional[RAGEngine] = None, knpack_manager: Optional[KNPackManager] = None):
        self.rag_engine = rag_engine or RAGEngine()
        self.knpack_manager = knpack_manager or KNPackManager(self.rag_engine)
        self._active_cartridges: Dict[str, Dict[str, Any]] = {}
        self._refresh_default_vectors()

    def _refresh_default_vectors(self):
        """Update vector count for default table."""
        try:
            records = self.rag_engine.get_all_records(DEFAULT_TABLE)
            DEFAULT_CARTRIDGE["vectors_count"] = len(records)
        except Exception:
            pass

    def get_active_status(self) -> Dict[str, Any]:
        """Return combined status and list of currently active mounted cartridges."""
        self._refresh_default_vectors()
        mounted_list = list(self._active_cartridges.values())
        
        if not mounted_list:
            return {
                "mounted": False,
                "cartridges": [],
                "table_names": [DEFAULT_TABLE],
                "table_name": DEFAULT_TABLE,
                "system_prompt": DEFAULT_CARTRIDGE["system_prompt"],
                "total_vectors": DEFAULT_CARTRIDGE["vectors_count"],
                "name": DEFAULT_CARTRIDGE["name"],
                "type": "default",
                "files_list": []
            }

        table_names = [c["table_name"] for c in mounted_list]
        combined_prompts = " ".join([c["system_prompt"] for c in mounted_list])
        total_vectors = sum(c["vectors_count"] for c in mounted_list)
        all_files = []
        for c in mounted_list:
            all_files.extend(c.get("files_list", []))

        return {
            "mounted": True,
            "cartridges": mounted_list,
            "table_names": table_names,
            "table_name": table_names[0] if table_names else DEFAULT_TABLE,
            "system_prompt": combined_prompts,
            "total_vectors": total_vectors,
            "name": f"{len(mounted_list)} Cartucho(s) Ativo(s)",
            "type": "multi_dock",
            "files_list": all_files
        }

    def mount_media(self, file_path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Mount a .knpack file or document (.pdf, .txt, .csv, .docx) into LanceDB
        as an active cartridge in the Multi-Slot Dock.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        display_name = file_name or os.path.basename(file_path)
        ext = os.path.splitext(display_name)[1].lower()
        file_size = os.path.getsize(file_path)
        cart_id = str(uuid.uuid4())[:8]

        if ext == ".knpack":
            import_res = self.knpack_manager.import_knpack(file_path)
            manifest = import_res.get("manifest", {})
            table_name = import_res.get("table_name", DEFAULT_TABLE)
            chunks_imported = import_res.get("chunks_imported", 0)

            files_contained = [display_name]
            try:
                with zipfile.ZipFile(file_path, "r") as zipf:
                    if "manifest.json" in zipf.namelist():
                        m_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
                        if "files_contained" in m_data:
                            files_contained = m_data["files_contained"]
            except Exception:
                pass

            cartridge_data = {
                "id": cart_id,
                "mounted": True,
                "name": manifest.get("module_name", display_name.replace(".knpack", "")),
                "type": "knpack",
                "table_name": table_name,
                "vectors_count": chunks_imported,
                "size_bytes": file_size,
                "system_prompt": manifest.get("system_prompt", f"Você é especialista no pacote '{display_name}'."),
                "files_list": files_contained,
                "mounted_at": datetime.now().isoformat(),
                "cover_color": "#7C3AED"
            }
        elif ext in [".pdf", ".txt", ".csv", ".docx"]:
            clean_name = os.path.splitext(display_name)[0]
            table_name = f"cartridge_{clean_name.lower().replace(' ', '_')}_{cart_id}"
            
            res = self.rag_engine.process_file(file_path, table_name=table_name)
            if res.get("status") == "error":
                raise ValueError(res.get("message", "Erro ao processar arquivo para o leitor."))

            chunks_count = res.get("chunks_count", 0)

            cartridge_data = {
                "id": cart_id,
                "mounted": True,
                "name": clean_name.capitalize(),
                "type": "document",
                "table_name": table_name,
                "vectors_count": chunks_count,
                "size_bytes": file_size,
                "system_prompt": f"Você é um assistente especialista no documento '{display_name}'. Responda com base nele.",
                "files_list": [display_name],
                "mounted_at": datetime.now().isoformat(),
                "cover_color": "#06B6D4"
            }
        else:
            raise ValueError(f"Extensão de arquivo '{ext}' não suportada. Use .knpack, .pdf, .txt, .csv ou .docx.")

        self._active_cartridges[cart_id] = cartridge_data

        return {
            "status": "success",
            "message": f"Cartucho '{cartridge_data['name']}' encaixado com sucesso no leitor multi-dock!",
            "cartridge": cartridge_data,
            "active_status": self.get_active_status()
        }

    def eject_media(self, cartridge_id: Optional[str] = None) -> Dict[str, Any]:
        """Eject a specific cartridge by ID or eject all cartridges."""
        if cartridge_id and cartridge_id in self._active_cartridges:
            removed = self._active_cartridges.pop(cartridge_id)
            msg = f"Cartucho '{removed['name']}' ejetado do leitor."
        else:
            self._active_cartridges.clear()
            msg = "Todos os cartuchos foram ejetados do leitor BORAX."

        return {
            "status": "success",
            "message": msg,
            "active_status": self.get_active_status()
        }
