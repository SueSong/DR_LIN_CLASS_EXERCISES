"""
Chatbot Agent with Security Monitoring
Handles document Q&A with prompt injection detection
"""
from typing import Dict, Any, List, Optional
import re
from datetime import datetime


class ChatbotAgent:
    """
    Secure chatbot for legal document Q&A with prompt injection detection
    """
    
    # Prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        # Direct instruction overrides
        r"ignore\s+(?:previous|all|above)\s+(?:instructions?|prompts?|commands?)",
        r"disregard\s+(?:previous|all|above)\s+(?:instructions?|rules?)",
        r"forget\s+(?:everything|all|previous|above)",
        
        # Role/system manipulation
        r"you\s+are\s+(?:now|actually)\s+(?:a|an)\s+\w+",
        r"act\s+(?:as|like)\s+(?:a|an)\s+\w+",
        r"pretend\s+(?:to\s+be|you\s+are)\s+(?:a|an)\s+\w+",
        r"your\s+new\s+(?:role|purpose|task)\s+is",
        
        # System prompt extraction
        r"show\s+(?:me\s+)?(?:your|the)\s+(?:system\s+)?(?:prompt|instructions)",
        r"what\s+(?:are|is)\s+your\s+(?:system\s+)?(?:prompt|instructions)",
        r"repeat\s+(?:your|the)\s+(?:instructions|prompt|rules)",
        r"print\s+(?:your|the)\s+(?:system\s+)?(?:prompt|instructions)",
        
        # Data extraction attempts
        r"show\s+(?:me\s+)?all\s+(?:documents?|data|information|files)",
        r"list\s+all\s+(?:documents?|users?|files|data)",
        r"dump\s+(?:all|the)\s+(?:data|database|documents?)",
        r"export\s+(?:all|the)\s+(?:data|documents?|information)",
        
        # PII extraction
        r"(?:show|give|provide|list)\s+(?:me\s+)?(?:all\s+)?(?:ssn|social\s+security|credit\s+card|password)s?",
        r"what\s+(?:is|are)\s+(?:the|their)\s+(?:ssn|password|credit\s+card)",
        
        # Delimiter/encoding attacks
        r"[<>]{3,}",  # HTML/XML injection attempts
        r"```[\s\S]*?```",  # Code block injection
        r"\{%.*?%\}",  # Template injection
        r"\{\{.*?\}\}",  # Template injection
        
        # Special tokens
        r"<\|.*?\|>",  # Special tokens
        r"\[INST\]|\[/INST\]",  # Instruction markers
        r"<system>|</system>",  # System tags
    ]
    
    # Jailbreak phrases
    JAILBREAK_PATTERNS = [
        r"DAN\s+mode",  # Do Anything Now
        r"developer\s+mode",
        r"God\s+mode",
        r"unrestricted\s+mode",
        r"freedom\s+mode",
        r"bypass\s+(?:all|your)\s+(?:restrictions?|rules?|limitations?)",
    ]
    
    # Forbidden operations
    FORBIDDEN_OPERATIONS = [
        r"execute\s+(?:code|command|script)",
        r"run\s+(?:code|command|script)",
        r"eval\s*\(",
        r"exec\s*\(",
        r"subprocess\.",
        r"os\.",
        r"__import__",
    ]
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.security_alerts: List[Dict[str, Any]] = []
    
    def chat(
        self,
        message: str,
        document_context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process chat message with security checks
        """
        # Security scan
        security_scan = self._scan_for_threats(message)
        
        if security_scan["threats_detected"]:
            return {
                "response": "⚠️ Security Alert: Your message was flagged for potential security concerns. Please rephrase your question.",
                "blocked": True,
                "security_scan": security_scan,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Extract context from documents
        context = self._extract_context(message, document_context) if document_context else None
        
        # Generate response (simulated - in production would use LLM)
        response = self._generate_response(message, context, conversation_id)
        
        # Log interaction
        self.conversation_history.append({
            "message": message,
            "response": response,
            "security_scan": security_scan,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "response": response,
            "blocked": False,
            "security_scan": security_scan,
            "context_used": context is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _scan_for_threats(self, message: str) -> Dict[str, Any]:
        """
        Scan message for security threats
        """
        threats = []
        message_lower = message.lower()
        
        # Check for prompt injection
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                threats.append({
                    "type": "prompt_injection",
                    "pattern": pattern,
                    "severity": "high"
                })
        
        # Check for jailbreak attempts
        for pattern in self.JAILBREAK_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                threats.append({
                    "type": "jailbreak_attempt",
                    "pattern": pattern,
                    "severity": "critical"
                })
        
        # Check for forbidden operations
        for pattern in self.FORBIDDEN_OPERATIONS:
            if re.search(pattern, message, re.IGNORECASE):
                threats.append({
                    "type": "forbidden_operation",
                    "pattern": pattern,
                    "severity": "critical"
                })
        
        # Check message length (potential DoS)
        if len(message) > 10000:
            threats.append({
                "type": "excessive_length",
                "severity": "medium",
                "length": len(message)
            })
        
        # Check for excessive special characters
        special_char_ratio = len([c for c in message if not c.isalnum() and not c.isspace()]) / max(len(message), 1)
        if special_char_ratio > 0.5:
            threats.append({
                "type": "suspicious_characters",
                "severity": "medium",
                "ratio": special_char_ratio
            })
        
        return {
            "threats_detected": len(threats) > 0,
            "threat_count": len(threats),
            "threats": threats,
            "risk_score": self._calculate_risk_score(threats)
        }
    
    def _calculate_risk_score(self, threats: List[Dict[str, Any]]) -> float:
        """
        Calculate overall risk score (0-1)
        """
        if not threats:
            return 0.0
        
        severity_weights = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        }
        
        total_score = sum(severity_weights.get(t.get("severity", "low"), 0.2) for t in threats)
        return min(total_score / len(threats), 1.0)
    
    def _extract_context(self, message: str, document_context: Dict[str, Any]) -> Optional[str]:
        """
        Extract relevant context from documents (simplified RAG)
        """
        if not document_context:
            return None
        
        content = document_context.get("content", "")
        
        # Simple keyword matching (in production would use embeddings)
        keywords = self._extract_keywords(message)
        
        # Find relevant paragraphs
        paragraphs = content.split('\n\n')
        relevant_paragraphs = []
        
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword.lower() in para_lower for keyword in keywords):
                relevant_paragraphs.append(para)
        
        if relevant_paragraphs:
            return '\n\n'.join(relevant_paragraphs[:3])  # Top 3 relevant paragraphs
        
        return None
    
    def _extract_keywords(self, message: str) -> List[str]:
        """
        Extract keywords from message
        """
        # Remove common stop words
        stop_words = {'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for'}
        words = re.findall(r'\b\w+\b', message.lower())
        return [w for w in words if w not in stop_words and len(w) > 3]
    
    def _generate_response(
        self,
        message: str,
        context: Optional[str],
        conversation_id: Optional[str]
    ) -> str:
        """
        Generate response (simulated - in production would use LLM)
        """
        # This is a simple simulated response
        # In production, this would call GPT-4, Claude, or another LLM
        
        message_lower = message.lower()
        
        # Handle common queries
        if any(word in message_lower for word in ['liability', 'cap', 'limit']):
            if context:
                return f"Based on the document, here's what I found about liability:\n\n{context[:500]}...\n\nNote: This is for informational purposes only and does not constitute legal advice."
            return "I found mentions of liability terms in the document. Please upload a document for specific details."
        
        if any(word in message_lower for word in ['term', 'duration', 'period']):
            if context:
                return f"Regarding the term or duration:\n\n{context[:500]}...\n\nDisclaimer: Consult with a qualified attorney for legal interpretation."
            return "The document mentions terms and durations. Please upload a document to see specific details."
        
        if any(word in message_lower for word in ['confidential', 'secret', 'private']):
            if context:
                return f"Regarding confidentiality:\n\n{context[:500]}...\n\nImportant: This document contains confidential information."
            return "This appears to relate to confidentiality provisions. Upload a document to analyze specific clauses."
        
        if 'summary' in message_lower or 'summarize' in message_lower:
            return "I can help summarize legal documents. Please upload a document and I'll provide a summary of key terms, obligations, and risks."
        
        if 'risk' in message_lower:
            return "I can help identify potential risks in legal documents. Upload a document and I'll analyze clauses for risk factors, liability issues, and compliance concerns."
        
        # Default response
        if context:
            return f"Based on the document content:\n\n{context[:400]}...\n\nLegal Disclaimer: This information is provided for educational purposes only and does not constitute legal advice. Always consult with a qualified attorney for legal matters."
        
        return "I'm a legal document assistant. I can help you understand contracts, agreements, and other legal documents. Please upload a document and ask specific questions about:\n\n• Terms and conditions\n• Liability clauses\n• Confidentiality provisions\n• Contract duration\n• Risk factors\n\nWhat would you like to know?"


def detect_prompt_injection(message: str) -> Dict[str, Any]:
    """
    Standalone function to detect prompt injection
    """
    agent = ChatbotAgent()
    return agent._scan_for_threats(message)

