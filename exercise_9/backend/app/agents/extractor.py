"""
Extractor Agent
Extracts clauses, PII, and entities from documents
"""
from typing import Dict, Any, List
import re
import hashlib


class ExtractorAgent:
    """
    Extracts structured information including PII from documents
    """
    
    PII_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "tax_id": r"\b\d{2}-\d{7}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "bank_account": r"\b\d{8,17}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "address": r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b",
        "name": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Simple name pattern
    }
    
    def extract(
        self,
        document: Dict[str, Any],
        classification: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract clauses and PII from document
        """
        content = document.get("content", "")
        
        # Extract clauses
        clauses = self._extract_clauses(content)
        
        # Extract PII entities
        pii_entities = self._extract_pii(content, policies)
        
        # Extract key terms and entities
        key_terms = self._extract_key_terms(content)
        
        # Determine if HITL is required
        requires_hitl = self._check_hitl_requirement(pii_entities, classification, policies)
        
        return {
            "clauses": clauses,
            "pii_entities": pii_entities,
            "key_terms": key_terms,
            "requires_hitl": requires_hitl,
            "extraction_stats": {
                "total_clauses": len(clauses),
                "pii_count": len(pii_entities),
                "high_risk_pii": sum(1 for p in pii_entities if p["risk_level"] == "high")
            }
        }
    
    def _extract_clauses(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract document clauses
        """
        clauses = []
        
        # Split by double newlines or numbered sections
        sections = re.split(r'\n\n+|\n\d+\.', content)
        
        for idx, section in enumerate(sections):
            section = section.strip()
            if len(section) < 20:  # Skip very short sections
                continue
            
            # Try to extract heading
            lines = section.split('\n')
            heading = lines[0] if lines else f"Section {idx + 1}"
            text = '\n'.join(lines[1:]) if len(lines) > 1 else section
            
            clause_id = f"clause_{idx + 1}"
            clauses.append({
                "id": clause_id,
                "heading": heading[:100],  # Limit heading length
                "text": text,
                "position": idx,
                "length": len(text)
            })
        
        return clauses
    
    def _extract_pii(self, content: str, policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract PII entities with context
        """
        pii_entities = []
        
        # Get redaction mode from policies
        redaction_mode = "mask"
        for policy in policies:
            if policy.get("name") == "PII Protection Policy":
                redaction_mode = policy.get("rules", {}).get("redaction_mode", "mask")
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.finditer(pattern, content)
            
            for match in matches:
                entity_text = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # Get context (50 chars before and after)
                context_start = max(0, start_pos - 50)
                context_end = min(len(content), end_pos + 50)
                context = content[context_start:context_end]
                
                # Determine risk level
                risk_level = self._assess_pii_risk(pii_type)
                
                # Create entity ID
                entity_id = hashlib.md5(f"{pii_type}_{start_pos}_{entity_text}".encode()).hexdigest()[:16]
                
                pii_entities.append({
                    "id": entity_id,
                    "type": pii_type,
                    "text": entity_text,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "context": context,
                    "risk_level": risk_level,
                    "redaction_mode": redaction_mode,
                    "redacted_value": self._redact_value(entity_text, pii_type, redaction_mode)
                })
        
        return pii_entities
    
    def _extract_key_terms(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract key legal terms
        """
        key_term_patterns = {
            "liability_cap": r"liability\s+(?:is\s+)?cap(?:ped)?(?:\s+at)?\s+[\$\d,]+",
            "term_duration": r"term\s+of\s+\d+\s+(?:years?|months?|days?)",
            "termination": r"terminat(?:ion|e)\s+(?:clause|provision|notice)",
            "indemnification": r"indemnif(?:ication|y)",
            "governing_law": r"governing\s+law",
            "dispute_resolution": r"(?:dispute\s+resolution|arbitration|mediation)",
        }
        
        key_terms = []
        for term_type, pattern in key_term_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                key_terms.append({
                    "type": term_type,
                    "text": match.group(),
                    "position": match.start()
                })
        
        return key_terms
    
    def _assess_pii_risk(self, pii_type: str) -> str:
        """
        Assess risk level of PII type
        """
        high_risk = ["ssn", "tax_id", "credit_card", "bank_account"]
        medium_risk = ["email", "phone", "address"]
        
        if pii_type in high_risk:
            return "high"
        elif pii_type in medium_risk:
            return "medium"
        else:
            return "low"
    
    def _redact_value(self, value: str, pii_type: str, mode: str) -> str:
        """
        Redact PII value based on mode
        """
        if mode == "refuse":
            return "[REDACTED]"
        elif mode == "generalize":
            if pii_type == "email":
                return "[EMAIL]"
            elif pii_type == "phone":
                return "[PHONE]"
            elif pii_type == "ssn":
                return "[SSN]"
            elif pii_type == "credit_card":
                return "[CREDIT_CARD]"
            elif pii_type == "bank_account":
                return "[BANK_ACCOUNT]"
            else:
                return f"[{pii_type.upper()}]"
        else:  # mask
            if pii_type in ["ssn", "tax_id"]:
                # Keep last 4 digits
                if len(value) >= 4:
                    return "***-**-" + value[-4:]
                return "***"
            elif pii_type == "credit_card":
                # Keep last 4 digits
                if len(value) >= 4:
                    return "**** **** **** " + value[-4:]
                return "****"
            elif pii_type == "email":
                # Mask username, keep domain
                if '@' in value:
                    parts = value.split('@')
                    return "***@" + parts[1]
                return "***"
            elif pii_type == "phone":
                # Keep last 4 digits
                digits = ''.join(c for c in value if c.isdigit())
                if len(digits) >= 4:
                    return "***-***-" + digits[-4:]
                return "***"
            else:
                return "***"
    
    def _check_hitl_requirement(
        self,
        pii_entities: List[Dict[str, Any]],
        classification: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if HITL is required based on PII and classification
        """
        # Check for high-risk PII
        high_risk_pii = [p for p in pii_entities if p["risk_level"] == "high"]
        if len(high_risk_pii) > 0:
            return True
        
        # Check if document has financial or health data with PII
        if classification.get("has_financial_terms") or classification.get("has_health_data"):
            if len(pii_entities) > 0:
                return True
        
        # Check policy requirements
        for policy in policies:
            if policy.get("name") == "PII Protection Policy":
                if policy.get("rules", {}).get("require_hitl", False) and len(pii_entities) > 0:
                    return True
        
        return False

