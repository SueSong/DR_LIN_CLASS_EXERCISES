"""
Reviewer Agent
Assesses risks and policy compliance
"""
from typing import Dict, Any, List
import re


class ReviewerAgent:
    """
    Reviews documents for risk and policy compliance
    """
    
    RISK_KEYWORDS = {
        "high": [
            "unlimited liability",
            "no liability cap",
            "perpetual",
            "irrevocable",
            "waiver of rights",
            "exclusive remedy",
        ],
        "medium": [
            "limited liability",
            "termination for convenience",
            "auto-renewal",
            "binding arbitration",
        ]
    }
    
    FORBIDDEN_ADVICE_PATTERNS = [
        r"\byou should\s+(?:file|claim|deduct)",  # Tax advice
        r"\bthis (?:will|would) (?:cure|treat|prevent)",  # Medical advice
        r"\bI (?:recommend|advise|suggest)\s+that\s+you\s+(?:sue|file)",  # Unauthorized legal advice
    ]
    
    def review(
        self,
        document: Dict[str, Any],
        classification: Dict[str, Any],
        extraction: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Review document for risks and policy compliance
        """
        content = document.get("content", "")
        clauses = extraction.get("clauses", [])
        pii_entities = extraction.get("pii_entities", [])
        
        # Assess each clause
        clause_assessments = self._assess_clauses(clauses, policies)
        
        # Check policy violations
        policy_violations = self._check_policy_violations(content, pii_entities, policies)
        
        # Assess overall risk
        overall_risk = self._assess_overall_risk(
            classification,
            clause_assessments,
            policy_violations,
            pii_entities
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            clause_assessments,
            policy_violations,
            overall_risk
        )
        
        # Identify high-risk items for HITL
        high_risk_items = self._identify_high_risk_items(
            clause_assessments,
            policy_violations
        )
        
        # Check if HITL is required
        requires_hitl = self._check_hitl_requirement(
            overall_risk,
            high_risk_items,
            policies
        )
        
        return {
            "overall_risk": overall_risk,
            "clause_assessments": clause_assessments,
            "policy_violations": policy_violations,
            "recommendations": recommendations,
            "high_risk_items": high_risk_items,
            "requires_hitl": requires_hitl,
            "review_summary": {
                "total_clauses": len(clauses),
                "high_risk_clauses": sum(1 for c in clause_assessments if c["risk_level"] == "high"),
                "policy_violations_count": len(policy_violations),
                "pii_detected": len(pii_entities)
            }
        }
    
    def _assess_clauses(self, clauses: List[Dict[str, Any]], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assess each clause for risk
        """
        assessments = []
        
        for clause in clauses:
            text = clause.get("text", "").lower()
            
            # Determine risk level
            risk_level = "low"
            risk_factors = []
            
            # Check for high-risk keywords
            for keyword in self.RISK_KEYWORDS["high"]:
                if keyword in text:
                    risk_level = "high"
                    risk_factors.append(f"contains: {keyword}")
            
            # Check for medium-risk keywords if not already high
            if risk_level == "low":
                for keyword in self.RISK_KEYWORDS["medium"]:
                    if keyword in text:
                        risk_level = "medium"
                        risk_factors.append(f"contains: {keyword}")
            
            # Check for financial amounts
            financial_match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
            if financial_match:
                amount_str = financial_match.group().replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    # Check threshold from policies
                    threshold = 100000
                    for policy in policies:
                        if policy.get("name") == "Risk Management Thresholds":
                            threshold = policy.get("rules", {}).get("financial_terms_threshold", 100000)
                    
                    if amount > threshold:
                        risk_level = "high"
                        risk_factors.append(f"financial amount exceeds threshold: ${amount:,.2f}")
                except:
                    pass
            
            # Generate rationale
            if not risk_factors:
                rationale = "Standard clause with no identified risk factors"
            else:
                rationale = "; ".join(risk_factors)
            
            # Find relevant policy references
            policy_refs = self._find_policy_references(text, policies)
            
            assessments.append({
                "clause_id": clause["id"],
                "heading": clause["heading"],
                "risk_level": risk_level,
                "rationale": rationale,
                "policy_refs": policy_refs,
                "risk_factors": risk_factors
            })
        
        return assessments
    
    def _check_policy_violations(
        self,
        content: str,
        pii_entities: List[Dict[str, Any]],
        policies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check for policy violations
        """
        violations = []
        
        # Check for forbidden advice patterns
        for pattern in self.FORBIDDEN_ADVICE_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": "forbidden_advice",
                    "severity": "high",
                    "description": "Document contains potentially unauthorized legal/tax/medical advice",
                    "text": match.group(),
                    "position": match.start(),
                    "policy": "Legal Compliance Policy"
                })
        
        # Check for missing required disclaimers
        compliance_policy = next(
            (p for p in policies if p.get("name") == "Legal Compliance Policy"),
            None
        )
        
        if compliance_policy:
            required_disclaimers = compliance_policy.get("rules", {}).get("required_disclaimers", [])
            for disclaimer_type in required_disclaimers:
                if not self._has_disclaimer(content, disclaimer_type):
                    violations.append({
                        "type": "missing_disclaimer",
                        "severity": "medium",
                        "description": f"Missing required {disclaimer_type.replace('_', ' ')}",
                        "policy": "Legal Compliance Policy",
                        "disclaimer_type": disclaimer_type
                    })
        
        # Check for third-party sharing without protection
        if re.search(r"third[- ]party|share.*(?:with|to).*(?:partner|vendor|contractor)", content, re.IGNORECASE):
            if any(pii["risk_level"] == "high" for pii in pii_entities):
                violations.append({
                    "type": "third_party_pii_sharing",
                    "severity": "high",
                    "description": "Document mentions third-party sharing with high-risk PII present",
                    "policy": "PII Protection Policy"
                })
        
        return violations
    
    def _assess_overall_risk(
        self,
        classification: Dict[str, Any],
        clause_assessments: List[Dict[str, Any]],
        policy_violations: List[Dict[str, Any]],
        pii_entities: List[Dict[str, Any]]
    ) -> str:
        """
        Assess overall document risk level
        """
        # Count risk factors
        high_risk_clauses = sum(1 for c in clause_assessments if c["risk_level"] == "high")
        high_severity_violations = sum(1 for v in policy_violations if v["severity"] == "high")
        high_risk_pii = sum(1 for p in pii_entities if p["risk_level"] == "high")
        
        # Classification risk factors
        classification_risk_factors = len(classification.get("risk_factors", []))
        
        # Determine overall risk
        if high_severity_violations > 0 or high_risk_clauses > 2 or high_risk_pii > 2:
            return "high"
        elif high_risk_clauses > 0 or high_risk_pii > 0 or classification_risk_factors > 2:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(
        self,
        clause_assessments: List[Dict[str, Any]],
        policy_violations: List[Dict[str, Any]],
        overall_risk: str
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations
        """
        recommendations = []
        
        # Recommendations for high-risk clauses
        high_risk_clauses = [c for c in clause_assessments if c["risk_level"] == "high"]
        for clause in high_risk_clauses:
            recommendations.append({
                "type": "clause_revision",
                "priority": "high",
                "target": clause["clause_id"],
                "description": f"Review and revise clause: {clause['heading']}",
                "rationale": clause["rationale"]
            })
        
        # Recommendations for policy violations
        for violation in policy_violations:
            if violation["type"] == "missing_disclaimer":
                recommendations.append({
                    "type": "add_disclaimer",
                    "priority": "medium",
                    "description": f"Add required {violation['disclaimer_type'].replace('_', ' ')}",
                    "disclaimer_type": violation["disclaimer_type"]
                })
            elif violation["type"] == "forbidden_advice":
                recommendations.append({
                    "type": "remove_content",
                    "priority": "high",
                    "description": "Remove unauthorized advice language",
                    "text": violation["text"]
                })
        
        # Overall recommendations based on risk
        if overall_risk == "high":
            recommendations.append({
                "type": "general",
                "priority": "high",
                "description": "Document requires legal counsel review before use",
            })
        
        return recommendations
    
    def _identify_high_risk_items(
        self,
        clause_assessments: List[Dict[str, Any]],
        policy_violations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify items that need HITL review
        """
        high_risk_items = []
        
        # High-risk clauses
        for clause in clause_assessments:
            if clause["risk_level"] == "high":
                high_risk_items.append({
                    "id": f"hitl_{clause['clause_id']}",
                    "type": "clause",
                    "clause_id": clause["clause_id"],
                    "heading": clause["heading"],
                    "risk_level": "high",
                    "rationale": clause["rationale"]
                })
        
        # High severity violations
        for idx, violation in enumerate(policy_violations):
            if violation["severity"] == "high":
                high_risk_items.append({
                    "id": f"hitl_violation_{idx}",
                    "type": "violation",
                    "violation_type": violation["type"],
                    "description": violation["description"],
                    "severity": "high"
                })
        
        return high_risk_items
    
    def _check_hitl_requirement(
        self,
        overall_risk: str,
        high_risk_items: List[Dict[str, Any]],
        policies: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if HITL is required
        """
        # Check policy requirements
        for policy in policies:
            if policy.get("name") == "Risk Management Thresholds":
                if policy.get("rules", {}).get("high_risk_requires_hitl", False):
                    if overall_risk == "high":
                        return True
        
        # Require HITL if there are high-risk items
        if len(high_risk_items) > 0:
            return True
        
        return False
    
    def _find_policy_references(self, text: str, policies: List[Dict[str, Any]]) -> List[str]:
        """
        Find applicable policy references
        """
        refs = []
        
        if "liability" in text and "cap" in text:
            refs.append("liability_cap_policy")
        if "confidential" in text or "secret" in text:
            refs.append("confidentiality_policy")
        if "termination" in text:
            refs.append("termination_policy")
        
        return refs
    
    def _has_disclaimer(self, content: str, disclaimer_type: str) -> bool:
        """
        Check if document has required disclaimer
        """
        disclaimer_patterns = {
            "legal_disclaimer": r"(?:legal disclaimer|not legal advice|for informational purposes)",
            "confidentiality_notice": r"(?:confidential|proprietary|not for distribution)"
        }
        
        pattern = disclaimer_patterns.get(disclaimer_type)
        if pattern:
            return bool(re.search(pattern, content, re.IGNORECASE))
        
        return False

