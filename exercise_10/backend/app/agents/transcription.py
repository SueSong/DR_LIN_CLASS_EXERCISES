import openai
import asyncio
from typing import AsyncGenerator
import io
import wave

class TranscriptionEngine:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.buffer_size = 16000 * 5  # 5 seconds at 16kHz
    
    async def transcribe_stream(
        self, 
        call_id: str, 
        audio_queue: asyncio.Queue
    ) -> AsyncGenerator[dict, None]:
        """Transcribe audio chunks as they arrive"""
        
        buffer = bytearray()
        
        while True:
            try:
                # Get audio chunk
                chunk = await asyncio.wait_for(audio_queue.get(), timeout=30)
                buffer.extend(chunk)
                
                # Process when buffer is full
                if len(buffer) >= self.buffer_size:
                    audio_data = bytes(buffer)
                    buffer.clear()
                    
                    # Convert to WAV format
                    wav_buffer = self._to_wav(audio_data)
                    
                    # Transcribe
                    result = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=("audio.wav", wav_buffer, "audio/wav"),
                        language="en"
                    )
                    
                    yield {
                        "call_id": call_id,
                        "text": result.text,
                        "timestamp": asyncio.get_event_loop().time()
                    }
            
            except asyncio.TimeoutError:
                # No audio received, end stream
                break
            except Exception as e:
                print(f"Transcription error: {e}")
                continue
    
    def _to_wav(self, audio_data: bytes) -> io.BytesIO:
        """Convert raw PCM to WAV format"""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data)
        wav_buffer.seek(0)
        return wav_buffer