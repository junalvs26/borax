import os
import json
import zipfile
import tempfile
from datetime import datetime
from typing import List, Dict, Any

class PackService:
    def create_knpack(
        self,
        pack_name: str,
        module_prompt: str,
        records: List[Dict[str, Any]],
        output_dir: str
    ) -> str:
        """Create a compressed .knpack file containing knowledge base vectors & module system prompt."""
        timestamp = datetime.now().isoformat()
        pack_filename = f"{pack_name.lower().replace(' ', '_')}.knpack"
        pack_filepath = os.path.join(output_dir, pack_filename)

        manifest = {
            "pack_name": pack_name,
            "created_at": timestamp,
            "version": "1.0.0",
            "chunks_count": len(records)
        }

        # Create temporary zip structure
        with zipfile.ZipFile(pack_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Manifest
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            # 2. Prompt instructions
            zipf.writestr("prompt.txt", module_prompt)
            # 3. Serialized vector & text records
            zipf.writestr("data.json", json.dumps(records, indent=2, ensure_ascii=False))

        return pack_filepath
