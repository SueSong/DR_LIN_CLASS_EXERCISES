import openai
import json
from typing import AsyncGenerator

class StreamingAssistant:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.system_prompt = """You are an AI assistant helping a call center agent in real-time.

Analyze the conversation and provide:
1. **Immediate suggestions** - What the agent should say next
2. **Customer insights** - Important facts about the customer
3. **Policy guidance** - Relevant company policies
4. **Risk alerts** - If customer is frustrated or at risk of churning

Respond in short, actionable bullet points. Be concise and helpful."""
    
    async def stream_suggestions(
        self,
        context: str
    ) -> AsyncGenerator[dict, None]:
        """Generate streaming suggestions"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]
        
        stream = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            
            if delta.content:
                yield {
                    "type": "text",
                    "content": delta.content
                }
            
            if chunk.choices[0].finish_reason:
                yield {"type": "complete"}