"""
Safety Guard Module
Implements content safety checks and refusal handling for the Child Growth Assistant.
"""

import json
import re
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from .observability import get_tracer


class SafetyClassification(Enum):
    """Safety classification categories"""
    SAFE = "safe"
    BLOCKED = "blocked"
    ESCALATE = "escalate"


class SafetyGuard:
    """Safety guard that checks user messages against safety policies"""
    
    def __init__(self, policy_path: Optional[str] = None):
        """
        Initialize the safety guard with policy configuration.
        
        Args:
            policy_path: Path to safety_policy.json. If None, uses default location.
        """
        if policy_path is None:
            # Default to config/safety_policy.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            policy_path = project_root / "config" / "safety_policy.json"
        
        self.policy_path = Path(policy_path)
        self.policy = self._load_policy()
        self.keyword_patterns = self.policy.get("keyword_patterns", {})
        self.refusal_templates = self.policy.get("refusal_templates", {})
        self.log_enabled = self.policy.get("settings", {}).get("enable_logging", True)
        
        # Pre-compile regex patterns for performance
        self._compiled_patterns = {}
        self._compile_patterns()
    
    def _load_policy(self) -> Dict:
        """Load safety policy from JSON file"""
        try:
            with open(self.policy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Safety policy file not found: {self.policy_path}. "
                "Please create config/safety_policy.json"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in safety policy: {e}")
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for all keyword categories"""
        for category, config in self.keyword_patterns.items():
            patterns = config.get("patterns", [])
            compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            self._compiled_patterns[category] = compiled
    
    def check_message(self, message: str, session_id: Optional[str] = None) -> Tuple[SafetyClassification, Optional[str], Dict]:
        """
        Check a user message against safety policies.
        
        Args:
            message: User message to check
            session_id: Optional session ID for logging
        
        Returns:
            Tuple of (classification, refusal_message, metadata)
            - classification: SAFE, BLOCKED, or ESCALATE
            - refusal_message: Template response if blocked/escalated, None if safe
            - metadata: Dict with matched keywords, category, etc.
        """
        tracer = get_tracer()
        start_time = time.time()
        
        with tracer.start_as_current_span("guard.check_message") as span:
            span.set_attribute("guard.message_length", len(message))
            span.set_attribute("guard.session_id", session_id or "unknown")
            
            message_lower = message.lower().strip()
            
            if not message_lower:
                span.set_attribute("guard.classification", "SAFE")
                span.set_attribute("guard.latency_ms", (time.time() - start_time) * 1000)
                return SafetyClassification.SAFE, None, {}
            
            # Check against all keyword categories
            matches = {}
            
            # Priority: Check crisis/escalate first, then blocked categories
            escalate_matches = []
            blocked_matches = []
            
            for category, config in self.keyword_patterns.items():
                category_type = config.get("category", "blocked")
                keywords = config.get("keywords", [])
                patterns = config.get("patterns", [])
                
                # Check keywords
                matched_keywords = [
                    kw for kw in keywords 
                    if kw.lower() in message_lower
                ]
                
                # Check patterns
                matched_patterns = []
                if category in self._compiled_patterns:
                    for pattern in self._compiled_patterns[category]:
                        if pattern.search(message_lower):
                            matched_patterns.append(pattern.pattern)
                
                if matched_keywords or matched_patterns:
                    matches[category] = {
                        "keywords": matched_keywords,
                        "patterns": matched_patterns
                    }
                    
                    if category_type == "escalate":
                        escalate_matches.append(category)
                    elif category_type == "blocked":
                        blocked_matches.append(category)
            
            # Determine classification based on matches
            if escalate_matches:
                # Crisis situation - highest priority
                classification = SafetyClassification.ESCALATE
                template_key = "crisis"
                primary_category = escalate_matches[0]
            elif blocked_matches:
                # Out of scope request
                classification = SafetyClassification.BLOCKED
                primary_category = blocked_matches[0]
                # Map category to template key
                if primary_category == "medical":
                    template_key = "medical"
                elif primary_category == "legal":
                    template_key = "legal"
                elif primary_category == "professional_services":
                    template_key = "professional_services"
                else:
                    template_key = "general_out_of_scope"
            else:
                # Safe to process
                classification = SafetyClassification.SAFE
                template_key = None
                primary_category = None
            
            # Generate refusal message if needed
            refusal_message = None
            if classification != SafetyClassification.SAFE:
                refusal_message = self._generate_refusal_message(
                    template_key, 
                    message, 
                    primary_category
                )
            
            # Build metadata
            latency_ms = (time.time() - start_time) * 1000
            metadata = {
                "matched_categories": list(matches.keys()),
                "primary_category": primary_category,
                "matches": matches,
                "template_used": template_key,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "latency_ms": latency_ms
            }
            
            # Set span attributes for observability
            span.set_attribute("guard.classification", classification.value)
            span.set_attribute("guard.latency_ms", latency_ms)
            span.set_attribute("guard.primary_category", primary_category or "none")
            span.set_attribute("guard.matched_categories_count", len(matches))
            if primary_category:
                span.set_attribute("guard.template_used", template_key or "none")
            
            # Log intervention
            if classification != SafetyClassification.SAFE and self.log_enabled:
                self._log_intervention(message, classification, metadata)
            
            return classification, refusal_message, metadata
    
    def _generate_refusal_message(
        self, 
        template_key: str, 
        original_message: str,
        category: Optional[str]
    ) -> str:
        """Generate refusal message from template"""
        template = self.refusal_templates.get(template_key)
        
        if not template:
            # Fallback template
            template = self.refusal_templates.get(
                "general_out_of_scope",
                "I'm sorry, but I can't help with that request. I specialize in general parenting strategies and child development guidance."
            )
        
        # Extract topic from original message (simple extraction)
        # Try to find a key phrase or use a generic topic
        topic = self._extract_topic(original_message, category)
        
        # Replace {topic} placeholder if present
        if "{topic}" in template:
            template = template.replace("{topic}", topic)
        
        return template
    
    def _extract_topic(self, message: str, category: Optional[str]) -> str:
        """Extract a topic description from the message"""
        # Simple topic extraction - take first 50 chars or key phrase
        if category == "medical":
            return "medical concerns"
        elif category == "legal":
            return "legal matters"
        elif category == "crisis":
            return "this situation"
        elif category == "professional_services":
            return "professional services"
        else:
            # Take a snippet of the message
            words = message.split()[:10]
            topic = " ".join(words)
            if len(topic) > 50:
                topic = topic[:47] + "..."
            return topic if topic else "that topic"
    
    def _log_intervention(self, message: str, classification: SafetyClassification, metadata: Dict):
        """Log safety intervention to file"""
        log_file = self.policy.get("settings", {}).get("log_file", "safety_interventions.log")
        log_path = Path(__file__).parent.parent.parent / log_file
        
        log_entry = {
            "timestamp": metadata["timestamp"],
            "classification": classification.value,
            "session_id": metadata.get("session_id"),
            "message": message,
            "metadata": metadata
        }
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            # Don't fail if logging fails
            print(f"Warning: Could not log safety intervention: {e}")


# Global guard instance (singleton pattern)
_guard_instance: Optional[SafetyGuard] = None


def get_safety_guard(policy_path: Optional[str] = None) -> SafetyGuard:
    """Get or create the global safety guard instance"""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = SafetyGuard(policy_path)
    return _guard_instance


def check_message_safety(message: str, session_id: Optional[str] = None) -> Tuple[SafetyClassification, Optional[str], Dict]:
    """
    Convenience function to check message safety.
    
    Args:
        message: User message to check
        session_id: Optional session ID
    
    Returns:
        Tuple of (classification, refusal_message, metadata)
    """
    guard = get_safety_guard()
    return guard.check_message(message, session_id)

