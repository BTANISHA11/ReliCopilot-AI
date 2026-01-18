"""
Simple tests for ReliCopilot-AI core functionality.
Run with: pytest test_basic.py
"""

import pytest
from utils import should_simulate_error, generate_random_error


def test_should_simulate_error_always_false():
    """Test that error simulation returns False with 0% error rate."""
    for _ in range(100):
        assert should_simulate_error(error_rate=0.0) == False


def test_should_simulate_error_always_true():
    """Test that error simulation returns True with 100% error rate."""
    for _ in range(100):
        assert should_simulate_error(error_rate=1.0) == True


def test_generate_random_error():
    """Test that random error generation returns valid format."""
    status_code, error_message = generate_random_error()
    
    # Status code should be an error code
    assert isinstance(status_code, int)
    assert status_code >= 400
    
    # Error message should be a non-empty string
    assert isinstance(error_message, str)
    assert len(error_message) > 0


def test_generate_multiple_errors():
    """Test that multiple calls generate varied errors."""
    errors = [generate_random_error() for _ in range(20)]
    
    # Should have some variety in errors (not all the same)
    unique_errors = set(errors)
    assert len(unique_errors) > 1, "Should generate different error types"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
