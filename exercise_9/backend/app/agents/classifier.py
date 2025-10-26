"""
Classifier Agent
Determines document type and sensitivity level
"""
from typing import Dict, Any, List
import re


class ClassifierAgent:
    """
    Classifies legal documents by type and sensitivity
    """
    
    DOC_TYPE_PATTERNS = {
        "nda": [r"\bnon-disclosure\b", r"\bconfidentiality agreement\b", r"\bsecrecy agreement\b"],
        "employment_contract": [r"\bemployment agreement\b", r"\bwork contract\b", r"\bemployee agreement\b"],
        "service_agreement": [r"\bservice agreement\b", r"\bmaster service agreement\b", r"\bmsa\b"],
        "purchase_order": [r"\bpurchase order\b", r"\bp\.?o\.?\b", r"\bpo#\b"],
        "lease": [r"\blease agreement\b", r"\brental agreement\b", r"\btenancy agreement\b"],
        "terms_of_service": [r"\bterms of service\b", r"\bterms and conditions\b", r"\buser agreement\b"],
        "privacy_policy": [r"\bprivacy policy\b", r"\bdata protection\b", r"\bprivacy notice\b"],
    }
    
    SENSITIVITY_INDICATORS = {
        "high": [
            r"\bconfidential\b",
            r"\btrade secret\b",
            r"\bproprietary\b",
            r"\bfinancial data\b",
            r"\bhealth information\b",
            r"\bhipaa\b",
            r"\bpii\b",
            r"\bssn\b",
            r"\bbank account\b",
        ],
        "medium": [
            r"\binternal use only\b",
            r"\brestricted\b",
            r"\bbusiness sensitive\b",
        ],
    }
    
    def classify(self, document: Dict[str, Any], policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify document type and sensitivity
        """
        content = document.get("content", "").lower()
        
        # Detect document type
        doc_type = self._detect_document_type(content)
        
        # Detect sensitivity level
        sensitivity_level = self._detect_sensitivity(content)
        
        # Check for financial terms
        has_financial_terms = self._detect_financial_terms(content)
        
        # Check for health data
        has_health_data = self._detect_health_data(content)
        
        # Determine risk factors
        risk_factors = []
        if sensitivity_level == "high":
            risk_factors.append("high_sensitivity")
        if has_financial_terms:
            risk_factors.append("financial_terms")
        if has_health_data:
            risk_factors.append("health_data")
        if doc_type == "nda":
            risk_factors.append("nda_document")
        
        return {
            "doc_type": doc_type,
            "sensitivity_level": sensitivity_level,
            "has_financial_terms": has_financial_terms,
            "has_health_data": has_health_data,
            "risk_factors": risk_factors,
            "confidence": 0.85,  # Simulated confidence score
            "metadata": {
                "document_length": len(content),
                "estimated_clauses": content.count('\n\n') + 1
            }
        }
    
    def _detect_document_type(self, content: str) -> str:
        """
        Detect document type based on content patterns
        """
        for doc_type, patterns in self.DOC_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return doc_type
        return "general_legal"
    
    def _detect_sensitivity(self, content: str) -> str:
        """
        Detect sensitivity level
        """
        high_count = sum(
            1 for pattern in self.SENSITIVITY_INDICATORS["high"]
            if re.search(pattern, content, re.IGNORECASE)
        )
        
        medium_count = sum(
            1 for pattern in self.SENSITIVITY_INDICATORS["medium"]
            if re.search(pattern, content, re.IGNORECASE)
        )
        
        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _detect_financial_terms(self, content: str) -> bool:
        """
        Detect financial terms and amounts
        """
        financial_patterns = [
            r"\$[\d,]+(?:\.\d{2})?",
            r"\d+\s*(?:dollars|usd|eur|gbp)",
            r"\b(?:payment|fee|cost|price|salary|compensation)\b",
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _detect_health_data(self, content: str) -> bool:
        """
        Detect health-related information
        """
        health_patterns = [
            r"\bhipaa\b",
            r"\bhealth information\b",
            r"\bmedical record\b",
            r"\bpatient data\b",
            r"\bphi\b",
        ]
        
        for pattern in health_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

