import whisper
import os
from typing import List, Dict

class TranscriptionService:
    def __init__(self, model_name: str = "tiny"):  # Changed from "base" to "tiny" for lower memory usage
        self.model = whisper.load_model(model_name)

    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict[str, any]]:
        """
        Transcribes audio and returns segments with timestamps.
        Format: [{"start": 0.0, "end": 2.0, "text": "Hello world"}]
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        result = self.model.transcribe(audio_path)
        segments = []
        for segment in result['segments']:
            segments.append({
                "start": segment['start'],
                "end": segment['end'],
                "text": segment['text']
            })
        return segments

    def format_segments_to_string(self, segments: List[Dict[str, any]]) -> str:
        """
        Formats segments into the requested string format:
        [0.00 - 2.00] text
        """
        lines = []
        for s in segments:
            lines.append(f"[{s['start']:.2f} - {s['end']:.2f}] {s['text']}")
        return "\n".join(lines)

# Singleton instance
transcription_service = None

def get_transcription_service():
    global transcription_service
    if transcription_service is None:
        transcription_service = TranscriptionService()
    return transcription_service
