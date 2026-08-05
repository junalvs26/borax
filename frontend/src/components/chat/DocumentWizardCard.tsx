import React, { useState } from 'react';
import { DocumentWizardPreferences } from '../../types';
import { Sparkles, FileText, Check, Rocket, HelpCircle, BookOpen, Layers } from 'lucide-react';

interface DocumentWizardCardProps {
  promptOriginal: string;
  initialPreferences: DocumentWizardPreferences;
  onConfirm: (prefs: DocumentWizardPreferences) => void;
  disabled?: boolean;
}

export const DocumentWizardCard: React.FC<DocumentWizardCardProps> = ({
  promptOriginal,
  initialPreferences,
  onConfirm,
  disabled = false
}) => {
  const [theme, setTheme] = useState(initialPreferences.theme || (promptOriginal && !promptOriginal.startsWith('@') ? promptOriginal : ''));
  const [sections, setSections] = useState(initialPreferences.sections || '');
  const [docType, setDocType] = useState<DocumentWizardPreferences['document_type']>(initialPreferences.document_type || 'technical');
  const [tone, setTone] = useState<DocumentWizardPreferences['tone']>(initialPreferences.tone || 'scientific');
  const [format, setFormat] = useState<DocumentWizardPreferences['export_format']>(initialPreferences.export_format || 'docx');
  const [errorMsg, setErrorMsg] = useState('');

  const docTypeOptions = [
    { id: 'abnt', label: 'Acadêmico ABNT', desc: 'Estrutura formal ABNT com citações' },
    { id: 'technical', label: 'Relatório Técnico', desc: 'Especificações, métricas e análises' },
    { id: 'proposal', label: 'Proposta Comercial', desc: 'Objetivos, escopo e termos' },
    { id: 'summary', label: 'Resumo Executivo', desc: 'Síntese concisa em tópicos' }
  ];

  const toneOptions = [
    { id: 'scientific', label: 'Científico / Formal', desc: 'Linguagem impessoal e precisa' },
    { id: 'direct', label: 'Direto e Objetivo', desc: 'Foco em decisões' },
    { id: 'didactic', label: 'Didático / Explicativo', desc: 'Instrutivo com exemplos' }
  ];

  const formatOptions = [
    { id: 'docx', label: 'Word (.docx)' },
    { id: 'pdf', label: 'PDF (.pdf)' },
    { id: 'txt', label: 'Texto (.txt)' }
  ];

  const handleConfirm = () => {
    if (!theme.trim()) {
      setErrorMsg('Por favor, informe o Tema/Assunto principal do trabalho.');
      return;
    }
    setErrorMsg('');
    onConfirm({
      theme: theme.trim(),
      sections: sections.trim(),
      document_type: docType,
      tone,
      export_format: format
    });
  };

  return (
    <div className="my-3 p-5 rounded-2xl bg-[#14111F] border border-[#2B2443] shadow-2xl space-y-5 max-w-xl text-gray-200">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-[#2B2443] pb-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-md">
          <Sparkles size={20} />
        </div>
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-white font-mono flex items-center gap-2">
            Moldagem Interativa de Documentos
            <span className="text-[9px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono">
              REDAÇÃO LLM
            </span>
          </h3>
          <p className="text-[11px] text-gray-400">
            Coleta obrigatória de requisitos para redação articulada pela IA:
          </p>
        </div>
      </div>

      {/* Tema / Assunto Principal */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5 font-mono">
          <BookOpen size={13} />
          1. Qual é o Tema / Assunto Principal do trabalho? *
        </label>
        <input
          type="text"
          value={theme}
          onChange={(e) => { setTheme(e.target.value); setErrorMsg(''); }}
          placeholder="Ex: Impacto da Inteligência Artificial na Medicina Diagnóstica"
          disabled={disabled}
          className="w-full bg-[#0B0A12] border border-[#372D5C] focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none font-sans shadow-inner"
        />
        {errorMsg && <p className="text-[10px] text-red-400 font-mono mt-1">{errorMsg}</p>}
      </div>

      {/* Seções / Tópicos Desejados */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1.5 font-mono">
          <Layers size={13} />
          2. Quais Seções ou Tópicos deseja desenvolver? (Opcional):
        </label>
        <input
          type="text"
          value={sections}
          onChange={(e) => setSections(e.target.value)}
          placeholder="Ex: Introdução, Tecnologias de Imagem, Ética e Privacidade, Conclusão"
          disabled={disabled}
          className="w-full bg-[#0B0A12] border border-[#2B2443] focus:border-purple-500 rounded-xl px-3.5 py-2 text-xs text-gray-200 placeholder-gray-500 focus:outline-none font-sans"
        />
      </div>

      {/* Tipo de Documento */}
      <div className="space-y-2">
        <label className="text-[11px] font-bold uppercase tracking-wider text-cyan-300 flex items-center gap-1.5 font-mono">
          <FileText size={13} />
          3. Tipo e Estrutura de Documento:
        </label>
        <div className="grid grid-cols-2 gap-2">
          {docTypeOptions.map((opt) => (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              onClick={() => setDocType(opt.id as any)}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                docType === opt.id
                  ? 'bg-cyan-500/20 border-cyan-500 text-white shadow-md shadow-cyan-500/20'
                  : 'bg-[#0B0A12] border-[#2B2443] text-gray-400 hover:border-cyan-500/30 hover:text-gray-200'
              }`}
            >
              <div className="text-xs font-bold font-mono flex items-center justify-between">
                <span>{opt.label}</span>
                {docType === opt.id && <Check size={12} className="text-cyan-400" />}
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5">{opt.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tom de Voz */}
      <div className="space-y-2">
        <label className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5 font-mono">
          <Sparkles size={13} />
          4. Tom de Voz da Escrita:
        </label>
        <div className="grid grid-cols-3 gap-2">
          {toneOptions.map((opt) => (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              onClick={() => setTone(opt.id as any)}
              className={`p-2 rounded-xl border text-left transition-all ${
                tone === opt.id
                  ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md shadow-indigo-600/20'
                  : 'bg-[#0B0A12] border-[#2B2443] text-gray-400 hover:border-indigo-500/30 hover:text-gray-200'
              }`}
            >
              <div className="text-xs font-bold font-mono flex items-center justify-between">
                <span>{opt.label}</span>
                {tone === opt.id && <Check size={12} className="text-indigo-400" />}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Formato Final */}
      <div className="space-y-2">
        <label className="text-[11px] font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1.5 font-mono">
          <FileText size={13} />
          5. Formato do Arquivo de Saída:
        </label>
        <div className="flex items-center gap-2">
          {formatOptions.map((opt) => (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              onClick={() => setFormat(opt.id as any)}
              className={`flex-1 py-2 px-3 rounded-xl border text-center font-mono text-xs font-bold transition-all ${
                format === opt.id
                  ? 'bg-purple-600/20 border-purple-500 text-purple-200 shadow-md shadow-purple-600/20'
                  : 'bg-[#0B0A12] border-[#2B2443] text-gray-400 hover:border-purple-500/30'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Confirm Action Button */}
      <button
        type="button"
        disabled={disabled}
        onClick={handleConfirm}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-xl shadow-indigo-600/25 hover:scale-[1.01] disabled:opacity-50"
      >
        <Rocket size={16} />
        <span>🚀 Confirmar e Gerar Documento Final</span>
      </button>
    </div>
  );
};
