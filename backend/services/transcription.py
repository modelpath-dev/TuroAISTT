import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict[str, any]]:
        """
        Transcribes audio using OpenAI Whisper API and returns segments (simulated timestamps if not provided by verbose_json).
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="verbose_json"
            )
        
        # Extract segments from verbose_json response
        segments = []
        if hasattr(transcript, 'segments'):
            for segment in transcript.segments:
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
        else:
            # Fallback if no segments returned (shouldn't happen with verbose_json)
            segments.append({
                "start": 0.0,
                "end": 0.0,
                "text": transcript.text
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
