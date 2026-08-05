import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function FileDropzone({ onIngestSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [ingestedFiles, setIngestedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = async (file) => {
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf' && ext !== 'txt' && ext !== 'docx') {
      setStatusMsg({ type: 'error', text: 'Apenas arquivos PDF, TXT ou DOCX são permitidos.' });
      return;
    }

    setUploading(true);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/ingest', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao ingerir arquivo.');

      setStatusMsg({ type: 'success', text: `${file.name} (${data.chunks_count} chunks)` });
      setIngestedFiles((prev) => [...prev, { name: file.name, chunks: data.chunks_count }]);
      if (onIngestSuccess) onIngestSuccess(data);
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          Ingestão RAG (Tradutor)
        </h3>
        <span className="text-xs text-gray-400">PDF, TXT ou DOCX</span>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: isDragging ? '2px dashed #6366F1' : '1px dashed rgba(255, 255, 255, 0.15)',
          backgroundColor: isDragging ? 'rgba(99, 102, 241, 0.08)' : 'rgba(255, 255, 255, 0.02)'
        }}
        className="p-4 rounded-xl cursor-pointer transition-all duration-200 text-center flex flex-col items-center justify-center min-h-[100px]"
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.txt,.docx"
          className="hidden"
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-2 text-indigo-400">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="text-xs font-medium">Extraindo texto e gerando vetores no LanceDB...</span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            <Upload className="w-6 h-6 text-gray-400 hover:text-indigo-400 transition-colors" />
            <p className="text-xs text-gray-300 font-medium">
              Arraste seu PDF, TXT ou DOCX aqui ou <span className="text-indigo-400 underline">clique para procurar</span>
            </p>
          </div>
        )}
      </div>

      {statusMsg && (
        <div
          className={`flex items-center gap-2 p-2.5 rounded-lg text-xs font-medium border ${
            statusMsg.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
          }`}
        >
          {statusMsg.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          )}
          <span className="truncate">{statusMsg.text}</span>
        </div>
      )}

      {ingestedFiles.length > 0 && (
        <div className="mt-1 flex flex-col gap-1.5">
          <span className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">
            Arquivos Ingeridos (~/.app_data/lancedb):
          </span>
          <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
            {ingestedFiles.map((file, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-800/80 border border-slate-700 text-[11px] text-gray-300"
              >
                <FileText className="w-3 h-3 text-cyan-400" />
                {file.name} ({file.chunks} chunks)
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
