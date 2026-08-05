import React, { useState, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { mountCartridge, ejectCartridge, ejectOneCartridge } from '../../services/api';
import { 
  Disc, 
  UploadCloud, 
  FileText, 
  Database, 
  Cpu, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  Terminal,
  HardDrive,
  Trash2,
  Plus
} from 'lucide-react';

const EjectIcon: React.FC<{ size?: number; className?: string }> = ({ size = 18, className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
  >
    <polygon points="12 2 2 14 22 14 12 2" />
    <line x1="2" y1="18" x2="22" y2="18" />
  </svg>
);

export const KnowledgeDrive: React.FC = () => {
  const { activeCartridge, refreshCartridge } = useApp();
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const cartridgesList = activeCartridge?.cartridges || [];
  const isMounted = activeCartridge?.mounted && cartridgesList.length > 0;

  const handleFile = async (file: File) => {
    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await mountCartridge(file);
      await refreshCartridge();
      setStatusMsg({ type: 'success', text: res.message || 'Cartucho encaixado no leitor com sucesso!' });
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Erro ao encaixar cartucho no leitor.' });
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleEjectAll = async () => {
    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await ejectCartridge();
      await refreshCartridge();
      setStatusMsg({ type: 'success', text: res.message || 'Todos os cartuchos foram ejetados com sucesso.' });
      setIsInspectorOpen(false);
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Erro ao ejetar cartuchos.' });
    } finally {
      setLoading(false);
    }
  };

  const handleEjectSingle = async (cartId: string) => {
    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await ejectOneCartridge(cartId);
      await refreshCartridge();
      setStatusMsg({ type: 'success', text: res.message || 'Cartucho ejetado.' });
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Erro ao ejetar cartucho.' });
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#090811] p-6 overflow-y-auto select-none font-sans text-gray-200 custom-scrollbar">
      {/* Header */}
      <div className="flex items-center justify-between bg-[#131022] border border-[#2B2443] p-5 rounded-2xl mb-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-[#1D1833] border border-[#3D335E] flex items-center justify-center text-indigo-400 shadow-inner">
            <HardDrive size={26} strokeWidth={2} />
          </div>
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider flex items-center gap-2">
              Leitor Multi-Dock de Cartuchos (Cérebro Composto)
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-mono font-medium">
                BORAX MULTI-DOCK
              </span>
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Encaixe múltiplos cartuchos (.knpack, .pdf, .txt, .csv) simultaneamente para alimentar a IA com contextos combinados.
            </p>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#0F0D18] border border-[#2B2443]">
            <span className={`w-2.5 h-2.5 rounded-full ${isMounted ? 'bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400' : 'bg-amber-400'}`} />
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-300 font-mono">
              {isMounted ? `${cartridgesList.length} CARTUCHO(S) DOCKED` : 'SLOTS LIVRES'}
            </span>
          </div>

          {isMounted && (
            <button
              onClick={handleEjectAll}
              className="px-3.5 py-2 rounded-xl bg-red-500/15 hover:bg-red-500/25 border border-red-500/40 text-red-300 text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition-colors"
            >
              <EjectIcon size={14} />
              <span>EJETAR TODOS</span>
            </button>
          )}
        </div>
      </div>

      {/* Alert Messages */}
      {statusMsg && (
        <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 text-xs font-medium ${
          statusMsg.type === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
            : 'bg-red-500/10 border-red-500/30 text-red-300'
        }`}>
          {statusMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{statusMsg.text}</span>
        </div>
      )}

      {/* Multi-Cartridge Active Dock List */}
      {isMounted && (
        <div className="mb-6 space-y-4">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
            <Layers size={16} className="text-indigo-400" />
            Cartuchos Encaixados no Dock:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cartridgesList.map((cart) => (
              <div 
                key={cart.id} 
                className="bg-[#14111F] border border-[#2B2443] rounded-2xl p-5 shadow-xl relative overflow-hidden flex items-center justify-between group hover:border-indigo-500/40 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div 
                    className="w-12 h-14 rounded-xl flex flex-col items-center justify-center p-2 text-white shadow-lg shrink-0"
                    style={{ backgroundColor: cart.cover_color || '#7C3AED' }}
                  >
                    <Disc size={20} className="animate-spin" style={{ animationDuration: '10s' }} />
                    <span className="text-[8px] font-bold uppercase font-mono mt-1">
                      {cart.type || 'CART'}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white font-mono">{cart.name}</h4>
                    <p className="text-xs text-gray-400 mt-0.5">
                      <span className="text-indigo-300 font-mono">{cart.vectors_count?.toLocaleString()} vetores</span> • {formatBytes(cart.size_bytes)}
                    </p>
                    <div className="text-[10px] text-gray-400 font-mono mt-1 truncate max-w-xs">
                      Tabela: {cart.table_name}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleEjectSingle(cart.id)}
                  title="Ejetar este cartucho"
                  className="p-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/25 border border-red-500/30 text-red-400 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input dropzone to add another cartridge */}
      <div className="mb-6">
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={(e) => e.target.files && e.target.files[0] && handleFile(e.target.files[0])}
          accept=".knpack,.pdf,.txt,.csv,.docx"
          className="hidden" 
        />

        {loading ? (
          <div className="w-full h-44 rounded-2xl bg-[#0F0D18] border-2 border-dashed border-indigo-500/60 flex flex-col items-center justify-center p-8 relative overflow-hidden shadow-2xl">
            <Disc className="w-10 h-10 text-indigo-400 animate-spin mb-3" />
            <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-widest font-mono">
              Indexando Chunks no Multi-Dock...
            </h3>
          </div>
        ) : (
          <div 
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`w-full ${isMounted ? 'h-36' : 'h-64'} rounded-2xl bg-[#0F0D18] border-2 border-dashed cursor-pointer transition-all duration-300 flex flex-col items-center justify-center p-6 text-center group ${
              isDragging 
                ? 'border-indigo-500 bg-indigo-500/10 shadow-2xl shadow-indigo-500/20' 
                : 'border-[#2B2443] hover:border-indigo-500/50 hover:bg-[#141122]'
            }`}
          >
            <div className="w-12 h-12 rounded-xl bg-[#1B162E] border border-[#362D54] flex items-center justify-center text-indigo-400 group-hover:scale-110 group-hover:border-indigo-500/60 transition-transform duration-300 mb-3 shadow-lg">
              {isMounted ? <Plus size={24} /> : <UploadCloud size={26} />}
            </div>
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider mb-1 font-mono">
              {isMounted ? 'ENCAIXAR MAIS UM CARTUCHO NO DOCK' : 'INSIRA OU ARRASTE UM CARTUCHO DE CONHECIMENTO'}
            </h3>
            <p className="text-[11px] text-gray-400 max-w-md">
              Arquivos suportados: <span className="text-indigo-300 font-mono">.knpack</span>, <span className="text-cyan-300 font-mono">.pdf</span>, <span className="text-cyan-300 font-mono">.txt</span>, <span className="text-cyan-300 font-mono">.csv</span>, <span className="text-cyan-300 font-mono">.docx</span>
            </p>
          </div>
        )}
      </div>

      {/* Inspector Drawer */}
      {isMounted && (
        <div className="bg-[#14111F] border border-[#2B2443] rounded-2xl overflow-hidden shadow-xl">
          <button
            onClick={() => setIsInspectorOpen(!isInspectorOpen)}
            className="w-full p-4 bg-[#181427] hover:bg-[#1C182E] flex items-center justify-between text-xs font-bold text-gray-200 uppercase tracking-wider transition-colors border-b border-[#2B2443]"
          >
            <div className="flex items-center gap-2.5">
              <FileText size={16} className="text-indigo-400" />
              <span>Inspetor de Contexto Combinado (Multi-Cartucho)</span>
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded font-mono font-normal">
                {activeCartridge?.total_vectors?.toLocaleString() || 0} vetores totais
              </span>
            </div>
            {isInspectorOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {isInspectorOpen && (
            <div className="p-6 space-y-6">
              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Terminal size={14} className="text-purple-400" />
                  System Prompt Combinado do Cérebro:
                </h4>
                <div className="bg-[#0B0A12] border border-[#231D38] rounded-xl p-4 font-mono text-xs text-purple-200 leading-relaxed whitespace-pre-wrap">
                  {activeCartridge?.system_prompt || 'Nenhum System Prompt configurado.'}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
