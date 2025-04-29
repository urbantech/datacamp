"""BotDefenseTool for managing anti-bot detection measures."""
import random
import time
from typing import Any, Dict, Optional

from fake_useragent import UserAgent
from pydantic import BaseModel, Field

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

    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, str]:
        """Execute anti-bot measures and return headers.
        
        Returns:
            Dict containing headers with User-Agent and any other anti-bot measures
        """
        # Add delay if there was a previous request
        if self._last_request_time is not None:
            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            time_since_last = time.time() - self._last_request_time
            if time_since_last < delay:
                time.sleep(delay - time_since_last)

        # Update last request time
        self._last_request_time = time.time()

        # Get appropriate User-Agent
        if self.config.user_agent_type == "random":
            user_agent = self.user_agent.random
        else:
            user_agent = getattr(self.user_agent, self.config.user_agent_type)

        return {
            "headers": {
                "User-Agent": user_agent,
                # Add other anti-bot headers as needed
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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
            }
        }

    @property
    def name(self) -> str:
        """Return the tool's name."""
        return "BotDefenseTool"

    @property
    def description(self) -> str:
        """Return the tool's description."""
        return "Tool for implementing anti-bot detection measures using random User-Agents and delays"

    @property
    def input_types(self) -> Dict[str, Any]:
        """Return the tool's input parameter types."""
        return {
            "min_delay": (float, "Minimum delay between requests in seconds"),
            "max_delay": (float, "Maximum delay between requests in seconds"),
            "user_agent_type": (str, "Type of User-Agent to use (random, chrome, firefox, etc.)"),
        }

    @property
    def output_type(self) -> Any:
        """Return the tool's output type."""
        return Dict[str, Dict[str, str]]
