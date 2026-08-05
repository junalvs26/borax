import React, { useState } from 'react';
import { ArtifactFilePayload } from './ArtifactCard';
import { X, Download, FileText, Table as TableIcon, Layers, FileSpreadsheet, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ArtifactViewerProps {
  file: ArtifactFilePayload;
  documentText?: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  file,
  documentText = '',
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'outline' | 'formulas'>('preview');
  const fmt = (file.file_format || 'docx').toLowerCase().replace('.', '');
  const downloadUrl = file.download_url || `http://127.0.0.1:8000/api/file/download/${file.filename}`;

  if (!isOpen) return null;

  // Extract headings (#, ##, ###) for structure outline
  const headings = documentText
    ? documentText
        .split('\n')
        .filter((l) => l.strip?.() !== undefined && l.trim().startswith?.('#'))
        .map((l) => l.trim())
    : [];

  const extractHeadingsList = () => {
    if (!documentText) return [];
    return documentText
      .split('\n')
      .filter((line) => line.trim().startsWith('#'))
      .map((line) => {
        const level = line.indexOf(' ');
        return {
          level: level > 0 ? level : 1,
          text: line.replace(/^#+\s*/, '')
        };
      });
  };

  const outline = extractHeadingsList();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="bg-[#14111F] border border-[#372D5C] w-full max-w-4xl h-[85vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden text-gray-200">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#2B2443] bg-[#0E0C17]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-mono font-bold text-xs uppercase shadow-md">
              {fmt}
            </div>
            <div>
              <h3 className="text-sm font-bold text-white font-mono">{file.filename}</h3>
              <p className="text-[11px] text-gray-400 font-mono">
                Estrutura Compilada via Engine BORAX • {file.page_count ? `${file.page_count} Páginas` : 'Alta Performance'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href={downloadUrl}
              download={file.filename}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs font-mono flex items-center gap-2 shadow-lg transition-transform hover:scale-105"
            >
              <Download size={13} />
              <span>Baixar</span>
            </a>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-gray-400 hover:text-white bg-[#1A162B] border border-[#2B2443] hover:border-gray-500 transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 px-6 py-2.5 bg-[#171324] border-b border-[#2B2443] text-xs font-mono">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-colors ${
              activeTab === 'preview'
                ? 'bg-indigo-600 text-white font-bold shadow-md'
                : 'text-gray-400 hover:text-white hover:bg-[#231C38]'
            }`}
          >
            <FileText size={14} />
            <span>Prévia do Documento</span>
          </button>

          <button
            onClick={() => setActiveTab('outline')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-colors ${
              activeTab === 'outline'
                ? 'bg-indigo-600 text-white font-bold shadow-md'
                : 'text-gray-400 hover:text-white hover:bg-[#231C38]'
            }`}
          >
            <Layers size={14} />
            <span>Sumário / Tópicos ({outline.length})</span>
          </button>

          {fmt === 'xlsx' && (
            <button
              onClick={() => setActiveTab('formulas')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-colors ${
                activeTab === 'formulas'
                  ? 'bg-emerald-600 text-white font-bold shadow-md'
                  : 'text-gray-400 hover:text-white hover:bg-[#231C38]'
              }`}
            >
              <FileSpreadsheet size={14} />
              <span>Fórmulas & Células Excel</span>
            </button>
          )}
        </div>

        {/* Modal Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-[#0E0C17]">
          {activeTab === 'preview' && (
            <div className="prose prose-invert max-w-none text-xs leading-relaxed font-sans p-6 rounded-2xl bg-[#14111F] border border-[#2B2443]">
              {documentText ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({ node, ...props }) => (
                      <div className="overflow-x-auto my-4 rounded-xl border border-[#2B2443]">
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
                    )
                  }}
                >
                  {documentText}
                </ReactMarkdown>
              ) : (
                <p className="text-gray-400 font-mono text-center py-8">
                  Estrutura compilada com sucesso. Faça o download para visualizar no formato nativo ({fmt.toUpperCase()}).
                </p>
              )}
            </div>
          )}

          {activeTab === 'outline' && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300 font-mono mb-3">
                Estrutura Hieraquica dos Capítulos e Seções:
              </h4>
              {outline.length > 0 ? (
                <div className="space-y-2">
                  {outline.map((h, i) => (
                    <div
                      key={i}
                      style={{ paddingLeft: `${(h.level - 1) * 1.25}rem` }}
                      className="flex items-center gap-2 p-2.5 rounded-xl bg-[#14111F] border border-[#2B2443] text-xs font-mono text-gray-200"
                    >
                      <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                      <span className="font-bold">{h.text}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400 font-mono p-4 rounded-xl bg-[#14111F] border border-[#2B2443]">
                  Nenhum título hierárquico detectado no texto de entrada.
                </p>
              )}
            </div>
          )}

          {activeTab === 'formulas' && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono">
                Detecção de Fórmulas e Cálculos Excel (`openpyxl`):
              </h4>
              <div className="p-4 rounded-2xl bg-[#14111F] border border-emerald-500/30 space-y-2 font-mono text-xs text-emerald-300">
                <div className="flex items-center gap-2">
                  <Check size={14} />
                  <span>Fórmulas nativas ativadas: `=SUM(...)`, `=AVERAGE(...)`, `=B2*C2`</span>
                </div>
                <div className="flex items-center gap-2 text-gray-300">
                  <Check size={14} className="text-emerald-400" />
                  <span>Largura das colunas auto-ajustada dinamicamente</span>
                </div>
                <div className="flex items-center gap-2 text-gray-300">
                  <Check size={14} className="text-emerald-400" />
                  <span>Estilização de cabeçalho roxo escuro (#14111F)</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
