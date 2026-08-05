import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { confirmAgentExecution } from '../services/api';
import { ShieldAlert, CheckCircle2, XCircle, Terminal } from 'lucide-react';

export const ConfirmationModal: React.FC = () => {
  const { pendingAgentPlan, setPendingAgentPlan } = useApp();
  const [loading, setLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);

  if (!pendingAgentPlan) return null;

  const handleConfirm = async () => {
    if (!pendingAgentPlan.plan_id) return;
    setLoading(true);
    try {
      const res = await confirmAgentExecution(pendingAgentPlan.plan_id);
      setResultMessage(`Sucesso! ${res.actions_executed_count || 0} ações executadas.`);
      setTimeout(() => {
        setPendingAgentPlan(null);
        setResultMessage(null);
      }, 2000);
    } catch (e: any) {
      setResultMessage(`Erro: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setPendingAgentPlan(null);
  };

  return (
    <div className="fixed inset-0 z-50 bg-borax-bg/85 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-borax-surface border border-borax-border rounded-borax-card p-6 max-w-lg w-full shadow-2xl shadow-borax-purple/10">
        <div className="flex items-center gap-3 text-amber-400 mb-4">
          <ShieldAlert size={28} strokeWidth={2} />
          <div>
            <h3 className="text-lg font-bold text-white tracking-borax">Autorização de Ação Pendente</h3>
            <p className="text-xs text-amber-400/90 font-medium tracking-borax">Modo de Permissão: Confirmar Ações</p>
          </div>
        </div>

        <div className="bg-borax-input p-4 rounded-borax-input border border-borax-border mb-5 space-y-3">
          <div>
            <p className="text-xs text-borax-gray-muted font-semibold mb-1 tracking-borax">Instrução Solicitada:</p>
            <p className="text-sm font-medium text-borax-gray-light tracking-borax">{pendingAgentPlan.instruction}</p>
          </div>

          <div>
            <p className="text-xs text-borax-gray-muted font-semibold mb-2 tracking-borax">Ações a Serem Executadas no Sistema:</p>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
              {pendingAgentPlan.pending_actions?.map((act, idx) => (
                <div key={idx} className="flex items-start gap-2 bg-borax-surface p-2.5 rounded-xl border border-borax-border text-xs font-mono">
                  <Terminal size={14} className="text-borax-lilac-light shrink-0 mt-0.5" strokeWidth={2} />
                  <div className="break-all">
                    <span className="text-borax-lilac-light font-bold">{act.tool}</span>
                    <span className="text-borax-gray-muted">({JSON.stringify(act.args)})</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {resultMessage && (
          <div className="p-3 mb-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium tracking-borax">
            {resultMessage}
          </div>
        )}

        <div className="flex items-center justify-end gap-3">
          <button
            onClick={handleCancel}
            disabled={loading}
            className="px-4 py-2.5 rounded-borax-btn borax-btn-secondary text-xs font-semibold tracking-borax flex items-center gap-1.5"
          >
            <XCircle size={16} strokeWidth={2} />
            <span>Recusar</span>
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="px-5 py-2.5 rounded-borax-btn bg-borax-gradient text-white font-semibold text-xs tracking-borax flex items-center gap-1.5 shadow-lg shadow-borax-purple/20 hover:scale-[1.02] transition-transform duration-200 ease-out disabled:opacity-50"
          >
            <CheckCircle2 size={16} strokeWidth={2} />
            <span>{loading ? 'Executando...' : 'Aprovar & Executar'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
