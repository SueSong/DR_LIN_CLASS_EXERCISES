import openai
from fastapi import HTTPException
import io

class WhisperService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio using OpenAI Whisper API
        
        Args:
            audio_bytes: Audio data in WebM format
            
        Returns:
            Transcribed text
        """
        try:
            # Convert audio bytes to file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"
            
            # Call Whisper API
            response = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
            
            return response.get("text", "")
            
        except Exception as e:
            print(f"Whisper error: {e}")
            raise HTTPException(status_code=500, detail=str(e))