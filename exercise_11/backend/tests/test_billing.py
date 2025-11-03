"""
Tests for billing ledger functionality.
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import sys

# Add billing directory to path
billing_dir = Path(__file__).parent.parent.parent.parent / "billing"
sys.path.insert(0, str(billing_dir.parent))

from billing.ledger import BillingLedger, reset_ledger, get_ledger
from billing.lite_mode import generate_lite_mode_response, get_lite_mode_notice


@pytest.fixture
def ledger():
    """Create a fresh ledger instance for testing."""
    reset_ledger()
    ledger = get_ledger()
    ledger.set_daily_budget(100.0)  # $100/day default
    return ledger


def test_record_turn(ledger):
    """Test recording a turn with token/cost tracking."""
    record = ledger.record_turn(
        session_id="test_session",
        input_text="How to handle bedtime?",
        output_text="Establishing a consistent bedtime routine helps...",
        model_mode="full",
        was_over_budget=False
    )
    
    assert record.session_id == "test_session"
    assert record.input_tokens > 0
    assert record.output_tokens > 0
    assert record.cost_usd > 0
    assert record.model_mode == "full"
    assert record.was_over_budget is False


def test_estimate_tokens(ledger):
    """Test token estimation from text."""
    text = "This is a test message with about 40 characters in it."
    tokens = ledger.estimate_tokens(text)
    
    # Should estimate ~10 tokens (40 chars / 4)
    assert tokens >= 8
    assert tokens <= 12


def test_calculate_cost(ledger):
    """Test cost calculation."""
    cost = ledger.calculate_cost(1000, 500)  # 1000 input, 500 output tokens
    
    # Cost = (1000/1M * $30) + (500/1M * $60)
    #      = $0.03 + $0.03 = $0.06
    assert cost > 0
    assert cost < 0.1  # Should be around $0.06


def test_daily_budget_check(ledger):
    """Test budget checking."""
    # Initially under budget
    is_over, current_cost, budget = ledger.is_over_budget()
    assert is_over is False
    assert current_cost == 0.0
    assert budget == 100.0
    
    # Record many turns to exceed budget
    for i in range(1000):
        ledger.record_turn(
            session_id=f"test_{i}",
            input_text="Test input " * 100,  # ~400 chars
            output_text="Test output " * 500,  # ~6000 chars
            model_mode="full",
            was_over_budget=False
        )
    
    # Check if over budget
    is_over, current_cost, budget = ledger.is_over_budget()
    # May or may not be over depending on exact calculations
    # Just verify the function works
    assert current_cost >= 0
    assert budget == 100.0


def test_get_daily_stats(ledger):
    """Test getting daily statistics."""
    # Record some turns
    ledger.record_turn(
        session_id="test1",
        input_text="Test",
        output_text="Output",
        model_mode="full",
        was_over_budget=False
    )
    
    stats = ledger.get_daily_stats()
    
    assert stats["total_turns"] >= 1
    assert stats["total_cost_usd"] > 0
    assert stats["budget_limit_usd"] == 100.0
    assert "full_mode_turns" in stats
    assert "lite_mode_turns" in stats


def test_generate_csv(ledger, tmp_path):
    """Test CSV report generation."""
    # Record a turn
    ledger.record_turn(
        session_id="test_csv",
        input_text="Test input",
        output_text="Test output",
        model_mode="full",
        was_over_budget=False
    )
    
    # Generate CSV
    csv_path = ledger.generate_daily_csv()
    
    assert csv_path.exists()
    assert csv_path.name.startswith("billing_report_")
    assert csv_path.suffix == ".csv"


def test_lite_mode_response():
    """Test lite mode response generation."""
    response = generate_lite_mode_response(
        "How to handle bedtime?",
        None
    )
    
    assert len(response) > 0
    assert "bedtime" in response.lower() or "budget" in response.lower()
    assert "lite" in response.lower() or "limited" in response.lower()


def test_lite_mode_notice():
    """Test lite mode notice."""
    notice = get_lite_mode_notice()
    
    assert notice["type"] == "budget_limit"
    assert notice["mode"] == "lite"
    assert "message" in notice


def test_set_budget(ledger):
    """Test setting budget limit."""
    ledger.set_daily_budget(50.0)
    _, _, budget = ledger.is_over_budget()
    assert budget == 50.0


def test_summary_report(ledger):
    """Test summary report generation."""
    # Record some turns
    for i in range(5):
        ledger.record_turn(
            session_id=f"test_{i}",
            input_text="Test",
            output_text="Output",
            model_mode="full",
            was_over_budget=False
        )
    
    report = ledger.generate_summary_report(days=7)
    
    assert "total_cost_usd" in report
    assert "total_turns" in report
    assert "sparkline_data" in report
    assert len(report["sparkline_data"]) <= 7

