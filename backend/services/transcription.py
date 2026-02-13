import os
import json
from typing import List, Dict
from openai import OpenAI
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    def __init__(self):
        # Initialize OpenAI client (Keep for Chat/Report Gen)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Deepgram client (For Transcription)
        # User defined key as TURO_AI in .env
        deepgram_key = os.getenv("TURO_AI")
        if not deepgram_key:
            print("Warning: TURO_AI (Deepgram Key) not found in environment variables.")
        self.deepgram = DeepgramClient(deepgram_key)

    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict[str, any]]:
        """
        Transcribes audio using Deepgram Nova-2 API and returns segments.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        try:
            with open(audio_path, "rb") as audio_file:
                buffer_data = audio_file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            # Configure Deepgram options
            options = PrerecordedOptions(
                model="nova-2-medical",  # Use specialized medical model if enabled, else fallback to nova-2
                smart_format=True,
                utterances=True,
                punctuate=True,
            )

            # Call Deepgram API
            response = self.deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
            
            # Extract content
            segments = []
            
            # Check if utterances are available (preferred for timestamps)
            if response.results and response.results.utterances:
                for utterance in response.results.utterances:
                    segments.append({
                        "start": utterance.start,
                        "end": utterance.end,
                        "text": utterance.transcript
                    })
            # Fallback to general transcript if no utterances
            elif response.results and response.results.channels:
                channel = response.results.channels[0]
                if channel.alternatives:
                    alt = channel.alternatives[0]
                    segments.append({
                        "start": 0.0,
                        "end": 0.0, # Approximate
                        "text": alt.transcript
                    })
            
            return segments

        except Exception as e:
            print(f"Deepgram Transcription Error: {e}")
            # Fallback to basic error segment
            return [{"start": 0.0, "end": 0.0, "text": f"Error: {str(e)}"}]

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
