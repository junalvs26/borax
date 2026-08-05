import React, { useEffect, useState } from 'react';
import { Cpu, RefreshCw, AlertCircle } from 'lucide-react';

export default function ModelSelector({ selectedModel, setSelectedModel, backendStatus }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchModels = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/models');
      if (!res.ok) throw new Error('Falha ao obter lista de modelos');
      const data = await res.json();
      setModels(data.models || []);
      if (data.models && data.models.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0].name);
      }
    } catch (err) {
      setError('Ollama/Backend offline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, [backendStatus]);

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-sm text-gray-300 font-medium">
        <Cpu className="w-4 h-4 text-indigo-400" />
        <span>Modelo:</span>
      </div>

      <div className="relative flex items-center">
        {loading ? (
          <div className="text-xs text-gray-400 animate-pulse px-3 py-1.5 bg-slate-800/60 rounded-md">
            Carregando modelos...
          </div>
        ) : models.length > 0 ? (
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="select-dark pr-8 font-mono text-xs cursor-pointer"
          >
            {models.map((m) => (
              <option key={m.name} value={m.name}>
                {m.name} ({(m.size / (1024 * 1024 * 1024)).toFixed(1)} GB)
              </option>
            ))}
          </select>
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-md">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Nenhum modelo encontrado no Ollama</span>
          </div>
        )}

        <button
          onClick={fetchModels}
          title="Atualizar lista de modelos"
          className="ml-2 p-1.5 hover:bg-slate-800 rounded-md text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </div>
  );
}
