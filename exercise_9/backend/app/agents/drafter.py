"""
Drafter Agent
Creates redacted and edited versions of documents
"""
from typing import Dict, Any, List
import re


class DrafterAgent:
    """
    Drafts redacted and edited versions of documents
    """
    
    DISCLAIMER_TEMPLATES = {
        "legal_disclaimer": "\n\n---\n**LEGAL DISCLAIMER**: This document is for informational purposes only and does not constitute legal advice. Consult with a qualified attorney for legal guidance.\n",
        "confidentiality_notice": "\n\n---\n**CONFIDENTIAL**: This document contains confidential and proprietary information. Do not distribute without authorization.\n"
    }
    
    def draft(
        self,
        document: Dict[str, Any],
        classification: Dict[str, Any],
        extraction: Dict[str, Any],
        review: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Draft final version with redactions and edits
        """
        content = document.get("content", "")
        
        # Apply PII redactions
        redacted_content, redactions = self._apply_pii_redactions(
            content,
            extraction.get("pii_entities", [])
        )
        
        # Apply recommended edits
        edited_content, edits = self._apply_recommended_edits(
            redacted_content,
            review.get("recommendations", [])
        )
        
        # Add required disclaimers
        final_content, disclaimers_added = self._add_disclaimers(
            edited_content,
            review.get("policy_violations", [])
        )
        
        # Create redline document (track changes)
        redline_document = self._create_redline(
            content,
            final_content,
            redactions,
            edits
        )
        
        # Prepare proposed changes for HITL review
        proposed_changes = self._prepare_proposed_changes(
            redactions,
            edits,
            disclaimers_added
        )
        
        # Check if final HITL approval needed
        requires_final_hitl = self._check_final_hitl_requirement(
            review,
            classification,
            policies
        )
        
        return {
            "final_document": final_content,
            "redline_document": redline_document,
            "redactions_count": len(redactions),
            "edits_count": len(edits),
            "disclaimers_added": disclaimers_added,
            "proposed_changes": proposed_changes,
            "requires_final_hitl": requires_final_hitl,
            "changes_count": len(redactions) + len(edits) + len(disclaimers_added),
            "draft_summary": {
                "pii_redacted": len(redactions),
                "clauses_edited": len([e for e in edits if e["type"] == "clause_edit"]),
                "content_removed": len([e for e in edits if e["type"] == "content_removal"]),
                "disclaimers_added": len(disclaimers_added)
            }
        }
    
    def _apply_pii_redactions(
        self,
        content: str,
        pii_entities: List[Dict[str, Any]]
    ) -> tuple:
        """
        Apply PII redactions to content
        """
        redactions = []
        redacted_content = content
        
        # Sort entities by position (reverse) to maintain positions during replacement
        sorted_entities = sorted(pii_entities, key=lambda x: x["start_pos"], reverse=True)
        
        for entity in sorted_entities:
            original_text = entity["text"]
            redacted_value = entity["redacted_value"]
            start_pos = entity["start_pos"]
            end_pos = entity["end_pos"]
            
            # Apply redaction
            redacted_content = (
                redacted_content[:start_pos] +
                redacted_value +
                redacted_content[end_pos:]
            )
            
            redactions.append({
                "id": entity["id"],
                "type": entity["type"],
                "original": original_text,
                "redacted": redacted_value,
                "position": start_pos,
                "risk_level": entity["risk_level"]
            })
        
        return redacted_content, redactions
    
    def _apply_recommended_edits(
        self,
        content: str,
        recommendations: List[Dict[str, Any]]
    ) -> tuple:
        """
        Apply recommended edits based on reviewer recommendations
        """
        edits = []
        edited_content = content
        
        for rec in recommendations:
            if rec["type"] == "remove_content":
                # Remove forbidden advice
                text_to_remove = rec.get("text", "")
                if text_to_remove:
                    pattern = re.escape(text_to_remove)
                    if re.search(pattern, edited_content, re.IGNORECASE):
                        edited_content = re.sub(
                            pattern,
                            "[CONTENT REMOVED - POLICY VIOLATION]",
                            edited_content,
                            flags=re.IGNORECASE
                        )
                        edits.append({
                            "type": "content_removal",
                            "reason": "policy_violation",
                            "original": text_to_remove,
                            "replacement": "[CONTENT REMOVED - POLICY VIOLATION]"
                        })
            
            elif rec["type"] == "clause_revision":
                # Mark clause for revision (in real implementation, would have AI suggest edits)
                clause_id = rec.get("target", "")
                edits.append({
                    "type": "clause_edit",
                    "clause_id": clause_id,
                    "recommendation": rec["description"],
                    "rationale": rec.get("rationale", "")
                })
        
        return edited_content, edits
    
    def _add_disclaimers(
        self,
        content: str,
        policy_violations: List[Dict[str, Any]]
    ) -> tuple:
        """
        Add required disclaimers
        """
        disclaimers_added = []
        final_content = content
        
        # Check which disclaimers are needed
        needed_disclaimers = set()
        for violation in policy_violations:
            if violation["type"] == "missing_disclaimer":
                disclaimer_type = violation.get("disclaimer_type")
                if disclaimer_type:
                    needed_disclaimers.add(disclaimer_type)
        
        # Add disclaimers
        for disclaimer_type in needed_disclaimers:
            if disclaimer_type in self.DISCLAIMER_TEMPLATES:
                disclaimer_text = self.DISCLAIMER_TEMPLATES[disclaimer_type]
                final_content += disclaimer_text
                disclaimers_added.append({
                    "type": disclaimer_type,
                    "text": disclaimer_text.strip()
                })
        
        return final_content, disclaimers_added
    
    def _create_redline(
        self,
        original: str,
        final: str,
        redactions: List[Dict[str, Any]],
        edits: List[Dict[str, Any]]
    ) -> str:
        """
        Create redline document showing tracked changes
        """
        redline = "# REDLINE DOCUMENT - TRACKED CHANGES\n\n"
        redline += "## Summary of Changes\n\n"
        
        # List redactions
        if redactions:
            redline += "### PII Redactions\n\n"
            for i, red in enumerate(redactions, 1):
                redline += f"{i}. **{red['type'].upper()}** (Risk: {red['risk_level']})\n"
                redline += f"   - Original: `{red['original']}`\n"
                redline += f"   - Redacted: `{red['redacted']}`\n\n"
        
        # List edits
        if edits:
            redline += "### Content Edits\n\n"
            for i, edit in enumerate(edits, 1):
                if edit["type"] == "content_removal":
                    redline += f"{i}. **REMOVED** (Reason: {edit['reason']})\n"
                    redline += f"   - Original: `{edit['original'][:100]}...`\n"
                    redline += f"   - Replaced with: `{edit['replacement']}`\n\n"
                elif edit["type"] == "clause_edit":
                    redline += f"{i}. **CLAUSE REVISION NEEDED** ({edit['clause_id']})\n"
                    redline += f"   - {edit['recommendation']}\n"
                    redline += f"   - Rationale: {edit['rationale']}\n\n"
        
        # Add the final document
        redline += "\n---\n\n## Final Document\n\n"
        redline += final
        
        return redline
    
    def _prepare_proposed_changes(
        self,
        redactions: List[Dict[str, Any]],
        edits: List[Dict[str, Any]],
        disclaimers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare proposed changes for HITL review
        """
        changes = []
        
        # Add redactions as proposed changes
        for red in redactions:
            if red["risk_level"] == "high":
                changes.append({
                    "id": f"change_{red['id']}",
                    "type": "redaction",
                    "pii_type": red["type"],
                    "original": red["original"],
                    "proposed": red["redacted"],
                    "risk_level": red["risk_level"],
                    "requires_approval": True
                })
        
        # Add edits as proposed changes
        for edit in edits:
            if edit["type"] == "content_removal":
                changes.append({
                    "id": f"change_edit_{len(changes)}",
                    "type": "removal",
                    "original": edit["original"],
                    "reason": edit["reason"],
                    "requires_approval": True
                })
        
        return changes
    
    def _check_final_hitl_requirement(
        self,
        review: Dict[str, Any],
        classification: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if final HITL approval needed before external sharing
        """
        overall_risk = review.get("overall_risk", "low")
        
        # Always require HITL for high-risk documents
        if overall_risk == "high":
            return True
        
        # Check for third-party sharing
        compliance_policy = next(
            (p for p in policies if p.get("name") == "Legal Compliance Policy"),
            None
        )
        
        if compliance_policy:
            sharing_rule = compliance_policy.get("rules", {}).get("third_party_sharing")
            if sharing_rule == "prohibited_without_hitl":
                # In real implementation, would check if document is being shared
                # For demo, require HITL for NDAs
                if classification.get("doc_type") == "nda":
                    return True
        
        return False

