"""Unit tests for BotDefenseTool."""
import time
from typing import Dict

import pytest

from tools.bot_defense import BotDefenseTool


def test_bot_defense_initialization():
    """Test BotDefenseTool initialization with default values."""
    tool = BotDefenseTool()
    assert tool.config.min_delay == 1.0
    assert tool.config.max_delay == 3.0
    assert tool.config.user_agent_type == "random"


def test_bot_defense_custom_config():
    """Test BotDefenseTool initialization with custom values."""
    tool = BotDefenseTool(min_delay=2.0, max_delay=5.0, user_agent_type="chrome")
    assert tool.config.min_delay == 2.0
    assert tool.config.max_delay == 5.0
    assert tool.config.user_agent_type == "chrome"


def test_bot_defense_headers():
    """Test that BotDefenseTool returns valid headers."""
    tool = BotDefenseTool()
    result = tool.run()
    
    assert isinstance(result, dict)
    assert "headers" in result
    headers = result["headers"]
    
    # Check required headers
    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Accept-Language" in headers
    assert len(headers["User-Agent"]) > 0


def test_bot_defense_delay():
    """Test that BotDefenseTool implements delays between requests."""
    tool = BotDefenseTool(min_delay=1.0, max_delay=1.0)  # Fixed delay for testing
    
    # First request should have no delay
    start = time.time()
    tool.run()
    first_duration = time.time() - start
    assert first_duration < 0.1  # Should be near-instant
    
    # Second request should have ~1 second delay
    start = time.time()
    tool.run()
    second_duration = time.time() - start
    assert 0.9 <= second_duration <= 1.1  # Allow 0.1s margin


def test_bot_defense_user_agent_types():
    """Test different User-Agent types."""
    tool = BotDefenseTool()
    
    # Test random User-Agent
    tool.config.user_agent_type = "random"
    result1 = tool.run()
    result2 = tool.run()
    # Two random User-Agents should usually be different
    assert result1["headers"]["User-Agent"] != result2["headers"]["User-Agent"]
    
    # Test specific browser User-Agent
    tool.config.user_agent_type = "chrome"
    result = tool.run()
    assert "Chrome" in result["headers"]["User-Agent"]


def test_bot_defense_invalid_config():
    """Test that invalid configuration raises appropriate errors."""
    with pytest.raises(ValueError):
        BotDefenseTool(min_delay=-1.0)
    
    with pytest.raises(ValueError):
        BotDefenseTool(max_delay=-1.0)
