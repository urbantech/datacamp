"""PlaywrightCrawlerTool implementation."""

import asyncio
import json
from typing import Any, Dict, Optional, Union

from playwright.async_api import Browser, Page, async_playwright

from tools.bot_defense.tool import BotDefenseTool
from tools.interfaces import ToolInterface
from tools.playwright_crawler.config import PlaywrightConfig


class PlaywrightCrawlerTool(ToolInterface):
    """A tool for crawling web pages using Playwright."""

    def __init__(
        self,
        bot_defense: Optional[BotDefenseTool] = None,
        config: Optional[PlaywrightConfig] = None,
    ):
        """Initialize the crawler with optional bot defense and config."""
        self.config = config or PlaywrightConfig()
        self._bot_defense = bot_defense or BotDefenseTool()
        self._browser: Optional[Browser] = None

    async def init_browser(self) -> None:
        """Initialize the browser if not already initialized."""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=self.config.headless,
                args=["--no-sandbox"] if not self.config.headless else None,
            )

    async def get_new_page(self) -> Page:
        """Get a new page with configured viewport and user agent."""
        await self.init_browser()
        if not self._browser:
            raise RuntimeError("Browser initialization failed")

        page = await self._browser.new_page()
        if self.config.viewport_width and self.config.viewport_height:
            await page.set_viewport_size(
                {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                }
            )
        if self.config.user_agent:
            await page.set_extra_http_headers(
                {"User-Agent": self.config.user_agent}
            )
        return page

    async def fetch(
        self, url: str, retries: int = 1
    ) -> Dict[str, Union[str, int, dict, None]]:
        """Fetch a URL with retries and return the page content and metadata."""
        last_error = None
        for attempt in range(retries):
            page = None
            try:
                page = await self._bot_defense.get_new_page()
                await self._bot_defense.handle_page(page, url)

                response = await page.goto(
                    url,
                    wait_until=self.config.wait_until,
                    timeout=self.config.timeout,
                )

                if not response:
                    raise RuntimeError("No response received")

                await page.wait_for_load_state()
                content = await page.content()
                status = response.status
                headers = dict(response.headers)

                try:
                    json_data = await response.json()
                except (json.JSONDecodeError, AttributeError, ValueError):
                    json_data = None

                result = {
                    "url": url,
                    "content": content,
                    "status": status,
                    "headers": headers,
                    "error": None,
                    "json": json_data,
                }

                return result

            except Exception as e:
                last_error = str(e)
                if attempt < retries - 1:
                    await asyncio.sleep(1)  # Wait before retrying
            finally:
                if page:
                    await page.close()

        return {
            "url": url,
            "content": None,
            "status": None,
            "headers": None,
            "error": last_error,
            "json": None,
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._bot_defense:
            await self._bot_defense.cleanup()

    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality.

        Args:
            **kwargs: Keyword arguments for tool execution

        Returns:
            Dict containing tool execution results
        """
        url = kwargs.get("url")
        if not isinstance(url, str):
            raise ValueError("URL must be a string")

        retries = kwargs.get("retries", 1)
        if not isinstance(retries, int) or retries < 1:
            raise ValueError("Retries must be a positive integer")

        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.fetch(url, retries))
        finally:
            loop.run_until_complete(self.cleanup())

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "PlaywrightCrawlerTool"

    @property
    def description(self) -> str:
        """Get the tool description."""
        return "Tool for crawling web pages using Playwright"

    @property
    def parameters(self) -> Dict[str, str]:
        """Get the tool parameters."""
        return {
            "url": "URL to crawl",
            "retries": "Number of retries on failure",
        }

    @property
    def returns(self) -> Dict[str, str]:
        """Get the tool return values."""
        return {
            "content": "Page content",
            "status": "HTTP status code",
            "headers": "Response headers",
            "error": "Error message if any",
            "json": "JSON response if available",
        }

    @property
    def input_types(self) -> Dict[str, Any]:
        """Get the tool input parameter types."""
        return {"url": str, "retries": int}

    @property
    def output_type(self) -> Any:
        """Get the tool output type."""
        return Dict[str, Union[str, int, dict, None]]
