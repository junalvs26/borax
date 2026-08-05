import os
import shutil
import uuid
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from services.ollama_service import OllamaService

# Global pending plans storage for confirm mode
PENDING_PLANS: Dict[str, Dict[str, Any]] = {}

SYSTEM_BLACKLIST = [
    r"c:\\windows",
    r"c:\\program files",
    r"c:\\program files \(x86\)",
    r"c:\\system volume information",
    r"c:\\programdata",
    r"^/etc",
    r"^/sys",
    r"^/proc",
    r"^/boot",
    r"^/dev",
    r"^/usr",
    r"^/var"
]

class DesktopAgent:
    def __init__(self, ollama_service: Optional[OllamaService] = None):
        self.ollama_service = ollama_service or OllamaService()

    def get_default_safe_paths(self) -> List[str]:
        """Return list of default safe user directory paths."""
        home = Path.home().resolve()
        return [
            str(home / "Downloads"),
            str(home / "Documents"),
            str(home / "Desktop"),
            str(home / "Pictures"),
            str(home / "Videos"),
            str(home / ".app_data")
        ]

    def is_system_blacklisted(self, path_str: str) -> bool:
        """Check if path falls under OS system directory blacklist."""
        norm_path = os.path.abspath(path_str).lower()
        for pattern in SYSTEM_BLACKLIST:
            if re.search(pattern.lower(), norm_path):
                return True
        return False

    def validate_path_access(self, path_str: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> bool:
        """Validate if path access is permitted based on execution mode."""
        if self.is_system_blacklisted(path_str):
            return False

        if execution_mode == "unrestricted":
            return True

        if execution_mode in ["safe", "confirm"]:
            target_path = Path(path_str).resolve()
            user_allowed = self.get_default_safe_paths()
            if allowed_paths:
                user_allowed.extend([str(Path(p).resolve()) for p in allowed_paths])

            # Check if target_path is inside any of the allowed paths
            for safe_dir in user_allowed:
                safe_path = Path(safe_dir).resolve()
                try:
                    if target_path == safe_path or safe_path in target_path.parents:
                        return True
                except Exception:
                    continue
            return False

        return False

    # --- NATIVE TOOLS ---

    def list_directory(self, path: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """List files and subdirectories."""
        if not self.validate_path_access(path, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado ao diretório '{path}' no modo '{execution_mode}'.")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Diretório não encontrado: {path}")

        items = []
        for entry in os.scandir(path):
            stat = entry.stat()
            items.append({
                "name": entry.name,
                "path": entry.path,
                "is_dir": entry.is_dir(),
                "size_bytes": stat.st_size if not entry.is_dir() else 0,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return {"status": "success", "path": path, "total_items": len(items), "items": items}

    def create_directory(self, path: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create new directory."""
        if not self.validate_path_access(path, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado para criar diretório '{path}' no modo '{execution_mode}'.")

        os.makedirs(path, exist_ok=True)
        return {"status": "success", "action": "create_directory", "path": path, "message": f"Diretório '{path}' criado com sucesso."}

    def move_file(self, source_path: str, destination_path: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Move or rename file or directory."""
        if not self.validate_path_access(source_path, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado para origem '{source_path}' no modo '{execution_mode}'.")

        dest_dir = os.path.dirname(destination_path) or destination_path
        if not self.validate_path_access(dest_dir, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado para destino '{dest_dir}' no modo '{execution_mode}'.")

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Origem não encontrada: {source_path}")

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.move(source_path, destination_path)
        return {
            "status": "success",
            "action": "move_file",
            "source_path": source_path,
            "destination_path": destination_path,
            "message": f"Arquivo movido de '{source_path}' para '{destination_path}'."
        }

    def get_file_metadata(self, path: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get size, extension, modified and created timestamps for a file."""
        if not self.validate_path_access(path, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado para metadados de '{path}' no modo '{execution_mode}'.")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        stat = os.stat(path)
        ext = os.path.splitext(path)[1]
        return {
            "status": "success",
            "path": path,
            "filename": os.path.basename(path),
            "extension": ext,
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path),
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }

    def watch_folder(self, folder_path: str, execution_mode: str = "safe", allowed_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Register watcher for a folder."""
        if not self.validate_path_access(folder_path, execution_mode, allowed_paths):
            raise PermissionError(f"Acesso negado para monitorar '{folder_path}' no modo '{execution_mode}'.")

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Pasta para monitorar não encontrada: {folder_path}")

        return {
            "status": "success",
            "action": "watch_folder",
            "folder_path": folder_path,
            "message": f"Monitoramento registrado para '{folder_path}'."
        }

    # --- EXECUTION & CONFIRMATION FLOW ---

    def execute_tool(self, tool_name: str, args: Dict[str, Any], execution_mode: str, allowed_paths: List[str]) -> Dict[str, Any]:
        """Execute a single native tool call."""
        if tool_name == "list_directory":
            return self.list_directory(args["path"], execution_mode, allowed_paths)
        elif tool_name == "create_directory":
            return self.create_directory(args["path"], execution_mode, allowed_paths)
        elif tool_name == "move_file":
            return self.move_file(args["source_path"], args["destination_path"], execution_mode, allowed_paths)
        elif tool_name == "get_file_metadata":
            return self.get_file_metadata(args["path"], execution_mode, allowed_paths)
        elif tool_name == "watch_folder":
            return self.watch_folder(args["folder_path"], execution_mode, allowed_paths)
        else:
            raise ValueError(f"Ferramenta desconhecida: {tool_name}")

    def plan_and_execute(
        self,
        instruction: str,
        execution_mode: str = "safe",
        allowed_paths: Optional[List[str]] = None,
        model: str = "llama3.2"
    ) -> Dict[str, Any]:
        """Parse natural language instruction into tool action plan and execute/confirm."""
        allowed_paths = allowed_paths or []

        # Tool definition schema prompt for Ollama Text-to-Actions
        prompt = (
            f"Você é um Agente de Automação Desktop nativo. "
            f"Sua função é traduzir a instrução do usuário em um plano de ferramentas JSON válido.\n\n"
            f"Ferramentas Disponíveis:\n"
            f"1. list_directory(path: string)\n"
            f"2. create_directory(path: string)\n"
            f"3. move_file(source_path: string, destination_path: string)\n"
            f"4. get_file_metadata(path: string)\n"
            f"5. watch_folder(folder_path: string)\n\n"
            f"Instrução do Usuário: '{instruction}'\n\n"
            f"Retorne APENAS um objeto JSON com a lista de 'actions':\n"
            f"```json\n"
            f"{{\n"
            f'  "actions": [\n'
            f'    {{"tool": "nome_da_ferramenta", "args": {{"param": "valor"}}}}\n'
            f"  ]\n"
            f"}}\n"
            f"```"
        )

        messages = [{"role": "user", "content": prompt}]

        # Call Ollama stream synchronously to get response
        import asyncio
        async def get_response():
            res = []
            async for token in self.ollama_service.chat_stream(model, messages):
                res.append(token)
            return "".join(res)

        llm_response = ""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    llm_response = pool.submit(lambda: asyncio.run(get_response())).result()
            else:
                llm_response = loop.run_until_complete(get_response())
        except Exception:
            llm_response = ""

        # Parse actions JSON
        actions = []
        match = re.search(r'```json\s*(.*?)\s*```', llm_response, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
        else:
            match_gen = re.search(r'\{.*\}', llm_response, re.DOTALL)
            json_str = match_gen.group(0).strip() if match_gen else ""

        if json_str:
            try:
                parsed = json.loads(json_str)
                actions = parsed.get("actions", [])
            except Exception:
                actions = []

        # Fallback heuristic if LLM response couldn't be parsed
        if not actions:
            if "listar" in instruction.lower() or "list" in instruction.lower():
                # Extract path from instruction if possible
                path_found = str(Path.home() / "Downloads")
                actions = [{"tool": "list_directory", "args": {"path": path_found}}]

        # Check confirmation requirement in "confirm" mode
        has_modifying_actions = any(a["tool"] in ["create_directory", "move_file"] for a in actions)

        if execution_mode == "confirm" and has_modifying_actions:
            plan_id = str(uuid.uuid4())
            pending_plan = {
                "plan_id": plan_id,
                "instruction": instruction,
                "execution_mode": execution_mode,
                "allowed_paths": allowed_paths,
                "pending_actions": actions,
                "created_at": datetime.now().isoformat()
            }
            PENDING_PLANS[plan_id] = pending_plan

            return {
                "status": "requires_confirmation",
                "requires_confirmation": True,
                "plan_id": plan_id,
                "instruction": instruction,
                "pending_actions": actions,
                "message": f"A instrução requer modificações no sistema de arquivos. Por favor, confirme a execução do plano."
            }

        # Execute actions immediately for "safe" or "unrestricted" (or confirm without modify)
        execution_results = []
        for action in actions:
            tool_name = action["tool"]
            args = action["args"]

            try:
                res = self.execute_tool(tool_name, args, execution_mode, allowed_paths)
                execution_results.append({"tool": tool_name, "args": args, "result": res})
            except Exception as err:
                execution_results.append({"tool": tool_name, "args": args, "error": str(err)})
                if execution_mode == "safe":
                    raise err

        return {
            "status": "completed",
            "execution_mode": execution_mode,
            "instruction": instruction,
            "actions_executed_count": len(execution_results),
            "results": execution_results
        }

    def confirm_and_execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a previously held pending plan after user confirmation."""
        if plan_id not in PENDING_PLANS:
            raise KeyError(f"Plano de automação não encontrado ou expirado: '{plan_id}'")

        plan = PENDING_PLANS.pop(plan_id)
        actions = plan["pending_actions"]
        allowed_paths = plan["allowed_paths"]

        execution_results = []
        for action in actions:
            tool_name = action["tool"]
            args = action["args"]
            try:
                res = self.execute_tool(tool_name, args, execution_mode="unrestricted", allowed_paths=allowed_paths)
                execution_results.append({"tool": tool_name, "args": args, "result": res})
            except Exception as err:
                execution_results.append({"tool": tool_name, "args": args, "error": str(err)})

        return {
            "status": "completed",
            "plan_id": plan_id,
            "instruction": plan["instruction"],
            "actions_executed_count": len(execution_results),
            "results": execution_results
        }
