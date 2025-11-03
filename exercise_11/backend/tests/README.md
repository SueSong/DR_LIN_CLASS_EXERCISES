# Safety Guard Tests

This directory contains unit tests for the safety guard system (Task 1).

## Running Tests

From the `exercise_11/backend` directory:

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest tests/test_safety_guards.py -v

# Run with detailed output
pytest tests/test_safety_guards.py -v --tb=short

# Run a specific test
pytest tests/test_safety_guards.py::TestRedTeamPrompts::test_red_team_prompt -v
```

## Test Coverage

The test suite includes:

1. **Basic Functionality Tests** (`TestSafetyGuardBasics`)
   - Guard initialization
   - Safe message handling
   - Empty/whitespace message handling

2. **Red-Team Prompt Tests** (`TestRedTeamPrompts`)
   - All 20 red-team prompts from `config/safety_policy.json`
   - Each prompt is tested for correct classification (SAFE/BLOCKED/ESCALATE)
   - Template matching verification

3. **Category Tests** (`TestSafetyGuardCategories`)
   - Medical request blocking
   - Crisis escalation
   - Legal request blocking
   - Professional services blocking

4. **Integration Tests** (`TestSafetyGuardIntegration`)
   - Singleton pattern verification
   - Convenience function testing

5. **Metadata Tests** (`TestSafetyGuardMetadata`)
   - Metadata structure verification
   - Logging validation

## Expected Results

All 20 red-team prompts should:
- ✅ Be correctly classified (BLOCKED or ESCALATE)
- ✅ Generate appropriate refusal messages
- ✅ Use correct response templates
- ✅ Include proper metadata

## Passing Criteria

For Task 1 to pass:
- All 20 red-team prompts must trigger correct refusal/redirect
- All tests in `test_safety_guards.py` should pass
- Response times should be < 100ms (checked in metadata)

## Troubleshooting

If tests fail:
1. Ensure `config/safety_policy.json` exists and is valid JSON
2. Check that the policy file path is correct (relative to project root)
3. Verify all keyword patterns in the policy are properly formatted
4. Check that refusal templates match expected template keys

