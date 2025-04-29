"""BotDefenseTool for managing anti-bot detection measures."""

import random
import time
from typing import Any, Dict, List, Optional

from fake_useragent import UserAgent
from pydantic import BaseModel, Field, HttpUrl

from tools.interfaces import ToolInterface


class BotDefenseConfig(BaseModel):
    """Configuration for BotDefenseTool."""

    min_delay: float = Field(
        default=1.0,
        description="Minimum delay between requests in seconds",
        ge=0.0,
    )
    max_delay: float = Field(
        default=3.0,
        description="Maximum delay between requests in seconds",
        ge=0.0,
    )
    user_agent_type: str = Field(
        default="random",
        description="Type of User-Agent to use (random, chrome, firefox, etc.)",
    )
    proxies: List[HttpUrl] = Field(
        default_factory=list,
        description="List of proxy URLs to rotate through",
    )
    requests_per_minute: int = Field(
        default=30,
        description="Maximum number of requests per minute",
        ge=1,
    )
    enable_cookies: bool = Field(
        default=True,
        description="Whether to enable cookie management",
    )


class BotDefenseTool(ToolInterface):
    """Tool for implementing anti-bot detection measures."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize the BotDefenseTool.

        Args:
            **kwargs: Configuration parameters for BotDefenseConfig
        """
        self.config = BotDefenseConfig(**kwargs)
        self.user_agent = UserAgent()
        self._last_request_time: Optional[float] = None
        self._request_times: List[float] = []
        self._current_proxy_index: int = 0
        self._cookies: Dict[str, str] = {}

    def _rotate_proxy(self) -> Optional[Dict[str, str]]:
        """Rotate to the next proxy in the list.

        Returns:
            Dict containing proxy configuration or None if no proxies configured
        """
        if not self.config.proxies:
            return None

        proxy_url = self.config.proxies[self._current_proxy_index]
        self._current_proxy_index = (self._current_proxy_index + 1) % len(
            self.config.proxies
        )

        return {
            "http": str(proxy_url),
            "https": str(proxy_url),
        }

    def _enforce_rate_limit(self) -> None:
        """Enforce the configured request rate limit."""
        now = time.time()
        minute_ago = now - 60

        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if t > minute_ago]

        # If we're at or over the limit, sleep until we can make another request
        if len(self._request_times) >= self.config.requests_per_minute:
            sleep_time = 60.0 - (now - self._request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._request_times = self._request_times[1:]

    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute anti-bot measures and return headers.

        Returns:
            Dict containing headers, proxy settings, and cookies
        """
        now = time.time()

        # Add delay if there was a previous request
        if self._last_request_time is not None:
            delay = random.uniform(
                self.config.min_delay, self.config.max_delay
            )  # nosec B311 - not used for cryptographic purposes
            time_since_last = now - self._last_request_time
            if time_since_last < delay:
                time.sleep(delay - time_since_last)

        # Clean up old requests and check rate limit
        minute_ago = now - 60
        self._request_times = [t for t in self._request_times if t > minute_ago]
        if len(self._request_times) >= self.config.requests_per_minute:
            self._enforce_rate_limit()

        # Update request timing after rate limiting
        self._last_request_time = now
        self._request_times.append(now)

        # Get appropriate User-Agent
        if self.config.user_agent_type == "random":
            user_agent = self.user_agent.random
        else:
            user_agent = getattr(self.user_agent, self.config.user_agent_type)

        # Generate browser fingerprint
        screen_resolution = (
            random.choice(  # nosec B311 - not used for cryptographic purposes
                [
                    "1920x1080",
                    "1366x768",
                    "1536x864",
                    "1440x900",
                    "1280x720",
                    "2560x1440",
                ]
            )
        )
        color_depth = random.choice(
            ["24", "32"]
        )  # nosec B311 - not used for cryptographic purposes
        platform = random.choice(
            ["Win32", "MacIntel", "Linux x86_64"]
        )  # nosec B311 - not used for cryptographic purposes

        result = {
            "headers": {
                "User-Agent": user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": f'"{user_agent}"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": f'"{platform}"',
                "Viewport-Width": screen_resolution.split("x")[0],
                "Screen-Resolution": screen_resolution,
                "Color-Depth": color_depth,
            }
        }

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

        # Add proxy configuration if available
        proxy_config = self._rotate_proxy()
        if proxy_config:
            result["proxy"] = proxy_config

        # Add cookies if enabled
        if self.config.enable_cookies and self._cookies:
            result["cookies"] = self._cookies

        return result

    def update_cookies(self, cookies: Dict[str, str]) -> None:
        """Update stored cookies.

        Args:
            cookies: Dictionary of cookies to update
        """
        if self.config.enable_cookies:
            self._cookies.update(cookies)

    @property
    def name(self) -> str:
        """Return the tool's name."""
        return "BotDefenseTool"

    @property
    def description(self) -> str:
        """Get tool description."""
        return (
            "Tool for managing anti-bot detection measures including delays, "
            "user agents, proxies, and cookies"
        )

    @property
    def input_types(self) -> Dict[str, Any]:
        """Return the tool's input parameter types."""
        return {
            "min_delay": (float, "Minimum delay between requests in seconds"),
            "max_delay": (float, "Maximum delay between requests in seconds"),
            "user_agent_type": (
                str,
                "Type of User-Agent to use (random, chrome, firefox, etc.)",
            ),
            "proxies": (List[HttpUrl], "List of proxy URLs to rotate through"),
            "requests_per_minute": (
                int,
                "Maximum number of requests per minute",
            ),
            "enable_cookies": (bool, "Whether to enable cookie management"),
        }

    @property
    def output_type(self) -> Any:
        """Return the tool's output type."""
        return Dict[str, Any]
