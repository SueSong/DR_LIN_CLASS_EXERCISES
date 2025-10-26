from openai import AsyncOpenAI
from typing import List, Dict
from datetime import datetime
import json
import sys
import os

# Import existing assistant and context manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ..agents.assistant import StreamingAssistant
    from ..agents.context_manager import get_state
except:
    StreamingAssistant = None
    get_state = None

class AIAssistantService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    async def generate_suggestion(
        self, 
        call_id: str, 
        customer_message: str,
        conversation_context: List[Dict] = None
    ) -> Dict:
        """
        Generate agent suggestion based on customer message using existing context manager
        """
        try:
            # Use existing context manager to get conversation state
            if get_state:
                state = get_state(call_id)
                state.add_transcript("customer", customer_message)
                context = state.get_context_for_ai()
            else:
                # Fallback to simple context
                context = f"Customer said: {customer_message}"
            
            # Create a focused prompt for suggestions
            system_prompt = """You are an AI assistant helping call center agents respond to customers effectively.

Analyze the conversation and provide a helpful suggestion for the agent.

Respond with a JSON object containing:
- "suggestion": A specific, actionable suggestion for what the agent should say or do
- "reasoning": Brief explanation of why this is a good approach  
- "action": The type of action (ask_question, offer_solution, escalate, offer_refund, provide_information, empathize)
- "confidence": A score from 0.0 to 1.0 indicating how confident you are in this suggestion

Example:
{
    "suggestion": "Acknowledge the customer's frustration and offer to look into their order status immediately",
    "reasoning": "Customer seems concerned about delivery delay",
    "action": "empathize", 
    "confidence": 0.9
}

Keep suggestions concise and actionable. Always respond with valid JSON."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=250
            )
            
            suggestion_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                suggestion_data = json.loads(suggestion_text)
                return {
                    "suggestion": suggestion_data.get("suggestion", suggestion_text),
                    "reasoning": suggestion_data.get("reasoning", ""),
                    "action": suggestion_data.get("action", "provide_information"),
                    "confidence": suggestion_data.get("confidence", 0.8),
                    "timestamp": datetime.utcnow().isoformat()
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "suggestion": suggestion_text,
                    "reasoning": "",
                    "action": "provide_information",
                    "confidence": 0.7,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return {
                "suggestion": "Listen carefully and ask clarifying questions to understand the customer's needs",
                "reasoning": "General best practice for customer service",
                "action": "ask_question",
                "confidence": 0.5,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def clear_history(self, call_id: str):
        """Clear conversation history for a call"""
        if call_id in self.conversation_history:
            del self.conversation_history[call_id]