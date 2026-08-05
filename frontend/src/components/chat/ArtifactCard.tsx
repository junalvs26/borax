import React from 'react';
import { Download, Eye, FileText, Table, FileSpreadsheet, FileCode, CheckCircle2 } from 'lucide-react';

export interface ArtifactFilePayload {
  filename: str;
  file_format: string;
  filepath: string;
  size_bytes?: number;
  page_count?: number;
  line_count?: number;
  download_url?: string;
  message?: string;
}

interface ArtifactCardProps {
  file: ArtifactFilePayload;
  onViewStructure?: () => void;
}

export const ArtifactCard: React.FC<ArtifactCardProps> = ({ file, onViewStructure }) => {
  const fmt = (file.file_format || 'docx').toLowerCase().replace('.', '');
  
  const formatBytes = (bytes?: number) => {
    if (!bytes || bytes === 0) return 'Tamanho desconhecido';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFormatBadge = () => {
    switch (fmt) {
      case 'xlsx':
      case 'xls':
      case 'csv':
        return {
          label: 'XLSX PLANILHA',
          gradient: 'from-emerald-600 to-teal-700',
          borderColor: 'border-emerald-500/40',
          icon: <FileSpreadsheet size={18} className="text-emerald-300" />
        };
      case 'pdf':
        return {
          label: 'PDF TÉCNICO',
          gradient: 'from-rose-600 to-red-700',
          borderColor: 'border-rose-500/40',
          icon: <FileText size={18} className="text-rose-300" />
        };
      case 'docx':
      case 'doc':
      default:
        return {
          label: 'DOCX ABNT',
          gradient: 'from-indigo-600 to-purple-700',
          borderColor: 'border-indigo-500/40',
          icon: <FileText size={18} className="text-indigo-300" />
        };
    }
  };

  const badge = getFormatBadge();
  const downloadUrl = file.download_url || `http://127.0.0.1:8000/api/file/download/${file.filename}`;

  return (
    <div className={`my-3 p-4 rounded-2xl bg-[#14111F] border ${badge.borderColor} shadow-2xl space-y-3 w-full max-w-lg transition-all hover:border-opacity-80`}>
      {/* Top Bar: Icon, File Details & Badge */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${badge.gradient} flex items-center justify-center text-white shrink-0 shadow-lg`}>
            {badge.icon}
          </div>

          <div className="min-w-0">
            <h4 className="text-xs font-bold text-white font-mono truncate" title={file.filename}>
              {file.filename}
            </h4>
            <div className="flex items-center gap-2 mt-0.5 text-[11px] text-gray-400 font-mono">
              <span>{formatBytes(file.size_bytes)}</span>
              <span>•</span>
              {fmt === 'xlsx' ? (
                <span>{file.line_count ? `${file.line_count} Linhas / Fórmulas` : 'Dados com Fórmulas'}</span>
              ) : (
                <span>{file.page_count ? `${file.page_count} ${file.page_count === 1 ? 'Página' : 'Páginas'}` : 'Documento Extenso'}</span>
              )}
            </div>
          </div>
        </div>

        <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider uppercase bg-[#1D1730] text-gray-300 border border-[#372D5C] font-mono shrink-0">
          {badge.label}
        </span>
      </div>

      {/* Status Pill */}
      <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-mono bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20">
        <CheckCircle2 size={13} />
        <span>Artefato gerado e pronto para download na pasta local</span>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-1 border-t border-[#231C38]">
        <a
          href={downloadUrl}
          download={file.filename}
          className="flex-1 py-2 px-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs font-mono flex items-center justify-center gap-2 transition-all hover:scale-[1.02] shadow-md shadow-indigo-600/30"
        >
          <Download size={14} />
          <span>📥 Baixar Arquivo</span>
        </a>

        {onViewStructure && (
          <button
            onClick={onViewStructure}
            className="flex-1 py-2 px-3.5 rounded-xl bg-[#1C172E] hover:bg-[#282142] text-gray-200 hover:text-white border border-[#3B305C] font-semibold text-xs font-mono flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
          >
            <Eye size={14} className="text-indigo-400" />
            <span>👁️ Visualizar Estrutura</span>
          </button>
        )}
      </div>
    </div>
  );
};
