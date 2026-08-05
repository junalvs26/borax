import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

BORAX_HISTORY_DIR = os.path.expanduser("~/.borax/history")
SESSIONS_FILE = os.path.join(BORAX_HISTORY_DIR, "sessions.json")

def _ensure_history_dir():
    os.makedirs(BORAX_HISTORY_DIR, exist_ok=True)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

class ChatHistoryManager:
    def __init__(self):
        _ensure_history_dir()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Return list of saved chat session metadata."""
        _ensure_history_dir()
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions = json.load(f)
                return sorted(sessions, key=lambda s: s.get("updated_at", ""), reverse=True)
        except Exception as e:
            print(f"[ChatHistoryManager] Erro ao carregar sessões: {e}")
            return []

    def save_session(
        self,
        title: str,
        messages: List[Dict[str, Any]],
        cartridges: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a chat session in local storage."""
        _ensure_history_dir()
        sessions = self.list_sessions()
        
        now = datetime.now().isoformat()
        sid = session_id or str(uuid.uuid4())[:8]

        session_obj = {
            "id": sid,
            "title": title or "Nova Conversa BORAX",
            "messages": messages,
            "cartridges": cartridges or [],
            "message_count": len(messages),
            "updated_at": now
        }

        existing_index = next((i for i, s in enumerate(sessions) if s["id"] == sid), None)
        if existing_index is not None:
            sessions[existing_index] = session_obj
        else:
            session_obj["created_at"] = now
            sessions.insert(0, session_obj)

        try:
            with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            return {"status": "success", "session": session_obj}
        except Exception as e:
            print(f"[ChatHistoryManager] Erro ao salvar sessão: {e}")
            return {"status": "error", "message": str(e)}

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full chat session object by ID."""
        sessions = self.list_sessions()
        return next((s for s in sessions if s["id"] == session_id), None)

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a chat session by ID."""
        _ensure_history_dir()
        sessions = self.list_sessions()
        filtered = [s for s in sessions if s["id"] != session_id]

        try:
            with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)
            return {"status": "success", "message": f"Sessão '{session_id}' excluída com sucesso."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def get_sliding_window_context(messages: List[Dict[str, Any]], max_turns: int = 10) -> List[Dict[str, Any]]:
        """Return the last max_turns (20 messages max) for floating sliding window memory."""
        if not messages:
            return []
        max_msgs = max_turns * 2
        return messages[-max_msgs:] if len(messages) > max_msgs else messages

    @classmethod
    def build_consolidated_prompt(
        cls,
        query: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        rag_context: str = "",
        cartridges: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Consolidate [HISTÓRICO RECENTE DA CONVERSA] + [CONTEXTO DOS CDS ATIVOS] + [MENSAGEM ATUAL DO USUÁRIO].
        """
        prompt_parts = []

        # 1. Sliding Window History (Last 10 turns)
        sliding_msgs = cls.get_sliding_window_context(messages or [], max_turns=10)
        if sliding_msgs:
            history_lines = []
            for msg in sliding_msgs:
                role = "USUÁRIO" if msg.get("role") == "user" else "ASSISTENTE"
                content = (msg.get("content") or "").strip()
                if content and not content.startswith("⚠️"):
                    history_lines.append(f"{role}: {content[:500]}")
            if history_lines:
                prompt_parts.append("[HISTÓRICO RECENTE DA CONVERSA (ÚLTIMOS TURNOS)]:\n" + "\n".join(history_lines))

        # 2. Context from active CDs / RAG
        if rag_context and rag_context.strip():
            prompt_parts.append(f"[CONTEXTO DOS CDS / BASES ATIVAS]:\n{rag_context.strip()}")

        # 3. Current User Query
        prompt_parts.append(f"[MENSAGEM ATUAL DO USUÁRIO]:\n{query.strip()}")

        return "\n\n---\n\n".join(prompt_parts)

