"""PlaywrightCrawlerTool for web scraping."""

from typing import Any, Dict, Optional

from playwright.async_api import Browser

from tools.bot_defense.tool import BotDefenseTool
from tools.interfaces import ToolInterface
from tools.playwright_crawler.config import PlaywrightConfig


class PlaywrightCrawlerTool(ToolInterface):
    """Tool for crawling web pages using Playwright."""

    def __init__(
        self,
        browser: Optional[Browser] = None,
        bot_defense: Optional[BotDefenseTool] = None,
        config: Optional[PlaywrightConfig] = None,
    ):
        """Initialize PlaywrightCrawlerTool.

        Args:
            browser: Optional pre-configured browser instance
            bot_defense: Optional BotDefenseTool instance
            config: Optional PlaywrightConfig instance
        """
        self._browser = browser
        self._bot_defense = bot_defense or BotDefenseTool()
        self.config = config or PlaywrightConfig()

    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch a web page using Playwright.

        Args:
            url: URL to fetch

        Returns:
            Dict containing:
                - url: The final URL after any redirects
                - content: The page content (HTML)
                - status: HTTP status code
                - headers: Response headers
                - error: Error message if any
        """
        if not self._browser:
            raise RuntimeError("Browser not initialized")

        page = await self._browser.new_page()

        try:
            response = await page.goto(url)
            if not response:
                return {
                    "url": url,
                    "content": None,
                    "status": None,
                    "headers": {},
                    "error": "Failed to get response",
                }

            if not response.ok:
                return {
                    "url": url,
                    "content": None,
                    "status": response.status,
                    "headers": response.headers,
                    "error": f"Response not OK: {response.status}",
                }

            await self._bot_defense.handle_page(page, url)

            content = await page.content()
            return {
                "url": url,
                "content": content,
                "status": response.status,
                "headers": response.headers,
                "error": None,
            }

        except Exception as e:
            return {
                "url": url,
                "content": None,
                "status": None,
                "headers": {},
                "error": str(e),
            }
        finally:
            await page.close()

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's main functionality.

        Args:
            **kwargs: Tool parameters

        Returns:
            Dict containing scraping results
        """
        import asyncio

        url = kwargs.get("url")
        if not isinstance(url, str):
            raise ValueError("URL must be a string")

        try:
            return asyncio.run(self.fetch(url))
        finally:
            asyncio.run(self.cleanup())

    @property
    def name(self) -> str:
        """Return the tool's name."""
        return "PlaywrightCrawler"

    @property
    def description(self) -> str:
        """Return the tool's description."""
        return (
            "Tool for crawling JavaScript-rendered web pages using Playwright"
        )

    @property
    def input_types(self) -> Dict[str, Any]:
        """Return the tool's input parameter types."""
        return {"url": str}

    @property
    def output_type(self) -> Any:
        """Return the tool's output type."""
        return Dict[str, Any]
