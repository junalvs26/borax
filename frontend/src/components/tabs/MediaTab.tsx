import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { transcribeMedia } from '../../services/api';
import { MediaTranscribeResponse } from '../../types';
import { DragAndDropZone } from '../DragAndDropZone';
import { Video, Youtube, Play, FileText, Clock } from 'lucide-react';

export const MediaTab: React.FC = () => {
  const { activeTable } = useApp();
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<MediaTranscribeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleMediaFile = async (file: File) => {
    setIsProcessing(true);
    setErrorMessage(null);
    setResult(null);

    try {
      const res = await transcribeMedia(file, undefined, activeTable);
      setResult(res);
    } catch (e: any) {
      setErrorMessage(e.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleYoutubeSubmit = async () => {
    if (!youtubeUrl.trim()) return;
    setIsProcessing(true);
    setErrorMessage(null);
    setResult(null);

    try {
      const res = await transcribeMedia(undefined, youtubeUrl.trim(), activeTable);
      setResult(res);
      setYoutubeUrl('');
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
          <Video className="text-borax-lilac-light" size={24} strokeWidth={2} />
          <span>Módulo de Mídia & YouTube (Whisper Offline)</span>
        </h2>
        <p className="text-xs text-borax-gray-muted mb-4 tracking-borax">
          Transcrição de fala para texto 100% offline via Faster-Whisper e indexação automática no RAG LanceDB.
        </p>

        {/* YouTube Input */}
        <div className="bg-borax-input p-4 rounded-borax-input border border-borax-border space-y-2">
          <label className="text-xs font-semibold text-borax-gray-light flex items-center gap-2 tracking-borax">
            <Youtube size={18} className="text-red-500" strokeWidth={2} />
            <span>Extrair Áudio de Vídeo do YouTube:</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              disabled={isProcessing}
              className="flex-1 bg-borax-surface border border-borax-border text-borax-gray-light text-xs p-3 rounded-borax-input focus:outline-none focus:border-borax-purple tracking-borax"
            />
            <button
              onClick={handleYoutubeSubmit}
              disabled={isProcessing || !youtubeUrl.trim()}
              className="px-5 py-2.5 rounded-borax-btn bg-red-600 hover:bg-red-500 text-white font-semibold text-xs tracking-borax flex items-center gap-2 disabled:opacity-50 transition-all shadow-lg shadow-red-500/20"
            >
              <Play size={16} strokeWidth={2} />
              <span>Transcrever YouTube</span>
            </button>
          </div>
        </div>

        {/* Drag & Drop File */}
        <DragAndDropZone
          acceptText=".mp3, .wav, .mp4, .mkv, .m4a, .aac"
          onFileSelected={handleMediaFile}
          isProcessing={isProcessing}
          title="Arraste seu arquivo de áudio ou vídeo local"
          subtitle="Suporta MP3, WAV, MP4, MKV com Faster-Whisper"
        />

        {isProcessing && (
          <div className="mt-4 p-4 rounded-borax-input bg-borax-input border border-borax-border text-xs font-mono text-borax-lilac-light flex items-center gap-3">
            <div className="w-4 h-4 border-2 border-borax-lilac-light border-t-transparent rounded-full animate-spin" />
            <span>Processando áudio com Faster-Whisper offline...</span>
          </div>
        )}

        {errorMessage && (
          <div className="mt-4 p-4 rounded-borax-input bg-red-500/10 border border-red-500/30 text-xs font-mono text-red-400">
            ❌ {errorMessage}
          </div>
        )}
      </div>

      {/* Result Display */}
      {result && (
        <div className="bg-borax-surface border border-borax-border p-6 rounded-borax-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2 tracking-borax">
              <FileText className="text-borax-lilac-light" size={20} strokeWidth={2} />
              <span>Resultado da Transcrição</span>
            </h3>
            <div className="flex items-center gap-3 text-xs text-borax-gray-muted font-mono">
              <span>Idioma: {result.language.toUpperCase()} ({result.language_probability * 100}%)</span>
              <span>•</span>
              <span>Duração: {result.duration}s</span>
            </div>
          </div>

          <div className="p-4 rounded-borax-input bg-borax-input border border-borax-border text-xs text-borax-gray-light leading-relaxed font-sans max-h-48 overflow-y-auto custom-scrollbar tracking-borax">
            {result.full_transcript}
          </div>

          <div>
            <h4 className="text-xs font-semibold text-borax-gray-muted mb-2 flex items-center gap-1.5 tracking-borax">
              <Clock size={14} className="text-borax-lilac-light" strokeWidth={2} />
              <span>Segmentos com Timestamps ({result.segments_count}):</span>
            </h4>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
              {result.segments.map((seg, idx) => (
                <div key={idx} className="flex items-start gap-3 bg-borax-input p-2.5 rounded-xl border border-borax-border text-xs">
                  <span className="text-borax-lilac-light font-mono shrink-0">[{seg.start}s - {seg.end}s]</span>
                  <span className="text-borax-gray-light tracking-borax">{seg.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
