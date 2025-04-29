"""Unit tests for BotDefenseTool."""

from typing import Any, Dict, get_origin
from unittest.mock import Mock, patch

import pytest
from pydantic import HttpUrl

from tools.bot_defense import BotDefenseTool
from tools.interfaces import ToolInterface


def test_tool_interface_abstract():
    """Test that ToolInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ToolInterface()


def test_bot_defense_interface_methods():
    """Test that BotDefenseTool implements all required interface methods."""
    tool = BotDefenseTool()

    # Test interface properties
    assert isinstance(tool.name, str)
    assert isinstance(tool.description, str)
    assert isinstance(tool.input_types, dict)
    assert get_origin(tool.output_type) == dict


def test_bot_defense_initialization():
    """Test BotDefenseTool initialization with default values."""
    tool = BotDefenseTool()
    assert tool.config.min_delay == 1.0
    assert tool.config.max_delay == 3.0
    assert tool.config.user_agent_type == "random"
    assert tool.config.proxies == []
    assert tool.config.requests_per_minute == 30
    assert tool.config.enable_cookies is True


def test_bot_defense_custom_config():
    """Test BotDefenseTool initialization with custom values."""
    tool = BotDefenseTool(
        min_delay=2.0,
        max_delay=5.0,
        user_agent_type="chrome",
        requests_per_minute=60,
        enable_cookies=False,
        proxies=[
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
        ],
    )
    assert tool.config.min_delay == 2.0
    assert tool.config.max_delay == 5.0
    assert tool.config.user_agent_type == "chrome"
    assert tool.config.requests_per_minute == 60
    assert tool.config.enable_cookies is False
    assert len(tool.config.proxies) == 2
    assert all(isinstance(p, HttpUrl) for p in tool.config.proxies)


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

    # Check browser fingerprinting headers
    assert "Sec-Ch-Ua" in headers
    assert "Sec-Ch-Ua-Mobile" in headers
    assert "Sec-Ch-Ua-Platform" in headers
    assert "Viewport-Width" in headers
    assert "Screen-Resolution" in headers
    assert "Color-Depth" in headers


def test_bot_defense_delay():
    """Test that BotDefenseTool implements delays between requests."""
    with (
        patch("time.sleep") as mock_sleep,
        patch("random.uniform") as mock_uniform,
    ):
        mock_uniform.return_value = 1.0  # Fix the random delay
        tool = BotDefenseTool(
            min_delay=1.0, max_delay=1.0
        )  # Fixed delay for testing

        # First request should have no delay
        tool.run()
        assert not mock_sleep.called

        # Second request should have ~1 second delay
        tool.run()
        mock_sleep.assert_called_once()
        assert (
            abs(mock_sleep.call_args[0][0] - 1.0) < 0.001
        )  # Allow small floating point difference


def test_bot_defense_user_agent_types():
    """Test different User-Agent types."""
    # Create a mock UserAgent instance
    mock_ua = Mock()
    mock_ua.random = "UA1"
    mock_ua.chrome = "Chrome/100.0.0.0"

    # Create a mock UserAgent class that returns our mock instance
    mock_ua_class = Mock(return_value=mock_ua)

    # Patch the UserAgent class to return our mock
    with patch("tools.bot_defense.tool.UserAgent", mock_ua_class):
        tool = BotDefenseTool()

        # Test random User-Agent
        tool.config.user_agent_type = "random"
        result1 = tool.run()
        assert result1["headers"]["User-Agent"] == "UA1"

        # Test specific browser User-Agent
        tool.config.user_agent_type = "chrome"
        result2 = tool.run()
        assert result2["headers"]["User-Agent"] == "Chrome/100.0.0.0"


def test_bot_defense_proxy_rotation():
    """Test proxy rotation functionality."""
    proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080",
    ]
    tool = BotDefenseTool(proxies=proxies)

    # First request should use first proxy
    result1 = tool.run()
    assert "proxy" in result1
    assert result1["proxy"]["http"].rstrip("/") == proxies[0]
    assert result1["proxy"]["https"].rstrip("/") == proxies[0]

    # Second request should use second proxy
    result2 = tool.run()
    assert "proxy" in result2
    assert result2["proxy"]["http"].rstrip("/") == proxies[1]
    assert result2["proxy"]["https"].rstrip("/") == proxies[1]

    # After all proxies are used, should cycle back to first
    tool.run()  # Uses third proxy
    result4 = tool.run()  # Should cycle back to first
    assert result4["proxy"]["http"].rstrip("/") == proxies[0]
    assert result4["proxy"]["https"].rstrip("/") == proxies[0]


def test_bot_defense_rate_limiting():
    """Test request rate limiting."""
    with (
        patch("time.sleep") as mock_sleep,
        patch("time.time") as mock_time,
        patch("random.uniform") as mock_uniform,
    ):
        # Mock time to return increasing values
        mock_time.side_effect = [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
        ]  # All requests at t=3 for consistent timing
        mock_uniform.return_value = 0.0  # No random delay
        tool = BotDefenseTool(
            requests_per_minute=2, min_delay=0.0, max_delay=0.0
        )

        # First request should be quick
        tool.run()
        assert not mock_sleep.called

        # Second request should be quick
        tool.run()
        assert not mock_sleep.called

        # Third request should trigger rate limiting
        tool.run()
        mock_sleep.assert_called_once()
        assert (
            mock_sleep.call_args[0][0] == 57.0
        )  # Should wait until first request is 60s old


def test_bot_defense_cookie_management():
    """Test cookie management functionality."""
    tool = BotDefenseTool()

    # Initially no cookies
    result = tool.run()
    assert "cookies" not in result

    # Update cookies
    test_cookies = {"sessionid": "abc123", "csrftoken": "xyz789"}
    tool.update_cookies(test_cookies)

    # Next request should include cookies
    result = tool.run()
    assert "cookies" in result
    assert result["cookies"] == test_cookies

    # Test with cookies disabled
    tool = BotDefenseTool(enable_cookies=False)
    tool.update_cookies(test_cookies)
    result = tool.run()
    assert "cookies" not in result


def test_bot_defense_invalid_config():
    """Test that invalid configuration raises appropriate errors."""
    with pytest.raises(ValueError):
        BotDefenseTool(min_delay=-1.0)

    with pytest.raises(ValueError):
        BotDefenseTool(max_delay=-1.0)

    with pytest.raises(ValueError):
        BotDefenseTool(requests_per_minute=0)

    with pytest.raises(ValueError):
        BotDefenseTool(proxies=["not a valid url"])


def test_bot_defense_proxy_rotation_empty():
    """Test proxy rotation with no proxies configured."""
    tool = BotDefenseTool()
    result = tool.run()
    assert "proxy" not in result


def test_bot_defense_rate_limit_cleanup():
    """Test rate limit cleanup of old requests."""
    with patch("time.sleep") as mock_sleep, patch("time.time") as mock_time:
        # Mock time to simulate old requests
        mock_time.side_effect = [
            0,
            61,
            62,
        ]  # First request at t=0, check at t=61
        tool = BotDefenseTool(requests_per_minute=1)

        # Make first request at t=0
        tool.run()

        # Second request at t=61 (old request should be cleaned)
        tool.run()
        assert (
            not mock_sleep.called
        )  # No delay needed since old request was cleaned


def test_bot_defense_empty_cookies():
    """Test cookie management with no cookies set."""
    tool = BotDefenseTool()
    result = tool.run()
    assert "cookies" not in result


def test_bot_defense_interface_properties():
    """Test interface property methods."""
    tool = BotDefenseTool()

    # Test name property
    assert tool.name == "BotDefenseTool"

    # Test description property
    assert "anti-bot detection" in tool.description.lower()

    # Test input_types property
    input_types = tool.input_types
    assert isinstance(input_types, dict)
    assert "min_delay" in input_types
    assert "max_delay" in input_types
    assert "user_agent_type" in input_types
    assert "proxies" in input_types
    assert "requests_per_minute" in input_types
    assert "enable_cookies" in input_types

    # Test output_type property
    assert tool.output_type == Dict[str, Any]
