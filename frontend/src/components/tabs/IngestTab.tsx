import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { ingestFile, exportKnpack, importKnpack } from '../../services/api';
import { DragAndDropZone } from '../DragAndDropZone';
import { FileCheck, Download, Package } from 'lucide-react';

export const IngestTab: React.FC = () => {
  const { activeTable } = useApp();
  const [isProcessing, setIsProcessing] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  
  const [moduleName, setModuleName] = useState('Modulo_Especialista');
  const [systemPrompt, setSystemPrompt] = useState('Você é um assistente especialista no conhecimento deste pacote.');
  const [description, setDescription] = useState('Pacote compilado .knpack de conhecimento RAG');
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const handleFileIngest = async (file: File) => {
    if (file.name.endsWith('.knpack')) {
      handleImportKnpack(file);
      return;
    }

    setIsProcessing(true);
    setIngestStatus('Ingerindo e gerando embeddings no LanceDB...');
    try {
      const res = await ingestFile(file, activeTable);
      setIngestStatus(`✅ ${res.filename} ingerido com sucesso! ${res.chunks_count} chunks gravados no LanceDB.`);
    } catch (e: any) {
      setIngestStatus(`❌ Erro: ${e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleImportKnpack = async (file: File) => {
    setIsProcessing(true);
    setIngestStatus('Importando pacote .knpack...');
    try {
      const res = await importKnpack(file);
      setIngestStatus(`✅ Módulo '${res.manifest?.module_name || file.name}' importado com sucesso no LanceDB!`);
    } catch (e: any) {
      setIngestStatus(`❌ Erro ao importar .knpack: ${e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async () => {
    if (!moduleName.trim()) return;
    setIsProcessing(true);
    setExportMessage('Compactando vetores LanceDB e manifest.json em .knpack...');
    try {
      const blob = await exportKnpack(moduleName, systemPrompt, activeTable, description);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${moduleName}.knpack`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setExportMessage(`✅ Pacote ${moduleName}.knpack baixado com sucesso!`);
    } catch (e: any) {
      setExportMessage(`❌ Erro ao exportar: ${e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex-1 p-6 bg-borax-bg overflow-y-auto space-y-6 custom-scrollbar">
      <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
        <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2 tracking-borax">
          <FileCheck className="text-borax-lilac-light" size={24} strokeWidth={2} />
          <span>Tradutor de Conteúdo & Ingestão RAG</span>
        </h2>
        <p className="text-xs text-borax-gray-muted mb-4 tracking-borax">
          Divisão automática em chunks (500-1000 caracteres) e vetorização no LanceDB local.
        </p>

        <DragAndDropZone
          acceptText=".pdf, .txt, .docx, .knpack"
          onFileSelected={handleFileIngest}
          isProcessing={isProcessing}
          title="Arraste arquivos PDF, TXT, DOCX ou pacotes .knpack"
          subtitle="Os vetores serão gravados instantaneamente no LanceDB"
        />

        {ingestStatus && (
          <div className="mt-4 p-4 rounded-borax-input bg-borax-input border border-borax-border text-xs font-mono text-borax-lilac-light">
            {ingestStatus}
          </div>
        )}
      </div>

      {/* Export Pack Section */}
      <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2 tracking-borax">
          <Package className="text-borax-lilac-light" size={22} strokeWidth={2} />
          <span>Exportar Conhecimento (.knpack)</span>
        </h3>
        <p className="text-xs text-borax-gray-muted tracking-borax">
          Empacote a tabela ativa do LanceDB e o prompt do módulo especialista em um arquivo ZIP .knpack.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-borax-gray-muted block mb-1 tracking-borax">Nome do Módulo:</label>
            <input
              type="text"
              value={moduleName}
              onChange={(e) => setModuleName(e.target.value)}
              className="w-full bg-borax-input border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple tracking-borax"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-borax-gray-muted block mb-1 tracking-borax">Descrição Breve:</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-borax-input border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple tracking-borax"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-borax-gray-muted block mb-1 tracking-borax">System Prompt do Módulo:</label>
          <textarea
            rows={3}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full bg-borax-input border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple resize-none tracking-borax"
          />
        </div>

        {exportMessage && (
          <div className="p-3 rounded-borax-input bg-borax-input border border-borax-border text-xs font-mono text-emerald-400">
            {exportMessage}
          </div>
        )}

        <button
          onClick={handleExport}
          disabled={isProcessing || !moduleName.trim()}
          className="px-5 py-2.5 rounded-borax-btn bg-borax-gradient text-white font-semibold text-xs tracking-borax flex items-center gap-2 shadow-lg shadow-borax-purple/20 hover:scale-[1.02] transition-transform duration-200 ease-out disabled:opacity-50"
        >
          <Download size={16} strokeWidth={2} />
          <span>Exportar Pacote .knpack</span>
        </button>
      </div>
    </div>
  );
};
