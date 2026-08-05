import os
import re
import sys
import glob
import threading
from typing import Generator, List, Dict, Any, Optional

BORAX_MODELS_DIR = os.path.expanduser("~/.borax/models")

DEFAULT_SCIENTIFIC_SYSTEM_PROMPT = (
    "Você é um Orientador Acadêmico Sênior e Redator de Elite da Plataforma BORAX.\n"
    "Seu papel é orientar e auxiliar o usuário no desenvolvimento de TCCs, artigos científicos, pesquisas e relatórios de forma natural, consultiva e em diálogo contínuo.\n\n"
    "DIRETRIZES CONVERSACIONAIS:\n"
    "1. Sondagem e Diagnóstico Inicial (DINÂMICO E NÃO ENGESSADO):\n"
    "   - Aja como um verdadeiro orientador de doutorado. Analise o tema proposto e faça perguntas inteligentes, contextualizadas e fluídas que ajudem a delimitar a problematização, a metodologia e o referencial teórico.\n"
    "2. Construção do Sumário/Estrutura:\n"
    "   - À medida que o usuário alinha o tema, apresente primeiro a estrutura/sumário preliminar dividida em capítulos formais.\n"
    "3. Fundamentação com Pesquisa Web:\n"
    "   - Utilize dados reais, normas ABNT e referências pesquisadas na web para enriquecer a discussão. Ao citar dados web, inclua no final a seção '📌 **Fontes e Referências Consultadas:**'.\n"
    "4. Compilação Final:\n"
    "   - Quando o usuário aprovar o sumário ou pedir para compilar o arquivo final (.docx / .pdf), redija o texto completo estruturado em normas ABNT rigorosas.\n\n"
    "REGRA DE RESPOSTA LIMPA: NUNCA repita ou imprima na sua resposta cabeçalhos ou tags internas como '[HISTÓRICO...]', '[CONTEXTO...]' ou '[MENSAGEM...]'. Responda diretamente ao usuário."
)

def get_models_dir() -> str:
    """Return local storage path for BORAX GGUF models (~/.borax/models/)."""
    os.makedirs(BORAX_MODELS_DIR, exist_ok=True)
    return BORAX_MODELS_DIR

def download_model_if_missing(
    repo_id: str = "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    filename: str = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
) -> str:
    """Download ultra lightweight GGUF model file (~398 MB) from HuggingFace directly to ~/.borax/models/."""
    models_dir = get_models_dir()
    target_path = os.path.join(models_dir, filename)
    
    if os.path.exists(target_path) and os.path.getsize(target_path) > 100000:
        print(f"[BORAX LLM] Modelo '{filename}' já existe localmente em: {target_path}")
        return target_path

    print(f"[BORAX LLM] Baixando modelo ultra leve '{filename}' do HuggingFace ({repo_id})...")
    from huggingface_hub import hf_hub_download
    
    downloaded_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=models_dir,
        local_dir_use_symlinks=False
    )
    print(f"[BORAX LLM] Download concluído! Modelo salvo em: {downloaded_path}")
    return downloaded_path

def list_local_models() -> List[Dict[str, Any]]:
    """List all available .gguf model files in ~/.borax/models/."""
    models_dir = get_models_dir()
    pattern = os.path.join(models_dir, "*.gguf")
    files = glob.glob(pattern)
    
    result = []
    for f in files:
        b_name = os.path.basename(f)
        size = os.path.getsize(f)
        result.append({
            "name": b_name,
            "model": b_name,
            "path": f,
            "size": size
        })
    return result

class BoraxLLM:
    def __init__(
        self,
        model_name_or_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_threads: int = 2,
        n_gpu_layers: int = 0
    ):
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers = n_gpu_layers
        self.model_path = None
        self._llm = None
        self.current_model_name = ""
        self._lock = threading.Lock()

        if model_name_or_path:
            if os.path.exists(model_name_or_path):
                self.model_path = model_name_or_path
            else:
                target = os.path.join(get_models_dir(), model_name_or_path)
                if os.path.exists(target):
                    self.model_path = target
                else:
                    self.model_path = download_model_if_missing()
        else:
            local_models = list_local_models()
            if local_models:
                self.model_path = local_models[0]["path"]
            else:
                self.model_path = download_model_if_missing()

        self.current_model_name = os.path.basename(self.model_path)
        self._load_llama()

    def _load_llama(self):
        """Initialize llama_cpp.Llama instance."""
        try:
            from llama_cpp import Llama
            print(f"[BORAX LLM] Inicializando Llama C++ com o modelo: {self.current_model_name}")
            print(f"[BORAX LLM] Parâmetros: n_ctx={self.n_ctx}, n_threads={self.n_threads}, n_gpu_layers={self.n_gpu_layers}")
            
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            print(f"[BORAX LLM] Engine de inferência C++ embutida inicializada com sucesso!")
        except Exception as e:
            print(f"[BORAX LLM] Erro ao carregar Llama C++: {e}")
            raise e

    def generate_stream(
        self,
        prompt: str = "",
        system_prompt: str = DEFAULT_SCIENTIFIC_SYSTEM_PROMPT,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """Generate response tokens in streaming directly from C++ memory (no HTTP required)."""
        if not self._llm or self.n_ctx < 4096:
            self.n_ctx = 4096
            self._load_llama()

        payload_messages = []
        eff_system_prompt = system_prompt or DEFAULT_SCIENTIFIC_SYSTEM_PROMPT
        payload_messages.append({"role": "system", "content": eff_system_prompt})

        user_or_chat_msgs = []
        if messages:
            user_or_chat_msgs.extend(messages)
        elif prompt:
            user_or_chat_msgs.append({"role": "user", "content": prompt})

        # Sliding window: keep max 16 most recent messages if history is very long
        if len(user_or_chat_msgs) > 16:
            user_or_chat_msgs = user_or_chat_msgs[-16:]

        payload_messages.extend(user_or_chat_msgs)

        try:
            effective_max_tokens = min(max_tokens, max(256, self.n_ctx - 1000))
            with self._lock:
                response = self._llm.create_chat_completion(
                    messages=payload_messages,
                    stream=True,
                    max_tokens=effective_max_tokens,
                    temperature=0.2,
                    top_p=0.9,
                    repeat_penalty=1.15
                )
                for chunk in response:
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
        except Exception as e:
            print(f"[BORAX LLM] Erro durante a geração de streaming C++: {e}")
            yield f"[Erro na inferência local C++: {str(e)}]"

    def generate_text(
        self,
        prompt: str = "",
        system_prompt: str = DEFAULT_SCIENTIFIC_SYSTEM_PROMPT,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4096
    ) -> str:
        """Generate non-streaming text response directly from C++ memory."""
        chunks = list(self.generate_stream(prompt=prompt, system_prompt=system_prompt, messages=messages, max_tokens=max_tokens))
        return "".join(chunks)

    def generate_long_text(
        self,
        prompt: str = "",
        system_prompt: str = DEFAULT_SCIENTIFIC_SYSTEM_PROMPT,
        messages: Optional[List[Dict[str, str]]] = None,
        max_continues: int = 3
    ) -> str:
        """Generate long text with automatic continuation if generation hits token limit."""
        current_messages = []
        eff_system_prompt = system_prompt or DEFAULT_SCIENTIFIC_SYSTEM_PROMPT
        current_messages.append({"role": "system", "content": eff_system_prompt})

        if messages:
            current_messages.extend(messages)
        elif prompt:
            current_messages.append({"role": "user", "content": prompt})

        full_text = ""
        for iteration in range(max_continues + 1):
            chunk_text = self.generate_text(system_prompt="", messages=current_messages, max_tokens=4096)
            full_text += chunk_text

            trimmed = chunk_text.strip()
            if iteration < max_continues and trimmed and not trimmed.endswith((".", "!", "?", "```", "}", "]")):
                print(f"[BORAX LLM] Geração extensa atingiu limite parcial. Continuando automaticamente (Loop {iteration + 1})...")
                current_messages.append({"role": "assistant", "content": chunk_text})
                current_messages.append({"role": "user", "content": "Continue exatamente de onde parou, sem repetir o texto já escrito e mantendo o maior nível de detalhamento possível."})
            else:
                break

        return full_text

