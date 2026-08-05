import os
import re
import tempfile
from typing import Dict, Any, Optional, List
import yt_dlp
from faster_whisper import WhisperModel
from rag_engine import RAGEngine, DEFAULT_TABLE

class MediaProcessor:
    def __init__(self, model_size: str = "base", device: str = "cpu", rag_engine: Optional[RAGEngine] = None):
        self.model_size = model_size
        self.device = device
        self._rag_engine = rag_engine
        self._model = None

    @property
    def model(self):
        """Lazy loading of Whisper model to conserve RAM until transcription is called."""
        if self._model is None:
            self._model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
        return self._model

    @property
    def rag_engine(self):
        """Lazy loading of RAG engine."""
        if self._rag_engine is None:
            self._rag_engine = RAGEngine()
        return self._rag_engine

    def is_youtube_url(self, url_or_path: str) -> bool:
        """Check if string is a YouTube URL."""
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        return bool(re.match(youtube_regex, url_or_path.strip()))

    def download_youtube_audio(self, url: str) -> str:
        """Extract audio track from YouTube video using yt-dlp."""
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base_filename = os.path.splitext(filename)[0]
            audio_filename = f"{base_filename}.mp3"
            if os.path.exists(audio_filename):
                return audio_filename
            elif os.path.exists(filename):
                return filename
            else:
                files = os.listdir(temp_dir)
                if files:
                    return os.path.join(temp_dir, files[0])
                raise FileNotFoundError("Não foi possível extrair o áudio do vídeo do YouTube.")

    def transcribe_media(
        self,
        source_path_or_url: str,
        table_name: str = DEFAULT_TABLE,
        auto_ingest_rag: bool = True
    ) -> Dict[str, Any]:
        """Transcribe audio/video file or YouTube video and optionally ingest into LanceDB RAG."""
        is_yt = self.is_youtube_url(source_path_or_url)
        audio_file = None
        cleanup_file = False

        if is_yt:
            audio_file = self.download_youtube_audio(source_path_or_url)
            cleanup_file = True
            display_name = f"YouTube_{os.path.basename(audio_file)}"
        else:
            if not os.path.exists(source_path_or_url):
                raise FileNotFoundError(f"Arquivo de mídia não encontrado: {source_path_or_url}")
            audio_file = source_path_or_url
            display_name = os.path.basename(source_path_or_url)

        try:
            segments_generator, info = self.model.transcribe(audio_file, beam_size=5)

            segments = []
            full_text_parts = []

            for seg in segments_generator:
                segments.append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip()
                })
                full_text_parts.append(seg.text.strip())

            full_transcript = " ".join(full_text_parts)

            rag_result = None
            if auto_ingest_rag and full_transcript:
                temp_txt = os.path.join(tempfile.gettempdir(), f"transcript_{display_name}.txt")
                with open(temp_txt, "w", encoding="utf-8") as f:
                    f.write(f"--- TRANSCRIÇÃO DE MÍDIA: {display_name} ---\n\n{full_transcript}")
                
                try:
                    rag_result = self.rag_engine.process_file(temp_txt, table_name=table_name)
                finally:
                    if os.path.exists(temp_txt):
                        os.remove(temp_txt)

            return {
                "status": "success",
                "source": source_path_or_url,
                "is_youtube": is_yt,
                "language": info.language,
                "language_probability": round(info.language_probability, 2),
                "duration": round(info.duration, 2),
                "full_transcript": full_transcript,
                "segments_count": len(segments),
                "segments": segments,
                "rag_ingested": bool(rag_result and rag_result.get("status") == "success"),
                "table_name": table_name
            }
        finally:
            if cleanup_file and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    os.rmdir(os.path.dirname(audio_file))
                except Exception:
                    pass
