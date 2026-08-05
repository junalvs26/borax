import os
import sys
import shutil
import tempfile
import asyncio
from typing import List, Optional, Dict, Any

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from services.ollama_service import OllamaService
from rag_engine import RAGEngine, DEFAULT_TABLE
from knpack_manager import KNPackManager
from knowledge_manager import KnowledgeManager
from media_processor import MediaProcessor
from data_analyst import DataAnalyst
from desktop_agent import DesktopAgent

from chat_history_manager import ChatHistoryManager

from chat_power_executor import ChatPowerExecutor, generate_downloadable_file, BORAX_EXPORTS_DIR
from document_wizard_engine import DocumentWizardEngine

app = FastAPI(
    title="Plataforma de IA Local Modular - Backend",
    description="Engine RAG com LanceDB, Faster-Whisper, DuckDB Analista e Agente Desktop Autônomo com Permissões",
    version="1.6.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from embedded_engine import BoraxLLM, list_local_models

# Core Instances
borax_llm = BoraxLLM()
ollama_service = OllamaService(borax_llm=borax_llm)
rag_engine = RAGEngine()
knpack_manager = KNPackManager(rag_engine)
knowledge_manager = KnowledgeManager(rag_engine=rag_engine, knpack_manager=knpack_manager)
media_processor = MediaProcessor(rag_engine=rag_engine)
data_analyst = DataAnalyst(ollama_service=ollama_service)
desktop_agent = DesktopAgent(ollama_service=ollama_service)
history_manager = ChatHistoryManager()
power_executor = ChatPowerExecutor(
    rag_engine=rag_engine,
    knowledge_manager=knowledge_manager,
    media_processor=media_processor,
    data_analyst=data_analyst,
    ollama_service=borax_llm
)
doc_wizard = DocumentWizardEngine(ollama_service=borax_llm, rag_engine=rag_engine)

class SaveSessionRequest(BaseModel):
    id: Optional[str] = None
    title: str
    messages: List[Dict[str, Any]]
    cartridges: Optional[List[Dict[str, Any]]] = []

class GenerateFileRequest(BaseModel):
    content: str
    file_format: Optional[str] = "docx"
    filename: Optional[str] = None

class InitiateWizardRequest(BaseModel):
    prompt: str

class GenerateCustomDocRequest(BaseModel):
    prompt: str
    preferences: Dict[str, Any]
    use_rag: Optional[bool] = True

# Pydantic Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    model: str
    table_name: Optional[str] = DEFAULT_TABLE
    use_rag: Optional[bool] = True
    top_k: Optional[int] = 3
    messages: Optional[List[ChatMessage]] = []

class ExportPackRequest(BaseModel):
    module_name: str
    system_prompt: str
    table_name: Optional[str] = DEFAULT_TABLE
    description: Optional[str] = ""

class AgentExecuteRequest(BaseModel):
    instruction: str
    execution_mode: Optional[str] = "safe" # "safe", "confirm", "unrestricted"
    allowed_paths: Optional[List[str]] = []
    model: Optional[str] = "qwen2.5-0.5b-instruct-q4_k_m.gguf"

class AgentConfirmRequest(BaseModel):
    plan_id: str

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Backend de IA Local Modular (Tradutor + Mídia + Analista + Agente Desktop)",
        "lancedb_path": str(rag_engine.db_dir)
    }

@app.get("/api/ollama/status")
async def ollama_status_endpoint():
    """Healthcheck do serviço Ollama na porta 11434."""
    return await ollama_service.check_ollama_status()

@app.get("/api/models")
async def get_models():
    """Fetch installed local .gguf models for BoraxLLM C++ Engine."""
    models = await ollama_service.list_models()
    return {"models": models}

@app.post("/api/ingest")
async def ingest_endpoint(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    table_name: Optional[str] = Form(DEFAULT_TABLE)
):
    """Ingest .pdf, .txt, or .docx file into LanceDB vector database."""
    target_path = None
    cleanup_temp = False

    if file:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".pdf", ".txt", ".docx"]:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão '{ext}' não suportada. Use .pdf, .txt ou .docx."
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            target_path = tmp.name
            cleanup_temp = True
    elif file_path:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Caminho local não encontrado: {file_path}")
        target_path = file_path
    else:
        raise HTTPException(status_code=400, detail="Forneça um arquivo enviado ou um caminho local (file_path).")

    try:
        result = rag_engine.process_file(target_path, table_name=table_name)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    finally:
        if cleanup_temp and target_path and os.path.exists(target_path):
            os.remove(target_path)

from web_search_agent import WebSearchAgent
from academic_flow import AcademicFlowManager
from academic_writer_engine import AcademicWriterEngine
from embedded_engine import DEFAULT_SCIENTIFIC_SYSTEM_PROMPT

web_search_agent = WebSearchAgent()
academic_writer_engine = AcademicWriterEngine()

@app.post("/api/query")
async def query_endpoint(request: QueryRequest):
    """Query RAG context from multi-base LanceDB tables + Autonomous Web Search and stream chat response via BoraxLLM."""
    active_cartridge = knowledge_manager.get_active_status()
    system_prompt = active_cartridge.get("system_prompt") or DEFAULT_SCIENTIFIC_SYSTEM_PROMPT
    
    # 1. Override system prompt if user is in Academic / TCC Consultation Flow
    is_academic = AcademicFlowManager.is_academic_request(request.query)
    if is_academic:
        system_prompt = AcademicFlowManager.get_academic_system_prompt(request.query)

    target_tables = active_cartridge.get("table_names") or [request.table_name or DEFAULT_TABLE]
    
    rag_context_text = ""
    active_cds_has_answer = False
    if request.use_rag:
        contexts = await asyncio.to_thread(
            rag_engine.query_context,
            query=request.query,
            table_name=target_tables,
            top_k=request.top_k or 3,
            min_score=0.45
        )
        if contexts:
            active_cds_has_answer = True
            rag_context_text = "\n---\n".join([f"[{c.get('source_table', 'base')} - Score: {c.get('similarity_score', 0)}]: {c['text'][:400]}" for c in contexts])

    payload_messages = [msg.model_dump() for msg in request.messages]

    # 2. Check if user requested document compilation (.docx)
    if is_academic and AcademicFlowManager.is_ready_to_compile(request.query, payload_messages):
        compilation_res = await asyncio.to_thread(
            academic_writer_engine.process_academic_turn,
            query=request.query,
            messages=payload_messages,
            rag_context=rag_context_text,
            force_compile=True
        )
        
        async def compilation_stream():
            yield compilation_res["content"] + "\n\n"
            meta_json = json.dumps({"downloadFile": compilation_res["file_metadata"]})
            yield f"\n\n```json:metadata\n{meta_json}\n```"

        return StreamingResponse(compilation_stream(), media_type="text/event-stream")

    # 3. Autonomous Web Search decision via WebSearchAgent
    need_web_search = web_search_agent.should_search(
        query=request.query,
        history=payload_messages,
        has_local_answer=active_cds_has_answer
    )

    web_context_text = ""
    if need_web_search:
        print(f"[BORAX Web Search Agent] Acionando busca autônoma de fontes para: '{request.query}'")
        search_res = await asyncio.to_thread(web_search_agent.search_references, request.query)
        if search_res.get("has_results"):
            web_context_text = search_res.get("formatted_context", "")

    combined_context = f"{rag_context_text}\n\n{web_context_text}".strip()
    
    # Consolidate Sliding Window (10 turns) + RAG/Web Context + Query
    consolidated_query = ChatHistoryManager.build_consolidated_prompt(
        query=request.query,
        messages=payload_messages,
        rag_context=combined_context
    )

    final_payload_messages = [{"role": "user", "content": consolidated_query}]

    async def stream_generator():
        if need_web_search:
            yield "🔍 *Pesquisando fontes atualizadas na web...*\n\n"
        async for token in ollama_service.chat_stream(request.model, final_payload_messages, system_prompt):
            yield token

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

@app.post("/api/export-pack")
async def export_pack_endpoint(request: ExportPackRequest, background_tasks: BackgroundTasks):
    """Export LanceDB dataset and module metadata into a downloadable .knpack file."""
    temp_dir = tempfile.mkdtemp()
    try:
        pack_path = knpack_manager.export_knpack(
            module_name=request.module_name,
            system_prompt=request.system_prompt,
            table_name=request.table_name or DEFAULT_TABLE,
            description=request.description or "",
            output_dir=temp_dir
        )
    except Exception as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=400, detail=str(e))

    filename = os.path.basename(pack_path)

    def cleanup():
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    background_tasks.add_task(cleanup)

    return FileResponse(
        path=pack_path,
        filename=filename,
        media_type="application/zip"
    )

@app.post("/api/import-pack")
async def import_pack_endpoint(file: UploadFile = File(...)):
    """Upload and import a .knpack file into local LanceDB."""
    if not file.filename.endswith(".knpack"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .knpack são aceitos.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".knpack") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = knpack_manager.import_knpack(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao importar .knpack: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- MÓDULO LEITOR DE CARTUCHOS (KNOWLEDGE DRIVE) ---

@app.get("/api/drive/active-status")
async def drive_active_status_endpoint():
    """Fetch status of currently mounted cartridge/media."""
    return knowledge_manager.get_active_status()

@app.post("/api/drive/mount")
async def drive_mount_endpoint(file: UploadFile = File(...)):
    """Mount a .knpack, .pdf, .txt, .csv, or .docx file as the active system cartridge."""
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = [".knpack", ".pdf", ".txt", ".csv", ".docx"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Extensão '{ext}' não suportada para o leitor. Permitidas: {allowed_exts}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = await asyncio.to_thread(knowledge_manager.mount_media, tmp_path, file_name=filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao montar mídia no leitor: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/drive/eject")
async def drive_eject_endpoint():
    """Eject all active cartridges."""
    return knowledge_manager.eject_media()

@app.post("/api/drive/eject-one")
async def drive_eject_one_endpoint(cartridge_id: Optional[str] = Form(None)):
    """Eject a specific cartridge by ID or all if not specified."""
    return knowledge_manager.eject_media(cartridge_id=cartridge_id)

# --- HISTÓRICO LOCAL DE CONVERSAS ---

@app.get("/api/history/sessions")
async def list_history_sessions_endpoint():
    """List all saved chat sessions."""
    return {"sessions": history_manager.list_sessions()}

@app.post("/api/history/save")
async def save_history_session_endpoint(req: SaveSessionRequest):
    """Save or update a chat session."""
    return history_manager.save_session(
        title=req.title,
        messages=req.messages,
        cartridges=req.cartridges,
        session_id=req.id
    )

@app.get("/api/history/session/{session_id}")
async def load_history_session_endpoint(session_id: str):
    """Load chat session by ID."""
    session = history_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return session

@app.delete("/api/history/session/{session_id}")
async def delete_history_session_endpoint(session_id: str):
    """Delete chat session by ID."""
    return history_manager.delete_session(session_id)

# --- PODERES INLINE E GERAÇÃO DE ARQUIVOS ---

@app.post("/api/chat/power-execute")
async def chat_power_execute_endpoint(
    power_trigger: str = Form(...),
    text_input: Optional[str] = Form(""),
    file_format: Optional[str] = Form("docx"),
    file: Optional[UploadFile] = File(None)
):
    """Execute a power inline inside chat stream with optional attached file."""
    tmp_path = None
    file_name = None

    if file:
        file_name = file.filename
        ext = os.path.splitext(file_name)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

    try:
        res = await asyncio.to_thread(
            power_executor.execute_inline,
            power_trigger=power_trigger,
            text_input=text_input or "",
            file_path=tmp_path,
            file_name=file_name,
            file_format=file_format or "docx"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao executar poder inline: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/file/generate")
async def generate_file_endpoint(req: GenerateFileRequest):
    """Generate a downloadable file (.docx, .txt, .csv, .md) saved in ~/.borax/exports/."""
    return generate_downloadable_file(
        content=req.content,
        file_format=req.file_format or "docx",
        filename=req.filename
    )

@app.get("/api/file/download/{filename}")
async def download_file_endpoint(filename: str):
    """Download or view an exported file from ~/.borax/exports/."""
    file_path = os.path.join(BORAX_EXPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado nas exportações local.")

    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json"
    }

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_types.get(ext, "application/octet-stream")
    )

# --- MOLDAGEM INTERATIVA DE DOCUMENTOS ---

@app.post("/api/documents/initiate-wizard")
async def initiate_wizard_endpoint(req: InitiateWizardRequest):
    """Initiate document wizard proposals for user prompt."""
    return doc_wizard.initiate_wizard(req.prompt)

@app.post("/api/documents/generate-custom")
async def generate_custom_document_endpoint(req: GenerateCustomDocRequest):
    """Generate custom document text and compile downloadable file according to wizard preferences."""
    context_text = ""
    if req.use_rag:
        active_cartridge = knowledge_manager.get_active_status()
        target_tables = active_cartridge.get("table_names") or [DEFAULT_TABLE]
        contexts = await asyncio.to_thread(
            rag_engine.query_context,
            query=req.prompt,
            table_name=target_tables,
            top_k=2
        )
        if contexts:
            context_text = "\n---\n".join([f"[{c.get('source_table', 'base')}]: {c['text'][:350]}" for c in contexts])

    return await asyncio.to_thread(
        doc_wizard.generate_custom_document,
        prompt=req.prompt,
        preferences=req.preferences,
        context_text=context_text
    )

# --- MÍDIA E ANALISTA DE DADOS ---

@app.post("/api/media/transcribe")
async def transcribe_media_endpoint(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    table_name: Optional[str] = Form(DEFAULT_TABLE)
):
    """Transcribe local audio/video file or YouTube URL and index in RAG LanceDB."""
    source_target = None
    cleanup_temp = False

    if url:
        source_target = url.strip()
    elif file:
        ext = os.path.splitext(file.filename)[1].lower()
        allowed_media = [".mp3", ".wav", ".mp4", ".mkv", ".m4a", ".aac"]
        if ext not in allowed_media:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão de mídia '{ext}' não suportada. Permitidos: {allowed_media}"
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            source_target = tmp.name
            cleanup_temp = True
    else:
        raise HTTPException(status_code=400, detail="Forneça um arquivo de áudio/vídeo enviado ou uma URL do YouTube.")

    try:
        result = media_processor.transcribe_media(source_target, table_name=table_name, auto_ingest_rag=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na transcrição: {str(e)}")
    finally:
        if cleanup_temp and source_target and os.path.exists(source_target):
            os.remove(source_target)

@app.post("/api/data/analyze")
async def analyze_data_endpoint(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    user_query: str = Form(...),
    model: Optional[str] = Form("qwen2.5-0.5b-instruct-q4_k_m.gguf")
):
    """Query tabular data (CSV, Parquet, XLSX, JSON) using DuckDB + Polars Text-to-SQL."""
    target_path = None
    cleanup_temp = False

    if file:
        ext = os.path.splitext(file.filename)[1].lower()
        allowed_data = [".csv", ".parquet", ".xlsx", ".xls", ".json"]
        if ext not in allowed_data:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão de dados '{ext}' não suportada. Permitidos: {allowed_data}"
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            target_path = tmp.name
            cleanup_temp = True
    elif file_path:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Caminho do arquivo não encontrado: {file_path}")
        target_path = file_path
    else:
        raise HTTPException(status_code=400, detail="Forneça uma planilha/dataset enviado ou file_path.")

    try:
        result = data_analyst.query_data(target_path, user_query=user_query, model=model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de dados: {str(e)}")
    finally:
        if cleanup_temp and target_path and os.path.exists(target_path):
            os.remove(target_path)

# --- QUARTO MOTOR: AGENTE DESKTOP COM PERMISSÕES ---

@app.post("/api/agent/execute")
async def agent_execute_endpoint(request: AgentExecuteRequest):
    """Parse instruction and execute or return pending actions confirmation plan."""
    try:
        result = desktop_agent.plan_and_execute(
            instruction=request.instruction,
            execution_mode=request.execution_mode or "safe",
            allowed_paths=request.allowed_paths or [],
            model=request.model or "llama3.2"
        )
        return result
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na automação do agente: {str(e)}")

@app.post("/api/agent/confirm-execution")
async def agent_confirm_endpoint(request: AgentConfirmRequest):
    """Execute a confirmed automation plan."""
    try:
        result = desktop_agent.confirm_and_execute_plan(request.plan_id)
        return result
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na confirmação da automação: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
