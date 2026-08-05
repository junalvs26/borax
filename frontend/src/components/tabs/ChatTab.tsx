import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useApp } from '../../context/AppContext';
import { 
  sendMessageStream, 
  getChatSessions, 
  saveChatSession, 
  deleteChatSession,
  executeInlinePower,
  generateFile,
  getFileDownloadUrl,
  initiateDocumentWizard,
  generateCustomDocument
} from '../../services/api';
import { ChatMessage, PowerCommand, ChatSession, DocumentWizardPreferences } from '../../types';
import { DocumentWizardCard } from '../chat/DocumentWizardCard';
import { ArtifactCard, ArtifactFilePayload } from '../chat/ArtifactCard';
import { ArtifactViewer } from '../chat/ArtifactViewer';
import { 
  Send, 
  Bot, 
  User, 
  Database, 
  RefreshCw, 
  Zap, 
  Disc, 
  Trash2,
  Copy,
  Check,
  Volume2,
  RotateCcw,
  Save,
  History,
  X,
  Sparkles,
  Paperclip,
  FileText,
  Download,
  ExternalLink
} from 'lucide-react';

const POWERS_LIST: PowerCommand[] = [
  { id: '1', name: 'Criar / Montar Base', trigger: '@criar-base', description: 'Encaixar cartucho no leitor diretamente', icon: 'Disc', action_type: 'action' },
  { id: '2', name: 'Ingestão de Documento', trigger: '@ingestao', description: 'Ingerir PDF, TXT ou DOCX no LanceDB', icon: 'Database', action_type: 'action' },
  { id: '3', name: 'Transcrever Áudio/Vídeo', trigger: '@transcrever', description: 'Transcrição offline via Whisper', icon: 'Volume2', action_type: 'action' },
  { id: '4', name: 'Análise de Planilha SQL', trigger: '@analisar-dados', description: 'Consulta SQL via DuckDB em CSVs', icon: 'Sparkles', action_type: 'action' },
  { id: '5', name: 'Moldar & Gerar Documento', trigger: '@gerar-documento', description: 'Iniciar Card de Moldagem Interativa (Word/PDF/TXT)', icon: 'FileText', action_type: 'action' },
  { id: '6', name: 'Salvar Conversa Atual', trigger: '@salvar', description: 'Gravar sessão no histórico local', icon: 'Save', action_type: 'action' }
];

interface ChatMessageExtended extends ChatMessage {
  powerStatus?: 'running' | 'completed' | 'error';
  powerTitle?: string;
  wizardData?: {
    promptOriginal: string;
    suggestedPreferences: DocumentWizardPreferences;
  };
  downloadFile?: {
    filename: string;
    file_format: string;
    download_url: string;
    size_bytes?: number;
    page_count?: number;
    line_count?: number;
  };
  attachedFile?: {
    name: string;
    size: number;
  };
}

export const ChatTab: React.FC = () => {
  const { selectedModel, setSelectedModel, models, activeTable, refreshModels, activeCartridge, refreshCartridge } = useApp();
  const [messages, setMessages] = useState<ChatMessageExtended[]>([
    { id: '1', role: 'assistant', content: 'Olá! Sou sua IA local BORAX com **Moldagem Interativa de Documentos** e **Cérebro Composto**. Como posso ajudar você hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [useRag, setUseRag] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  
  // Artifact Viewer Modal state
  const [viewerArtifact, setViewerArtifact] = useState<ArtifactFilePayload | null>(null);
  const [viewerDocText, setViewerDocText] = useState<string>('');
  
  // Floating Power Menu state
  const [showPowerMenu, setShowPowerMenu] = useState(false);
  const [powerFilter, setPowerFilter] = useState('');

  // History Drawer state
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [savedSessions, setSavedSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // UX copy state
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const [copiedCodeIndex, setCopiedCodeIndex] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const cartridgesList = activeCartridge?.cartridges || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  const fetchHistory = async () => {
    const list = await getChatSessions();
    setSavedSessions(list);
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);

    if (val.includes('@') || val.includes('/')) {
      const match = val.match(/[@\/](\w*)$/);
      if (match) {
        setPowerFilter(match[1].toLowerCase());
        setShowPowerMenu(true);
      } else {
        setShowPowerMenu(false);
      }
    } else {
      setShowPowerMenu(false);
    }
  };

  const executePower = async (power: PowerCommand) => {
    setShowPowerMenu(false);
    setInput(`${power.trigger} `);
  };

  const handleSaveSession = async () => {
    if (messages.length <= 1) return;
    const firstUserMsg = messages.find(m => m.role === 'user')?.content || 'Conversa BORAX';
    const title = firstUserMsg.slice(0, 30) + (firstUserMsg.length > 30 ? '...' : '');

    try {
      const res = await saveChatSession({
        id: currentSessionId || undefined,
        title,
        messages,
        cartridges: cartridgesList
      });
      if (res.session) {
        setCurrentSessionId(res.session.id);
        await fetchHistory();
        setMessages(prev => [
          ...prev,
          { id: Date.now().toString(), role: 'assistant', content: `💾 Conversa salva no histórico local como **"${title}"**!` }
        ]);
      }
    } catch (e: any) {
      console.error('Erro ao salvar conversa:', e);
    }
  };

  const handleLoadSession = (session: ChatSession) => {
    setMessages(session.messages);
    setCurrentSessionId(session.id);
    setIsHistoryOpen(false);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteChatSession(sessionId);
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
    }
    await fetchHistory();
  };

  const handleWizardConfirm = async (msgId: string, promptOriginal: string, prefs: DocumentWizardPreferences) => {
    setMessages(prev =>
      prev.map(m =>
        m.id === msgId
          ? { ...m, powerStatus: 'running', powerTitle: '🚀 Solicitando redação à LLM e compilando documento ABNT...' }
          : m
      )
    );
    setIsStreaming(true);

    try {
      const res = await generateCustomDocument(promptOriginal, prefs, useRag);
      setMessages(prev =>
        prev.map(m =>
          m.id === msgId
            ? {
                ...m,
                powerStatus: 'completed',
                wizardData: undefined,
                content: res.document_text 
                  ? `### 📄 Documento Gerado com Sucesso!\n\n${res.document_text}`
                  : (res.message || 'Documento gerado com sucesso!'),
                downloadFile: res.file
              }
            : m
        )
      );
    } catch (err: any) {
      setMessages(prev =>
        prev.map(m =>
          m.id === msgId
            ? { ...m, powerStatus: 'error', content: `⚠️ Erro ao compilar documento: ${err.message}` }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && !attachedFile) || isStreaming) return;

    const trimmedInput = input.trim();
    const currentFile = attachedFile;
    setAttachedFile(null);
    setInput('');
    setShowPowerMenu(false);

    const powerMatch = trimmedInput.match(/^(@[\w-]+|\/[\w-]+)/i);
    const powerTrigger = powerMatch ? powerMatch[1].toLowerCase() : null;

    const userMsgId = Date.now().toString();
    const userMsg: ChatMessageExtended = {
      id: userMsgId,
      role: 'user',
      content: trimmedInput || (currentFile ? `Anexou arquivo: ${currentFile.name}` : ''),
      attachedFile: currentFile ? { name: currentFile.name, size: currentFile.size } : undefined
    };

    setMessages(prev => [...prev, userMsg]);
    setIsStreaming(true);

    if (powerTrigger === '@salvar') {
      setIsStreaming(false);
      await handleSaveSession();
      return;
    }

    // Conversational UX: All requests flow through natural streaming chat
    // (Static DocumentWizardCard deactivated in favor of Academic Advisor consultation)

    // Process inline power or file attachment
    if (powerTrigger || currentFile) {
      const assistantMsgId = (Date.now() + 1).toString();
      const statusMsg: ChatMessageExtended = {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        powerStatus: 'running',
        powerTitle: powerTrigger ? `Executando Poder ${powerTrigger}...` : `Processando arquivo ${currentFile?.name}...`
      };

      setMessages(prev => [...prev, statusMsg]);

      try {
        const effectiveTrigger = powerTrigger || (currentFile ? '@ingestao' : '');
        const res = await executeInlinePower(
          effectiveTrigger,
          trimmedInput.replace(/^(@[\w-]+|\/[\w-]+)\s*/i, ''),
          'docx',
          currentFile || undefined
        );

        await refreshCartridge();

        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  powerStatus: 'completed',
                  content: res.message || 'Poder executado com sucesso!',
                  downloadFile: res.file
                }
              : m
          )
        );
      } catch (err: any) {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMsgId
              ? {
                  ...m,
                  powerStatus: 'error',
                  content: `⚠️ Erro ao executar poder inline: ${err.message}`
                }
              : m
          )
        );
      } finally {
        setIsStreaming(false);
      }
      return;
    }

    // Normal AI Chat Streaming
    const assistantMsgId = (Date.now() + 1).toString();
    const assistantMsg: ChatMessageExtended = {
      id: assistantMsgId,
      role: 'assistant',
      content: ''
    };

    setMessages(prev => [...prev, assistantMsg]);

    try {
      let accumulatedText = '';
      await sendMessageStream(
        userMsg.content,
        selectedModel,
        activeTable,
        useRag,
        messages,
        (chunk) => {
          accumulatedText += chunk;
          setMessages(prev =>
            prev.map(m => (m.id === assistantMsgId ? { ...m, content: accumulatedText } : m))
          );
        }
      );
    } catch (e: any) {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMsgId
            ? { ...m, content: `⚠️ Erro na resposta: ${e.message || 'Falha de comunicação com o modelo C++ local.'}` }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const handleCopyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleSpeakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text.replace(/[*#_`]/g, ''));
      utterance.lang = 'pt-BR';
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleRegenerate = async (msgIndex: number) => {
    if (isStreaming || msgIndex === 0) return;
    const previousMessages = messages.slice(0, msgIndex);
    const lastUserMsg = [...previousMessages].reverse().find(m => m.role === 'user');

    if (!lastUserMsg) return;

    setMessages(previousMessages);
    setIsStreaming(true);

    const assistantMsgId = Date.now().toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '' }]);

    try {
      let accumulatedText = '';
      await sendMessageStream(
        lastUserMsg.content,
        selectedModel,
        activeTable,
        useRag,
        previousMessages,
        (chunk) => {
          accumulatedText += chunk;
          setMessages(prev =>
            prev.map(m => (m.id === assistantMsgId ? { ...m, content: accumulatedText } : m))
          );
        }
      );
    } catch (e: any) {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMsgId ? { ...m, content: `⚠️ Erro ao regenerar: ${e.message}` } : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const filteredPowers = POWERS_LIST.filter(p => 
    p.name.toLowerCase().includes(powerFilter) || 
    p.trigger.toLowerCase().includes(powerFilter)
  );

  return (
    <div 
      onDragOver={(e) => { e.preventDefault(); setIsDraggingFile(true); }}
      onDragLeave={() => setIsDraggingFile(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDraggingFile(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          setAttachedFile(e.dataTransfer.files[0]);
        }
      }}
      className="flex-1 flex flex-col h-full bg-[#090811] p-6 overflow-hidden select-none font-sans text-gray-200 relative"
    >
      {/* Drag and Drop File Overlay */}
      {isDraggingFile && (
        <div className="absolute inset-0 bg-indigo-900/80 backdrop-blur-md border-4 border-dashed border-indigo-400 z-50 flex flex-col items-center justify-center text-white">
          <Paperclip size={48} className="animate-bounce mb-3 text-indigo-300" />
          <h3 className="text-base font-bold font-mono uppercase tracking-widest">
            SOLTE O ARQUIVO PARA ANEXAR NO CHAT
          </h3>
          <p className="text-xs text-indigo-200 mt-1">
            Suporta .pdf, .txt, .csv, .docx, .knpack ou mídias
          </p>
        </div>
      )}

      {/* Header controls */}
      <div className="flex items-center justify-between bg-[#131022] border border-[#2B2443] p-4 rounded-2xl mb-4 shadow-xl">
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-gray-400 tracking-wider">Modelo:</label>
          <div className="flex items-center gap-2">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-[#0B0A12] border border-[#2B2443] text-gray-200 text-xs font-medium rounded-xl px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
            >
              {models.length > 0 ? (
                models.map(m => (
                  <option key={m.name} value={m.name}>
                    {m.name}
                  </option>
                ))
              ) : (
                <option value="qwen2.5-0.5b-instruct-q4_k_m.gguf">Qwen 2.5 0.5B (C++ Embutido Ultra Leve)</option>
              )}
            </select>
            <button
              onClick={refreshModels}
              title="Atualizar modelos"
              className="p-1.5 rounded-xl bg-[#0B0A12] text-gray-400 hover:text-white hover:border-indigo-500 border border-[#2B2443] transition-colors"
            >
              <RefreshCw size={14} strokeWidth={2} />
            </button>
          </div>
        </div>

        {/* Multi-Cartridge Active Badges */}
        <div className="flex items-center gap-3">
          {activeCartridge?.mounted && cartridgesList.length > 0 ? (
            <div className="flex items-center gap-2 bg-[#1A152E] border border-purple-500/40 text-purple-200 px-3 py-1.5 rounded-xl shadow-inner text-xs font-mono">
              <Disc size={14} className="text-purple-400 animate-spin" style={{ animationDuration: '8s' }} />
              <span className="text-gray-300 font-medium">Bases Ativas:</span>
              <div className="flex items-center gap-1.5">
                {cartridgesList.map((c) => (
                  <span key={c.id} className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/30 text-purple-200 border border-purple-400/40">
                    {c.name}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-[#0B0A12] px-3 py-1.5 rounded-xl border border-[#2B2443]">
              <Database size={14} className="text-cyan-400" strokeWidth={2} />
              <span className="text-xs font-medium text-gray-400 tracking-wider">Tabela LanceDB:</span>
              <span className="text-xs font-mono text-cyan-300">{activeTable}</span>
            </div>
          )}

          <button
            onClick={() => setUseRag(!useRag)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wider border transition-all ${
              useRag
                ? 'bg-indigo-500/15 text-indigo-300 border-indigo-500/40 shadow-sm shadow-indigo-500/20'
                : 'bg-[#0B0A12] text-gray-400 border-[#2B2443]'
            }`}
          >
            <Zap size={14} strokeWidth={2} />
            <span>RAG: {useRag ? 'Ativo' : 'Off'}</span>
          </button>

          <button
            onClick={() => setIsHistoryOpen(!isHistoryOpen)}
            title="Abrir histórico de conversas"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-gray-300 hover:text-white bg-[#0B0A12] border border-[#2B2443] hover:border-indigo-500/40 transition-colors"
          >
            <History size={14} />
            <span>Histórico</span>
          </button>

          <button
            onClick={handleSaveSession}
            title="Salvar conversa atual"
            className="p-1.5 rounded-xl text-xs text-gray-400 hover:text-emerald-400 bg-[#0B0A12] border border-[#2B2443] hover:border-emerald-500/40 transition-colors"
          >
            <Save size={14} />
          </button>

          <button
            onClick={() => {
              setMessages([{
                id: 'init-msg',
                role: 'assistant',
                content: 'Olá! Sou o assistente BORAX. Como posso te ajudar hoje?',
                timestamp: new Date().toLocaleTimeString()
              }]);
              setCurrentSessionId(null);
            }}
            title="Limpar chat"
            className="p-1.5 rounded-xl text-xs text-gray-400 hover:text-red-400 bg-[#0B0A12] border border-[#2B2443] hover:border-red-500/40 transition-colors"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
        {messages.map((msg, index) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-md ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white'
                  : 'bg-[#14111F] text-indigo-400 border border-[#2B2443]'
              }`}
            >
              {msg.role === 'user' ? <User size={18} strokeWidth={2} /> : <Bot size={18} strokeWidth={2} />}
            </div>

            <div className={`max-w-[78%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              
              {/* Attached file pill in user message */}
              {msg.attachedFile && (
                <div className="mb-1.5 px-3 py-1 rounded-xl bg-[#1B162E] border border-[#372D5C] text-xs font-mono text-indigo-300 flex items-center gap-2">
                  <Paperclip size={12} />
                  <span>Anexo: {msg.attachedFile.name} ({formatBytes(msg.attachedFile.size)})</span>
                </div>
              )}

              {/* Power Status Execution Card */}
              {msg.powerStatus === 'running' && (
                <div className="mb-2 p-3.5 rounded-2xl bg-[#14111F] border border-indigo-500/50 flex items-center gap-3 text-xs font-mono text-indigo-300 animate-pulse shadow-xl">
                  <Sparkles size={16} className="text-indigo-400 animate-spin" />
                  <span>⚡ {msg.powerTitle || 'Processando Poder Inline...'}</span>
                </div>
              )}

              {/* Interactive Document Wizard Card */}
              {msg.wizardData && (
                <DocumentWizardCard
                  promptOriginal={msg.wizardData.promptOriginal}
                  initialPreferences={msg.wizardData.suggestedPreferences}
                  disabled={isStreaming}
                  onConfirm={(prefs) => handleWizardConfirm(msg.id!, msg.wizardData!.promptOriginal, prefs)}
                />
              )}

              {/* Downloadable Artifact Card Payload */}
              {msg.downloadFile && (
                <ArtifactCard
                  file={{
                    filename: msg.downloadFile.filename,
                    file_format: msg.downloadFile.file_format,
                    filepath: '',
                    size_bytes: msg.downloadFile.size_bytes,
                    page_count: msg.downloadFile.page_count,
                    line_count: msg.downloadFile.line_count,
                    download_url: getFileDownloadUrl(msg.downloadFile.filename)
                  }}
                  onViewStructure={() => {
                    setViewerArtifact({
                      filename: msg.downloadFile!.filename,
                      file_format: msg.downloadFile!.file_format,
                      filepath: '',
                      size_bytes: msg.downloadFile!.size_bytes,
                      page_count: msg.downloadFile!.page_count,
                      line_count: msg.downloadFile!.line_count,
                      download_url: getFileDownloadUrl(msg.downloadFile!.filename)
                    });
                    setViewerDocText(msg.content);
                  }}
                />
              )}

              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed tracking-wide ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none shadow-lg'
                    : 'bg-[#14111F] text-gray-200 border border-[#2B2443] rounded-tl-none shadow-xl'
                }`}
              >
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ node, href, children, ...props }) => (
                        <a
                          href={href}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => {
                            e.preventDefault();
                            if (href) window.open(href, '_blank');
                          }}
                          className="text-[#6D28FF] hover:underline font-semibold inline-flex items-center gap-1 cursor-pointer"
                          {...props}
                        >
                          {children}
                          <ExternalLink size={12} className="inline" />
                        </a>
                      ),
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-3 rounded-xl border border-[#2B2443]">
                          <table className="min-w-full divide-y divide-[#2B2443] bg-[#14111F]" {...props} />
                        </div>
                      ),
                      thead: ({ node, ...props }) => (
                        <thead className="bg-[#1C172E] text-indigo-300 font-mono text-xs uppercase" {...props} />
                      ),
                      th: ({ node, ...props }) => (
                        <th className="px-4 py-2 text-left font-bold" {...props} />
                      ),
                      td: ({ node, ...props }) => (
                        <td className="px-4 py-2 border-t border-[#231C38] text-xs text-gray-300 font-mono" {...props} />
                      ),
                      code: ({ node, inline, className, children, ...props }: any) => {
                        const match = /language-(\w+)/.exec(className || '');
                        const codeString = String(children).replace(/\n$/, '');
                        const codeId = `${msg.id}-${match ? match[1] : 'code'}`;

                        return !inline ? (
                          <div className="relative my-3 rounded-xl overflow-hidden border border-[#2B2443] bg-[#0B0913]">
                            <div className="flex items-center justify-between px-4 py-1.5 bg-[#181427] border-b border-[#2B2443] text-xs font-mono text-gray-400">
                              <span>{match ? match[1] : 'código'}</span>
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(codeString);
                                  setCopiedCodeIndex(codeId);
                                  setTimeout(() => setCopiedCodeIndex(null), 2000);
                                }}
                                className="flex items-center gap-1 text-[11px] text-indigo-300 hover:text-white transition-colors"
                              >
                                {copiedCodeIndex === codeId ? <Check size={12} /> : <Copy size={12} />}
                                <span>{copiedCodeIndex === codeId ? 'Copiado!' : 'Copiar código'}</span>
                              </button>
                            </div>
                            <pre className="p-4 font-mono text-xs text-indigo-200 overflow-x-auto custom-scrollbar">
                              <code>{children}</code>
                            </pre>
                          </div>
                        ) : (
                          <code className="bg-[#1B162E] text-purple-300 font-mono px-1.5 py-0.5 rounded text-xs border border-[#372D5C]" {...props}>
                            {children}
                          </code>
                        );
                      }
                    }}
                  >
                    {msg.content || (isStreaming && !msg.powerStatus && !msg.wizardData ? 'Pensando no modelo C++...' : '')}
                  </ReactMarkdown>
                )}
              </div>

              {/* Message Action Bar (Assistant Only) */}
              {msg.role === 'assistant' && msg.content && (
                <div className="flex items-center gap-2 mt-1.5 text-xs text-gray-400 px-1">
                  <button
                    onClick={() => handleCopyText(msg.id!, msg.content)}
                    className="hover:text-indigo-400 flex items-center gap-1 transition-colors"
                  >
                    {copiedMsgId === msg.id ? <Check size={12} /> : <Copy size={12} />}
                    <span>{copiedMsgId === msg.id ? 'Copiado' : 'Copiar'}</span>
                  </button>

                  <button
                    onClick={() => handleSpeakText(msg.content)}
                    className="hover:text-purple-400 flex items-center gap-1 transition-colors ml-2"
                  >
                    <Volume2 size={12} />
                    <span>Ouvir</span>
                  </button>

                  <button
                    onClick={() => handleRegenerate(index)}
                    className="hover:text-emerald-400 flex items-center gap-1 transition-colors ml-2"
                  >
                    <RotateCcw size={12} />
                    <span>Regenerar</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Floating Power Menu */}
      {showPowerMenu && filteredPowers.length > 0 && (
        <div className="absolute bottom-20 left-6 right-6 max-w-lg bg-[#14111F] border border-indigo-500/40 rounded-2xl shadow-2xl p-2 z-50 overflow-hidden">
          <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-indigo-400 border-b border-[#2B2443] flex items-center gap-1.5">
            <Sparkles size={12} />
            <span>Poderes e Moldagem de Documentos BORAX:</span>
          </div>
          <div className="mt-1 space-y-1">
            {filteredPowers.map(power => (
              <button
                key={power.id}
                onClick={() => executePower(power)}
                className="w-full p-2.5 rounded-xl bg-[#0F0D18] hover:bg-[#1C172E] border border-transparent hover:border-indigo-500/30 flex items-center justify-between text-left transition-colors group"
              >
                <div>
                  <div className="text-xs font-bold text-white font-mono flex items-center gap-2">
                    <span className="text-indigo-400 font-bold">{power.trigger}</span>
                    <span>• {power.name}</span>
                  </div>
                  <div className="text-[11px] text-gray-400 mt-0.5">{power.description}</div>
                </div>
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded font-mono uppercase group-hover:bg-indigo-500/40">
                  Selecionar
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* History Sidebar Drawer */}
      {isHistoryOpen && (
        <div className="absolute top-0 right-0 bottom-0 w-80 bg-[#131022] border-l border-[#2B2443] p-5 shadow-2xl z-50 flex flex-col">
          <div className="flex items-center justify-between pb-4 border-b border-[#2B2443]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
              <History size={16} className="text-indigo-400" />
              Histórico de Conversas
            </h3>
            <button
              onClick={() => setIsHistoryOpen(false)}
              className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-[#1F1936]"
            >
              <X size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto my-4 space-y-2.5 custom-scrollbar pr-1">
            {savedSessions.length > 0 ? (
              savedSessions.map(session => (
                <div
                  key={session.id}
                  onClick={() => handleLoadSession(session)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    currentSessionId === session.id
                      ? 'bg-indigo-600/20 border-indigo-500/50 text-white'
                      : 'bg-[#0F0D18] border-[#2B2443] hover:border-indigo-500/30 text-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold font-mono truncate">{session.title}</h4>
                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      title="Excluir sessão"
                      className="text-gray-400 hover:text-red-400 p-1"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                  <div className="flex items-center justify-between mt-2 text-[10px] text-gray-400 font-mono">
                    <span>{session.message_count} mensagens</span>
                    <span>{new Date(session.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-gray-400 text-center py-8 italic font-mono">
                Nenhuma conversa salva ainda.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Attached file preview pill */}
      {attachedFile && (
        <div className="mb-2 px-3 py-1.5 rounded-xl bg-[#1A152E] border border-indigo-500/40 text-xs font-mono text-indigo-200 flex items-center justify-between max-w-md">
          <div className="flex items-center gap-2 truncate">
            <Paperclip size={14} className="text-indigo-400" />
            <span className="truncate">{attachedFile.name} ({formatBytes(attachedFile.size)})</span>
          </div>
          <button onClick={() => setAttachedFile(null)} className="text-gray-400 hover:text-red-400">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Input Form */}
      <div className="mt-2 flex gap-3 bg-[#131022] p-2 border border-[#2B2443] rounded-2xl shadow-xl items-center">
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => e.target.files && e.target.files[0] && setAttachedFile(e.target.files[0])}
          accept=".pdf,.txt,.csv,.docx,.knpack,audio/*,video/*"
          className="hidden"
        />

        <button
          onClick={() => fileInputRef.current?.click()}
          title="Anexar arquivo no chat"
          className="p-2.5 rounded-xl bg-[#0B0A12] border border-[#2B2443] text-gray-400 hover:text-indigo-400 hover:border-indigo-500/40 transition-colors"
        >
          <Paperclip size={18} />
        </button>

        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Digite sua mensagem, use @ para Poderes/Moldagem ou anexe arquivos..."
          disabled={isStreaming}
          className="flex-1 bg-transparent px-2 text-sm text-gray-200 placeholder-gray-400 focus:outline-none tracking-wide"
        />

        <button
          onClick={handleSend}
          disabled={isStreaming || (!input.trim() && !attachedFile)}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-xs tracking-wider flex items-center gap-2 shadow-lg shadow-indigo-600/20 hover:scale-[1.02] transition-all disabled:opacity-50"
        >
          <span>Enviar</span>
          <Send size={16} strokeWidth={2} />
        </button>
      </div>

      {/* Artifact Structure Viewer Modal */}
      {viewerArtifact && (
        <ArtifactViewer
          file={viewerArtifact}
          documentText={viewerDocText}
          isOpen={!!viewerArtifact}
          onClose={() => setViewerArtifact(null)}
        />
      )}
    </div>
  );
};
