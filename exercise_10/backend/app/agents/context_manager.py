from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime

@dataclass
class TranscriptSegment:
    speaker: str  # "customer" or "agent"
    text: str
    timestamp: datetime

@dataclass
class ConversationState:
    call_id: str
    customer_id: Optional[int] = None
    customer_info: Optional[dict] = None
    transcript: List[TranscriptSegment] = field(default_factory=list)
    topics: Set[str] = field(default_factory=set)
    entities: Dict[str, any] = field(default_factory=dict)
    sentiment: str = "neutral"
    
    def add_transcript(self, speaker: str, text: str):
        """Add new transcript segment"""
        self.transcript.append(TranscriptSegment(
            speaker=speaker,
            text=text,
            timestamp=datetime.now()
        ))
    
    def get_context_for_ai(self) -> str:
        """Build prompt context"""
        parts = []
        
        if self.customer_info:
            parts.append(f"**Customer:** {self.customer_info['name']}")
            parts.append(f"**Tier:** {self.customer_info['tier']}")
            parts.append(f"**Account:** {self.customer_info['account_number']}")
            parts.append("")
        
        parts.append("**Recent Conversation:**")
        for seg in self.transcript[-10:]:
            parts.append(f"{seg.speaker.title()}: {seg.text}")
        
        return "\n".join(parts)

# Global state manager
conversation_states: Dict[str, ConversationState] = {}

def get_state(call_id: str) -> ConversationState:
    if call_id not in conversation_states:
        conversation_states[call_id] = ConversationState(call_id=call_id)
    return conversation_states[call_id]