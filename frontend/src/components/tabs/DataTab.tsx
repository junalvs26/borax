import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { analyzeData } from '../../services/api';
import { DataAnalyzeResponse } from '../../types';
import { DragAndDropZone } from '../DragAndDropZone';
import { Table, Search, Terminal, CheckCircle2, FileSpreadsheet } from 'lucide-react';

export const DataTab: React.FC = () => {
  const { selectedModel } = useApp();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<DataAnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
    setResult(null);
    setErrorMessage(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile || !query.trim()) return;
    setIsProcessing(true);
    setErrorMessage(null);
    setResult(null);

    try {
      const res = await analyzeData(selectedFile, undefined, query.trim(), selectedModel);
      setResult(res);
    } catch (e: any) {
      setErrorMessage(e.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex-1 p-6 bg-borax-bg overflow-y-auto space-y-6 custom-scrollbar">
      <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
        <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2 tracking-borax">
          <Table className="text-borax-lilac-light" size={24} strokeWidth={2} />
          <span>Analista de Dados Pesados (DuckDB + Polars)</span>
        </h2>
        <p className="text-xs text-borax-gray-muted mb-4 tracking-borax">
          Consultas ultrarrápidas em planilhas sem limite de tamanho usando Text-to-SQL do Ollama local.
        </p>

        <DragAndDropZone
          acceptText=".csv, .parquet, .xlsx, .json"
          onFileSelected={handleFileSelected}
          isProcessing={isProcessing}
          title={selectedFile ? `Planilha Selecionada: ${selectedFile.name}` : "Arraste sua planilha (CSV, Parquet, XLSX, JSON)"}
          subtitle="Suporta leitura ultrarrápida via DuckDB & Polars"
        />

        {selectedFile && (
          <div className="mt-4 p-3 rounded-borax-input bg-borax-input border border-borax-border flex items-center justify-between text-xs tracking-borax">
            <div className="flex items-center gap-2 text-borax-lilac-light font-semibold">
              <FileSpreadsheet size={16} strokeWidth={2} />
              <span>{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-borax-gray-muted hover:text-white"
            >
              Trocar arquivo
            </button>
          </div>
        )}

        <div className="mt-4 flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
            placeholder="Faça uma pergunta sobre a planilha (ex: Qual a soma das vendas por estado?)"
            disabled={isProcessing || !selectedFile}
            className="flex-1 bg-borax-input border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple disabled:opacity-50 tracking-borax"
          />
          <button
            onClick={handleAnalyze}
            disabled={isProcessing || !selectedFile || !query.trim()}
            className="px-5 py-2.5 rounded-borax-btn bg-borax-gradient text-white font-semibold text-xs tracking-borax flex items-center gap-2 shadow-lg shadow-borax-purple/20 hover:scale-[1.02] transition-transform duration-200 ease-out disabled:opacity-50"
          >
            <Search size={16} strokeWidth={2} />
            <span>Analisar Dados</span>
          </button>
        </div>

        {isProcessing && (
          <div className="mt-4 p-4 rounded-borax-input bg-borax-input border border-borax-border text-xs font-mono text-borax-lilac-light flex items-center gap-3">
            <div className="w-4 h-4 border-2 border-borax-lilac-light border-t-transparent rounded-full animate-spin" />
            <span>Gerando consulta SQL com Ollama e executando no DuckDB...</span>
          </div>
        )}

        {errorMessage && (
          <div className="mt-4 p-4 rounded-borax-input bg-red-500/10 border border-red-500/30 text-xs font-mono text-red-400">
            ❌ {errorMessage}
          </div>
        )}
      </div>

      {/* Result Output */}
      {result && (
        <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2 tracking-borax">
              <CheckCircle2 className="text-emerald-400" size={20} strokeWidth={2} />
              <span>Resultado da Análise</span>
            </h3>
            <span className="text-xs text-borax-gray-muted font-mono">{result.total_rows} linhas encontradas</span>
          </div>

          <div className="bg-borax-input p-3.5 rounded-borax-input border border-borax-border">
            <div className="flex items-center gap-2 text-xs font-mono text-borax-lilac-light mb-1">
              <Terminal size={14} strokeWidth={2} />
              <span>Consulta SQL Executada:</span>
            </div>
            <code className="text-xs font-mono text-borax-gray-light break-all">{result.sql_executed}</code>
          </div>

          {/* Table display */}
          <div className="overflow-x-auto rounded-borax-input border border-borax-border max-h-64 overflow-y-auto custom-scrollbar">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-borax-input text-borax-gray-muted border-b border-borax-border font-mono">
                  {result.columns.map((col, i) => (
                    <th key={i} className="p-3 font-semibold">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-borax-border bg-borax-surface">
                {result.results.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-borax-input/60 text-borax-gray-light">
                    {result.columns.map((col, cIdx) => (
                      <td key={cIdx} className="p-3 font-mono text-borax-gray-light">{String(row[col] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
