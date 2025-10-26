from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()

# Store transcription streams
transcription_streams: dict = {}

@router.get("/api/stream/transcript/{call_id}")
async def stream_transcript(call_id: str):
    async def generate():
        queue = asyncio.Queue()
        transcription_streams[call_id] = queue
        
        try:
            while True:
                # Wait for transcript
                transcript = await queue.get()
                
                # Send as SSE
                data = json.dumps(transcript)
                yield f"data: {data}\n\n"
        
        finally:
            del transcription_streams[call_id]
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )