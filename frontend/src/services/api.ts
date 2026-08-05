import {
  OllamaModel,
  ChatMessage,
  IngestResponse,
  MediaTranscribeResponse,
  DataAnalyzeResponse,
  AgentExecuteResponse,
  MountedCartridge
} from '../types';

const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return 'http://localhost:8000';
};

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/`);
    return res.ok;
  } catch (e) {
    return false;
  }
}

export async function getModels(): Promise<OllamaModel[]> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/models`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.models || [];
  } catch (e) {
    console.error('Erro ao buscar modelos do Ollama:', e);
    return [];
  }
}

export async function sendMessageStream(
  query: string,
  model: string,
  tableName: string = 'knowledge_base',
  useRag: boolean = true,
  messages: ChatMessage[] = [],
  onChunk: (text: string) => void
): Promise<void> {
  const payload = {
    query,
    model: model || 'qwen2.5-0.5b-instruct-q4_k_m.gguf',
    table_name: tableName || 'knowledge_base',
    use_rag: useRag,
    messages: messages.map(m => ({ role: m.role, content: m.content }))
  };

  const response = await fetch(`${getApiBaseUrl()}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => response.statusText);
    throw new Error(`Erro ${response.status}: ${errText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }
}

export async function ingestFile(file: File, tableName: string = 'knowledge_base'): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('table_name', tableName);

  const res = await fetch(`${getApiBaseUrl()}/api/ingest`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Erro na ingestão de arquivo.');
  }

  return res.json();
}

export async function exportKnpack(
  moduleName: string,
  systemPrompt: string,
  tableName: string = 'knowledge_base',
  description: string = ''
): Promise<Blob> {
  const payload = {
    module_name: moduleName,
    system_prompt: systemPrompt,
    table_name: tableName,
    description
  };

  const res = await fetch(`${getApiBaseUrl()}/api/export-pack`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao exportar pacote' }));
    throw new Error(err.detail);
  }

  return res.blob();
}

export async function importKnpack(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${getApiBaseUrl()}/api/import-pack`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao importar .knpack' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function transcribeMedia(
  file?: File,
  url?: string,
  tableName: string = 'knowledge_base'
): Promise<MediaTranscribeResponse> {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (url) formData.append('url', url);
  formData.append('table_name', tableName);

  const res = await fetch(`${getApiBaseUrl()}/api/media/transcribe`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro na transcrição de mídia' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function analyzeData(
  file?: File,
  filePath?: string,
  userQuery: string = '',
  model: string = 'qwen2.5-0.5b-instruct-q4_k_m.gguf'
): Promise<DataAnalyzeResponse> {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (filePath) formData.append('file_path', filePath);
  formData.append('user_query', userQuery);
  formData.append('model', model);

  const res = await fetch(`${getApiBaseUrl()}/api/data/analyze`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro na análise de dados' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function executeAgent(
  instruction: string,
  executionMode: string = 'safe',
  allowedPaths: string[] = [],
  model: string = 'qwen2.5-0.5b-instruct-q4_k_m.gguf'
): Promise<AgentExecuteResponse> {
  const payload = {
    instruction,
    execution_mode: executionMode,
    allowed_paths: allowedPaths,
    model
  };

  const res = await fetch(`${getApiBaseUrl()}/api/agent/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao executar agente' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function confirmAgentExecution(planId: string): Promise<AgentExecuteResponse> {
  const res = await fetch(`${getApiBaseUrl()}/api/agent/confirm-execution`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan_id: planId })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao confirmar execução do plano' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function getCartridgeStatus(): Promise<MountedCartridge> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/drive/active-status`);
    if (!res.ok) throw new Error('Erro ao obter status do leitor');
    return res.json();
  } catch (e) {
    return { mounted: false, name: 'Nenhum Cartucho Montado' };
  }
}

export async function mountCartridge(file: File): Promise<{ status: string; message: string; cartridge: MountedCartridge }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${getApiBaseUrl()}/api/drive/mount`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao montar mídia no leitor' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function ejectCartridge(): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/drive/eject`, {
    method: 'POST'
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao ejetar mídia do leitor' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function ejectOneCartridge(cartridgeId?: string): Promise<any> {
  const formData = new FormData();
  if (cartridgeId) formData.append('cartridge_id', cartridgeId);

  const res = await fetch(`${getApiBaseUrl()}/api/drive/eject-one`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao ejetar cartucho do leitor' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function getChatSessions(): Promise<any[]> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/api/history/sessions`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.sessions || [];
  } catch (e) {
    console.error('Erro ao buscar histórico de conversas:', e);
    return [];
  }
}

export async function saveChatSession(sessionData: { id?: string; title: string; messages: ChatMessage[]; cartridges?: any[] }): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/history/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sessionData)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao salvar sessão de conversa' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function deleteChatSession(sessionId: string): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/history/session/${sessionId}`, {
    method: 'DELETE'
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao excluir conversa' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function executeInlinePower(
  powerTrigger: string,
  textInput: string = '',
  fileFormat: string = 'docx',
  file?: File
): Promise<any> {
  const formData = new FormData();
  formData.append('power_trigger', powerTrigger);
  formData.append('text_input', textInput);
  formData.append('file_format', fileFormat);
  if (file) formData.append('file', file);

  const res = await fetch(`${getApiBaseUrl()}/api/chat/power-execute`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao executar poder no chat' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function generateFile(content: string, fileFormat: string = 'docx', filename?: string): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/file/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, file_format: fileFormat, filename })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao gerar arquivo' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export function getFileDownloadUrl(filename: string): string {
  return `${getApiBaseUrl()}/api/file/download/${filename}`;
}

export async function initiateDocumentWizard(prompt: string): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/documents/initiate-wizard`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao iniciar moldagem de documento' }));
    throw new Error(err.detail);
  }

  return res.json();
}

export async function generateCustomDocument(prompt: string, preferences: any, useRag: boolean = true): Promise<any> {
  const res = await fetch(`${getApiBaseUrl()}/api/documents/generate-custom`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, preferences, use_rag: useRag })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro ao gerar documento customizado' }));
    throw new Error(err.detail);
  }

  return res.json();
}
