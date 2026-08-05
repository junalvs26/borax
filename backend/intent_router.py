import re
import os
from enum import Enum
from typing import Dict, Any, Optional, List

class IntentType(str, Enum):
    CHAT_ONLY = "CHAT_ONLY"
    TRANSCRIBE_MEDIA = "TRANSCRIBE_MEDIA"
    GENERATE_DOCUMENT = "GENERATE_DOCUMENT"
    ANALYZE_DATA = "ANALYZE_DATA"
    MOUNT_CARTRIDGE = "MOUNT_CARTRIDGE"
    INGEST_FILE = "INGEST_FILE"
    SAVE_SESSION = "SAVE_SESSION"

# Keyword patterns for Layer 2
DOC_GEN_KEYWORDS = [
    r"gerar\s+docx", r"gerar\s+word", r"exportar\s+word", r"salvar\s+word", r"baixar\s+em\s+word",
    r"gerar\s+pdf", r"salvar\s+pdf", r"exportar\s+pdf", r"exportar\s+arquivo",
    r"crie\s+um\s+arquivo", r"gerar\s+um\s+arquivo", r"gerar\s+arquivo", r"gerar\s+documento",
    r"salvar\s+em\s+arquivo", r"baixar\s+arquivo", r"crie\s+um\s+doc",
    r"gere\s+o?\s*projeto", r"gerar\s+o?\s*projeto", r"crie\s+o?\s*projeto", r"criar\s+o?\s*projeto",
    r"gere\s+o?\s*trabalho", r"gerar\s+o?\s*trabalho", r"crie\s+o?\s*relatorio", r"gerar\s+relatorio",
    r"gerar\s+planilha", r"crie\s+planilha", r"monte\s+a?\s*planilha", r"gere\s+a?\s*planilha"
]

AUDIO_VIDEO_EXTS = {".mp3", ".wav", ".mp4", ".m4a", ".webm", ".ogg", ".flac", ".mkv", ".avi", ".mov"}
DATA_FILE_EXTS = {".csv", ".xlsx", ".xls", ".parquet"}
DOC_FILE_EXTS = {".pdf", ".txt", ".docx"}

YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

def detect_intent(
    message: str = "",
    file_name: Optional[str] = None,
    active_power_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    3-Layer Intent Classification:
    Layer 1: Manual Override (@/slash trigger or active_power_override).
    Layer 2: Deterministic Rules (File extensions, YouTube URLs, Export keywords).
    Layer 3: Conversational Default (CHAT_ONLY).
    """
    clean_msg = (message or "").strip().lower()
    override = (active_power_override or "").strip().lower()

    # Layer 1: Manual / Override Trigger
    if override or clean_msg.startswith(("@", "/")):
        trigger = override or clean_msg.split()[0]
        if trigger in ["@criar-base", "/criar-base", "@montar-cartucho", "/montar-cartucho"]:
            return {"intent": IntentType.MOUNT_CARTRIDGE, "layer": 1, "trigger": trigger}
        elif trigger in ["@ingestao", "/ingestao", "@ingest", "/ingest"]:
            return {"intent": IntentType.INGEST_FILE, "layer": 1, "trigger": trigger}
        elif trigger in ["@transcrever", "/transcrever", "@whisper", "/whisper"]:
            return {"intent": IntentType.TRANSCRIBE_MEDIA, "layer": 1, "trigger": trigger}
        elif trigger in ["@analisar-dados", "/analisar-dados", "@sql", "/sql", "@duckdb", "/duckdb"]:
            return {"intent": IntentType.ANALYZE_DATA, "layer": 1, "trigger": trigger}
        elif trigger in ["@gerar-documento", "/gerar-documento", "@exportar", "/exportar"]:
            return {"intent": IntentType.GENERATE_DOCUMENT, "layer": 1, "trigger": trigger}
        elif trigger in ["@salvar", "/salvar"]:
            return {"intent": IntentType.SAVE_SESSION, "layer": 1, "trigger": trigger}

    # Layer 2: Deterministic Rules based on Attachments & Keywords
    if file_name:
        ext = os.path.splitext(file_name)[1].lower()
        if ext == ".knpack":
            return {"intent": IntentType.MOUNT_CARTRIDGE, "layer": 2, "reason": "Extensão .knpack detectada"}
        elif ext in AUDIO_VIDEO_EXTS:
            return {"intent": IntentType.TRANSCRIBE_MEDIA, "layer": 2, "reason": "Arquivo de áudio/vídeo detectado"}
        elif ext in DATA_FILE_EXTS:
            return {"intent": IntentType.ANALYZE_DATA, "layer": 2, "reason": "Planilha/Arquivo de dados detectado"}
        elif ext in DOC_FILE_EXTS:
            return {"intent": IntentType.INGEST_FILE, "layer": 2, "reason": "Documento para ingestão detectado"}

    # YouTube URL check
    if re.search(YOUTUBE_REGEX, clean_msg):
        return {"intent": IntentType.TRANSCRIBE_MEDIA, "layer": 2, "reason": "URL do YouTube detectada"}

    # Keyword check for document generation
    for pattern in DOC_GEN_KEYWORDS:
        if re.search(pattern, clean_msg):
            return {"intent": IntentType.GENERATE_DOCUMENT, "layer": 2, "reason": f"Palavra-chave '{pattern}' detectada"}

    # Layer 3: Conversational Default
    return {
        "intent": IntentType.CHAT_ONLY,
        "layer": 3,
        "reason": "Pergunta ou diálogo comum (CHAT_ONLY)"
    }
