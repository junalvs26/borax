import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { executeAgent } from '../../services/api';
import { AgentExecuteResponse } from '../../types';
import { Shield, Play, Terminal, CheckCircle2, Lock, AlertTriangle, Unlock, Plus, Trash2 } from 'lucide-react';

export const AgentSettingsTab: React.FC = () => {
  const {
    selectedModel,
    executionMode,
    setExecutionMode,
    allowedPaths,
    setAllowedPaths,
    setPendingAgentPlan
  } = useApp();

  const [instruction, setInstruction] = useState('');
  const [newPathInput, setNewPathInput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<AgentExecuteResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleAddPath = () => {
    if (newPathInput.trim() && !allowedPaths.includes(newPathInput.trim())) {
      setAllowedPaths(prev => [...prev, newPathInput.trim()]);
      setNewPathInput('');
    }
  };

  const handleRemovePath = (pathToRemove: string) => {
    setAllowedPaths(prev => prev.filter(p => p !== pathToRemove));
  };

  const handleRunAgent = async () => {
    if (!instruction.trim()) return;
    setIsExecuting(true);
    setErrorMessage(null);
    setExecutionResult(null);

    try {
      const res = await executeAgent(instruction.trim(), executionMode, allowedPaths, selectedModel);
      if (res.requires_confirmation) {
        setPendingAgentPlan(res);
      } else {
        setExecutionResult(res);
      }
    } catch (e: any) {
      setErrorMessage(e.message);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex-1 p-6 bg-borax-bg overflow-y-auto space-y-6 custom-scrollbar">
      {/* Permission Security Configuration */}
      <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2 tracking-borax">
            <Shield className="text-borax-lilac-light" size={24} strokeWidth={2} />
            <span>Nível de Permissão & Sandbox do Agente Desktop</span>
          </h2>
          <p className="text-xs text-borax-gray-muted tracking-borax">
            Configure o nível de acesso ao sistema de arquivos do computador para automação.
          </p>
        </div>

        {/* 3 Modes Selector */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Safe Mode */}
          <button
            onClick={() => setExecutionMode('safe')}
            className={`p-4 rounded-borax-card border text-left transition-all ${
              executionMode === 'safe'
                ? 'bg-borax-purple/15 border-borax-purple shadow-lg shadow-borax-purple/10'
                : 'bg-borax-input border-borax-border hover:border-borax-purple/40'
            }`}
          >
            <div className="flex items-center gap-2 text-borax-lilac-light font-bold text-sm mb-2 tracking-borax">
              <Lock size={18} strokeWidth={2} />
              <span>Seguro (Safe)</span>
            </div>
            <p className="text-xs text-borax-gray-muted leading-relaxed tracking-borax">
              Acesso apenas a diretórios seguros (Downloads, Documentos, Desktop). Pastas de sistema bloqueadas.
            </p>
          </button>

          {/* Confirm Mode */}
          <button
            onClick={() => setExecutionMode('confirm')}
            className={`p-4 rounded-borax-card border text-left transition-all ${
              executionMode === 'confirm'
                ? 'bg-amber-500/15 border-amber-500/60 shadow-lg shadow-amber-500/10'
                : 'bg-borax-input border-borax-border hover:border-borax-purple/40'
            }`}
          >
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm mb-2 tracking-borax">
              <AlertTriangle size={18} strokeWidth={2} />
              <span>Confirmar (Confirm)</span>
            </div>
            <p className="text-xs text-borax-gray-muted leading-relaxed tracking-borax">
              Gera o plano de ação, mas exibe um popup solicitando autorização do usuário antes de alterar o disco.
            </p>
          </button>

          {/* Unrestricted Mode */}
          <button
            onClick={() => setExecutionMode('unrestricted')}
            className={`p-4 rounded-borax-card border text-left transition-all ${
              executionMode === 'unrestricted'
                ? 'bg-red-500/15 border-red-500/60 shadow-lg shadow-red-500/10'
                : 'bg-borax-input border-borax-border hover:border-borax-purple/40'
            }`}
          >
            <div className="flex items-center gap-2 text-red-400 font-bold text-sm mb-2 tracking-borax">
              <Unlock size={18} strokeWidth={2} />
              <span>Sem Restrições</span>
            </div>
            <p className="text-xs text-borax-gray-muted leading-relaxed tracking-borax">
              Modo desenvolvedor sem trava de pastas. O usuário assume responsabilidade total pela execução.
            </p>
          </button>
        </div>

        {/* Custom Allowed Paths Manager */}
        <div className="bg-borax-input p-4 rounded-borax-input border border-borax-border space-y-3">
          <label className="text-xs font-semibold text-borax-gray-light block tracking-borax">
            Pastas Adicionais Permitidas (allowed_paths):
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={newPathInput}
              onChange={(e) => setNewPathInput(e.target.value)}
              placeholder="C:\Users\Jr\Projetos ou /home/user/workspace"
              className="flex-1 bg-borax-surface border border-borax-border text-borax-gray-light text-xs p-2.5 rounded-borax-input focus:outline-none focus:border-borax-purple tracking-borax"
            />
            <button
              onClick={handleAddPath}
              className="px-4 py-2.5 rounded-borax-btn borax-btn-secondary font-semibold text-xs flex items-center gap-1.5 tracking-borax"
            >
              <Plus size={16} strokeWidth={2} />
              <span>Adicionar</span>
            </button>
          </div>

          <div className="space-y-1.5">
            {allowedPaths.map((path, idx) => (
              <div key={idx} className="flex items-center justify-between bg-borax-surface p-2.5 rounded-xl border border-borax-border text-xs font-mono text-borax-gray-light">
                <span>{path}</span>
                <button onClick={() => handleRemovePath(path)} className="text-red-400 hover:text-red-300">
                  <Trash2 size={14} strokeWidth={2} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Execution Area */}
      <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2 tracking-borax">
          <Terminal className="text-borax-lilac-light" size={20} strokeWidth={2} />
          <span>Executar Automação Desktop</span>
        </h3>

        <div className="flex gap-2">
          <input
            type="text"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunAgent()}
            placeholder="Ex: Organize meus arquivos PDF na pasta Downloads em subpastas por mês"
            disabled={isExecuting}
            className="flex-1 bg-borax-input border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple tracking-borax"
          />
          <button
            onClick={handleRunAgent}
            disabled={isExecuting || !instruction.trim()}
            className="px-5 py-2.5 rounded-borax-btn bg-borax-gradient text-white font-semibold text-xs tracking-borax flex items-center gap-2 shadow-lg shadow-borax-purple/20 hover:scale-[1.02] transition-transform duration-200 ease-out disabled:opacity-50"
          >
            <Play size={16} strokeWidth={2} />
            <span>Executar Agente</span>
          </button>
        </div>

        {errorMessage && (
          <div className="p-4 rounded-borax-input bg-red-500/10 border border-red-500/30 text-xs font-mono text-red-400">
            ❌ {errorMessage}
          </div>
        )}

        {executionResult && (
          <div className="bg-borax-input p-4 rounded-borax-input border border-borax-border space-y-3 text-xs">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold tracking-borax">
              <CheckCircle2 size={16} strokeWidth={2} />
              <span>Automação Executada! ({executionResult.actions_executed_count || 0} ações)</span>
            </div>
            <pre className="text-borax-gray-light font-mono text-[11px] overflow-x-auto p-3 bg-borax-surface rounded-xl border border-borax-border custom-scrollbar">
              {JSON.stringify(executionResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
