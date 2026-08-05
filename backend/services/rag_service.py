import os
import uuid
from typing import List, Dict, Any
from pypdf import PdfReader
import lancedb
from sentence_transformers import SentenceTransformer

# Store vector database in backend/lancedb_data
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lancedb_data")
TABLE_NAME = "knowledge_base"

class RAGService:
    def __init__(self):
        os.makedirs(DB_PATH, exist_ok=True)
        self.db = lancedb.connect(DB_PATH)
        # Using a fast, lightweight sentence transformer model for local embeddings
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._ensure_table()

    def _ensure_table(self):
        """Ensure the LanceDB table exists."""
        if TABLE_NAME not in self.db.table_names():
            # Initialize table schema with dummy record if empty
            sample_emb = self.embedder.encode("initial sample text").tolist()
            dummy_data = [{
                "id": "init",
                "text": "Initialization text",
                "filename": "system",
                "vector": sample_emb
            }]
            self.table = self.db.create_table(TABLE_NAME, data=dummy_data)
        else:
            self.table = self.db.open_table(TABLE_NAME)

    def extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text from TXT or PDF file."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            extracted = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted.append(text)
            return "\n".join(extracted)
        else:
            raise ValueError(f"Extensão não suportada: {ext}")

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Simple sliding window text chunker."""
        words = text.split()
        if not words:
            return []
        
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += (chunk_size - overlap)
        return chunks

    def ingest_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process file, extract text, compute embeddings, and store in LanceDB."""
        full_text = self.extract_text_from_file(file_path, filename)
        chunks = self.chunk_text(full_text)

        if not chunks:
            return {"status": "error", "message": "Nenhum texto extraído do arquivo."}

        embeddings = self.embedder.encode(chunks)

        records = []
        for chunk, emb in zip(chunks, embeddings):
            records.append({
                "id": str(uuid.uuid4()),
                "text": chunk,
                "filename": filename,
                "vector": emb.tolist()
            })

        self.table.add(records)
        return {
            "status": "success",
            "filename": filename,
            "chunks_count": len(records),
            "message": f"Arquivo '{filename}' processado e {len(records)} chunks vetorizados."
        }

    def search_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search top-k most similar text chunks for a query."""
        if self.table is None:
            return []

        query_emb = self.embedder.encode(query).tolist()
        results = self.table.search(query_emb).limit(top_k).to_list()
        
        # Filter out the init record if matched
        filtered = [r for r in results if r.get("id") != "init"]
        return filtered

    def get_all_records() -> List[Dict[str, Any]]:
        """Get all stored vectors/chunks for knpack export."""
        if self.table is None:
            return []
        records = self.table.search().limit(10000).to_list()
        return [r for r in records if r.get("id") != "init"]
