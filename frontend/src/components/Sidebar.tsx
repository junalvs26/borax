import React from 'react';
import { useApp } from '../context/AppContext';
import { MessageSquare, HardDrive, FileText, Video, Table, Shield } from 'lucide-react';
import { ActiveTab } from '../types';

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, backendOnline, selectedModel } = useApp();

  const navItems: Array<{ id: ActiveTab; label: string; icon: React.ReactNode }> = [
    { id: 'chat', label: 'Chat & Módulos', icon: <MessageSquare size={18} strokeWidth={2} /> },
    { id: 'drive', label: 'Leitor de Cartuchos', icon: <HardDrive size={18} strokeWidth={2} /> },
    { id: 'ingest', label: 'Tradutor & .knpack', icon: <FileText size={18} strokeWidth={2} /> },
    { id: 'media', label: 'Mídia & YouTube', icon: <Video size={18} strokeWidth={2} /> },
    { id: 'data', label: 'Analista de Dados', icon: <Table size={18} strokeWidth={2} /> },
    { id: 'agent', label: 'Agente & Segurança', icon: <Shield size={18} strokeWidth={2} /> },
  ];

  return (
    <aside className="w-64 bg-borax-surface border-r border-borax-border flex flex-col justify-between p-5 select-none shrink-0 h-screen overflow-hidden">
      <div>
        {/* BORAX Brand Logo & Title */}
        <div className="flex items-center gap-3 px-1 py-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-700 border border-purple-400/40 flex items-center justify-center shrink-0 shadow-lg shadow-purple-900/30">
            <span className="text-xl font-black text-white font-mono leading-none select-none tracking-tighter drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]">
              B
            </span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-white uppercase tracking-borax font-sans leading-none">
              BORAX
            </h1>
            <p className="text-[11px] text-borax-lilac-light font-medium tracking-borax mt-1">
              IA Local Modular
            </p>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-3 rounded-borax-btn text-xs font-medium tracking-borax transition-all duration-200 ${
                  isActive
                    ? 'bg-borax-purple/15 text-borax-lilac-light border border-borax-purple/40 shadow-sm shadow-borax-purple/20 font-semibold'
                    : 'text-borax-gray-muted hover:text-white hover:bg-borax-input/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={isActive ? 'text-borax-lilac-light' : 'text-borax-gray-muted'}>{item.icon}</span>
                  <span>{item.label}</span>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="pt-4 border-t border-borax-border space-y-3">
        <div className="bg-borax-input p-3.5 rounded-borax-input border border-borax-border">
          <div className="flex items-center justify-between text-xs text-borax-gray-muted mb-1.5">
            <span>Backend Python:</span>
            <div className="flex items-center gap-1.5 font-semibold">
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
              <span className={backendOnline ? 'text-emerald-400' : 'text-red-400'}>
                {backendOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between text-xs text-borax-gray-muted">
            <span>Modelo Ativo:</span>
            <span className="text-borax-lilac-light font-mono font-medium truncate max-w-[100px]" title={selectedModel}>
              {selectedModel || 'Nenhum'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
