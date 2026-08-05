import React, { useState } from 'react';
import { UploadCloud, File } from 'lucide-react';

interface DragAndDropZoneProps {
  acceptText?: string;
  onFileSelected: (file: File) => void;
  isProcessing?: boolean;
  title?: string;
  subtitle?: string;
}

export const DragAndDropZone: React.FC<DragAndDropZoneProps> = ({
  acceptText = '.pdf, .txt, .docx, .mp3, .mp4, .csv, .parquet, .xlsx, .json, .knpack',
  onFileSelected,
  isProcessing = false,
  title = 'Arraste e solte seu arquivo aqui',
  subtitle = 'ou clique para navegar no seu computador'
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative border-2 border-dashed rounded-borax-card p-8 text-center transition-all duration-300 ${
        isDragOver
          ? 'border-borax-purple bg-borax-purple/10 scale-[1.01]'
          : 'border-borax-border bg-borax-input/50 hover:border-borax-purple/50 hover:bg-borax-input'
      } ${isProcessing ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}
    >
      <input
        type="file"
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isProcessing}
      />
      <div className="flex flex-col items-center justify-center space-y-3 pointer-events-none">
        <div className="w-14 h-14 rounded-full bg-borax-surface border border-borax-border flex items-center justify-center text-borax-lilac-light shadow-md shadow-borax-purple/10">
          <UploadCloud size={28} strokeWidth={2} />
        </div>
        <div>
          <p className="text-base font-semibold text-borax-gray-light tracking-borax">{title}</p>
          <p className="text-xs text-borax-gray-muted mt-1 tracking-borax">{subtitle}</p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-borax-surface text-[11px] text-borax-gray-muted font-mono border border-borax-border">
          <File size={12} strokeWidth={2} />
          <span>Suporta: {acceptText}</span>
        </div>
      </div>
    </div>
  );
};
