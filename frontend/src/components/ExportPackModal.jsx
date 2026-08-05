import React, { useState, useRef } from 'react';
import { Package, X, Download, Upload, Loader2, CheckCircle, FileText } from 'lucide-react';

export default function ExportPackModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('export'); // 'export' | 'import'
  const [moduleName, setModuleName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('Você é um assistente especialista neste pacote de conhecimento local.');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleExport = async (e) => {
    e.preventDefault();
    if (!moduleName.trim()) {
      setError('Por favor, digite o nome do módulo.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      const response = await fetch('http://localhost:8000/api/export-pack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_name: moduleName.trim(),
          description: description.trim(),
          system_prompt: systemPrompt.trim(),
          table_name: 'knowledge_base'
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erro ao exportar .knpack');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${moduleName.toLowerCase().replace(/\s+/g, '_')}.knpack`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setSuccessMsg('Pacote .knpack gerado e baixado com sucesso!');
      setTimeout(() => {
        setSuccessMsg('');
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleImportFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccessMsg('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/import-pack', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro ao importar .knpack');

      setSuccessMsg(`Módulo '${data.manifest?.module_name}' (${data.chunks_imported} chunks) importado no LanceDB!`);
      setTimeout(() => {
        setSuccessMsg('');
        onClose();
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="glass-panel w-full max-w-md p-6 relative border border-indigo-500/30 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Tab Headers */}
        <div className="flex border-b border-white/10 mb-4 pb-2 gap-4">
          <button
            onClick={() => { setActiveTab('export'); setError(''); setSuccessMsg(''); }}
            className={`flex items-center gap-2 text-sm font-semibold pb-1 border-b-2 transition-all ${
              activeTab === 'export'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Download className="w-4 h-4" />
            Exportar .knpack
          </button>

          <button
            onClick={() => { setActiveTab('import'); setError(''); setSuccessMsg(''); }}
            className={`flex items-center gap-2 text-sm font-semibold pb-1 border-b-2 transition-all ${
              activeTab === 'import'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Upload className="w-4 h-4" />
            Importar .knpack
          </button>
        </div>

        {activeTab === 'export' ? (
          <form onSubmit={handleExport} className="flex flex-col gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Nome do Módulo
              </label>
              <input
                type="text"
                placeholder="ex: Tradutor_Tecnico_v1"
                value={moduleName}
                onChange={(e) => setModuleName(e.target.value)}
                className="input-dark w-full text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                Descrição Breve
              </label>
              <input
                type="text"
                placeholder="ex: Pacote vetorial com documentação do sistema"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input-dark w-full text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1">
                System Prompt do Módulo
              </label>
              <textarea
                rows={3}
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="input-dark w-full text-xs font-mono resize-none"
              />
            </div>

            {error && (
              <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg">
                {error}
              </div>
            )}

            {successMsg && (
              <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-lg font-medium">
                <CheckCircle className="w-4 h-4" />
                {successMsg}
              </div>
            )}

            <div className="flex justify-end gap-2 mt-2">
              <button type="button" onClick={onClose} className="btn-secondary text-xs">
                Cancelar
              </button>
              <button type="submit" disabled={loading} className="btn-primary text-xs">
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Compilando ZIP...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Exportar Pacote</span>
                  </>
                )}
              </button>
            </div>
          </form>
        ) : (
          <div className="flex flex-col gap-4 py-2">
            <p className="text-xs text-gray-400 leading-relaxed">
              Selecione um arquivo <code className="text-cyan-400 bg-slate-800 px-1 py-0.5 rounded">.knpack</code> compilado para restaurar seus vetores e prompts no LanceDB local.
            </p>

            <div
              onClick={() => fileInputRef.current?.click()}
              className="p-6 rounded-xl border border-dashed border-cyan-500/40 bg-cyan-500/5 hover:bg-cyan-500/10 cursor-pointer flex flex-col items-center gap-2 transition-all"
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImportFile}
                accept=".knpack"
                className="hidden"
              />
              {loading ? (
                <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
              ) : (
                <Package className="w-8 h-8 text-cyan-400" />
              )}
              <span className="text-xs font-semibold text-gray-200">
                {loading ? 'Restaurando vetores no LanceDB...' : 'Clique para selecionar o arquivo .knpack'}
              </span>
            </div>

            {error && (
              <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg">
                {error}
              </div>
            )}

            {successMsg && (
              <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-lg font-medium">
                <CheckCircle className="w-4 h-4" />
                {successMsg}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
