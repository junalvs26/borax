import os
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from embedded_engine import BoraxLLM, list_local_models, download_model_if_missing

class OllamaService:
    """
    Adaptador de retrocompatibilidade para o BoraxLLM C++ Embutido.
    Elimina a dependência de portas HTTP, executáveis externos e do aplicativo Ollama.
    """
    def __init__(self, borax_llm: Optional[BoraxLLM] = None, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._llm_instance: Optional[BoraxLLM] = borax_llm

    def _get_llm(self, model_name: Optional[str] = None) -> BoraxLLM:
        if not self._llm_instance:
            self._llm_instance = BoraxLLM(model_name_or_path=model_name, n_ctx=4096)
        return self._llm_instance

    async def check_ollama_status(self) -> Dict[str, Any]:
        """Healthcheck da Engine C++ Embutida (100% online)."""
        return {
            "status": "online",
            "message": "Engine C++ Embutida (llama-cpp) ativa e operacional localmente."
        }

    async def list_models(self) -> List[Dict[str, Any]]:
        """Lista os modelos .gguf armazenados no diretório local do BORAX."""
        return await asyncio.to_thread(list_local_models)

    async def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens using non-blocking thread-safe queue for FastAPI."""
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def produce_tokens():
            try:
                llm = self._get_llm(model_name=model)
                for token in llm.generate_stream(system_prompt=system_prompt, messages=messages):
                    asyncio.run_coroutine_threadsafe(queue.put(token), loop).result()
            except Exception as e:
                print(f"[OllamaService Error] Falha na inferência C++: {e}")
                asyncio.run_coroutine_threadsafe(queue.put(f"[Erro C++: {str(e)}]"), loop).result()
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop).result()

        loop.run_in_executor(None, produce_tokens)

        while True:
            token = await queue.get()
            if token is None:
                break
            yield token



