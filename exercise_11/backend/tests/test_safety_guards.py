"""
Unit tests for safety guard functionality.
Tests all 20 red-team prompts from safety_policy.json.
"""

import pytest
import json
from pathlib import Path
from app.guards import SafetyGuard, SafetyClassification, get_safety_guard


# Get the path to safety_policy.json
PROJECT_ROOT = Path(__file__).parent.parent.parent
POLICY_PATH = PROJECT_ROOT / "config" / "safety_policy.json"


def load_red_team_prompts():
    """Load red-team prompts from safety_policy.json"""
    with open(POLICY_PATH, 'r', encoding='utf-8') as f:
        policy = json.load(f)
    return policy.get("red_team_prompts", [])


@pytest.fixture
def guard():
    """Create a safety guard instance for testing"""
    return SafetyGuard(policy_path=str(POLICY_PATH))


class TestSafetyGuardBasics:
    """Basic functionality tests"""
    
    def test_guard_initialization(self, guard):
        """Test that guard initializes correctly"""
        assert guard is not None
        assert guard.policy is not None
        assert guard.keyword_patterns is not None
        assert guard.refusal_templates is not None
    
    def test_safe_message_passes(self, guard):
        """Test that safe parenting questions pass through"""
        classification, refusal, metadata = guard.check_message(
            "How can I help my child learn to share toys?"
        )
        assert classification == SafetyClassification.SAFE
        assert refusal is None
    
    def test_empty_message_is_safe(self, guard):
        """Test that empty messages are treated as safe"""
        classification, refusal, metadata = guard.check_message("")
        assert classification == SafetyClassification.SAFE
    
    def test_whitespace_message_is_safe(self, guard):
        """Test that whitespace-only messages are treated as safe"""
        classification, refusal, metadata = guard.check_message("   \n\t  ")
        assert classification == SafetyClassification.SAFE


class TestRedTeamPrompts:
    """Test all 20 red-team prompts from safety_policy.json"""
    
    @pytest.mark.parametrize("test_case", load_red_team_prompts())
    def test_red_team_prompt(self, guard, test_case):
        """
        Test a single red-team prompt.
        
        This test is parameterized over all red-team prompts from the config.
        Each prompt should trigger the expected classification and template.
        """
        prompt = test_case["prompt"]
        expected_classification_str = test_case["expected_classification"]
        expected_template = test_case["expected_template"]
        test_id = test_case["id"]
        
        # Map string to enum
        expected_classification = SafetyClassification(expected_classification_str)
        
        # Check the message
        classification, refusal_message, metadata = guard.check_message(prompt, session_id=f"test_{test_id}")
        
        # Assert classification matches
        assert classification == expected_classification, (
            f"Test {test_id} failed: Expected {expected_classification_str}, "
            f"got {classification.value}. Prompt: {prompt}"
        )
        
        # If blocked or escalated, should have a refusal message
        if classification != SafetyClassification.SAFE:
            assert refusal_message is not None, (
                f"Test {test_id} failed: Should have refusal message for {expected_classification_str}"
            )
            assert len(refusal_message) > 0, (
                f"Test {test_id} failed: Refusal message should not be empty"
            )
            
            # Check that the correct template was used
            # The template should contain key phrases from the expected template type
            template_keywords = {
                "medical": ["medical", "pediatrician", "healthcare provider"],
                "legal": ["legal", "attorney", "law"],
                "professional_services": ["professional", "therapist", "licensed"],
                "crisis": ["crisis", "emergency", "911", "988"],
                "general_out_of_scope": ["scope", "specialize", "parenting"]
            }
            
            if expected_template in template_keywords:
                keywords = template_keywords[expected_template]
                message_lower = refusal_message.lower()
                assert any(kw in message_lower for kw in keywords), (
                    f"Test {test_id} failed: Refusal message should contain keywords "
                    f"from {expected_template} template. Message: {refusal_message}"
                )
        
        # Metadata should contain match information
        if classification != SafetyClassification.SAFE:
            assert "matched_categories" in metadata
            assert len(metadata["matched_categories"]) > 0
            assert "primary_category" in metadata
            assert metadata["primary_category"] is not None


class TestSafetyGuardCategories:
    """Test different safety categories"""
    
    def test_medical_blocked(self, guard):
        """Test medical requests are blocked"""
        classification, refusal, metadata = guard.check_message(
            "What medicine should I give my child for a fever?"
        )
        assert classification == SafetyClassification.BLOCKED
        assert "medical" in refusal.lower() or "pediatrician" in refusal.lower()
    
    def test_crisis_escalated(self, guard):
        """Test crisis situations are escalated"""
        classification, refusal, metadata = guard.check_message(
            "My child wants to kill themselves"
        )
        assert classification == SafetyClassification.ESCALATE
        assert "crisis" in refusal.lower() or "emergency" in refusal.lower() or "911" in refusal
    
    def test_legal_blocked(self, guard):
        """Test legal requests are blocked"""
        classification, refusal, metadata = guard.check_message(
            "I need help with my custody battle"
        )
        assert classification == SafetyClassification.BLOCKED
        assert "legal" in refusal.lower() or "attorney" in refusal.lower()
    
    def test_professional_services_blocked(self, guard):
        """Test professional service requests are blocked"""
        classification, refusal, metadata = guard.check_message(
            "Can you evaluate if my child needs therapy?"
        )
        assert classification == SafetyClassification.BLOCKED


class TestSafetyGuardIntegration:
    """Integration tests"""
    
    def test_get_safety_guard_singleton(self):
        """Test that get_safety_guard returns singleton"""
        guard1 = get_safety_guard()
        guard2 = get_safety_guard()
        assert guard1 is guard2
    
    def test_check_message_safety_convenience(self):
        """Test convenience function works"""
        from app.guards import check_message_safety
        
        classification, refusal, metadata = check_message_safety(
            "My child has a fever, what medicine?"
        )
        assert classification == SafetyClassification.BLOCKED
        assert refusal is not None


class TestSafetyGuardMetadata:
    """Test metadata and logging"""
    
    def test_metadata_structure(self, guard):
        """Test that metadata contains expected fields"""
        classification, refusal, metadata = guard.check_message(
            "What's the dosage for antibiotics?",
            session_id="test_session_123"
        )
        
        assert "matched_categories" in metadata
        assert "primary_category" in metadata
        assert "matches" in metadata
        assert "template_used" in metadata
        assert "timestamp" in metadata
        assert metadata["session_id"] == "test_session_123"
    
    def test_safe_message_has_minimal_metadata(self, guard):
        """Test that safe messages have minimal metadata"""
        classification, refusal, metadata = guard.check_message(
            "How do I help my child share toys?",
            session_id="test_session_456"
        )
        
        assert classification == SafetyClassification.SAFE
        assert "timestamp" in metadata
        assert metadata.get("matched_categories") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

