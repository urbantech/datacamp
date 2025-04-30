"""PlaywrightCrawlerTool for fetching HTML content from JS-rendered pages."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from playwright.async_api import Browser, Page, async_playwright

from tools.bot_defense.tool import BotDefenseTool


@dataclass
class PlaywrightConfig:
    """Configuration for the PlaywrightCrawlerTool."""

    wait_until: str = "networkidle"
    use_bot_defense: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000


class PlaywrightError(Exception):
    """Exception raised for errors in the PlaywrightCrawlerTool."""

    pass


class PlaywrightCrawlerTool:
    """Tool for crawling JavaScript-rendered pages using Playwright."""

    def __init__(
        self,
        config: Optional[PlaywrightConfig] = None,
        bot_defense: Optional[BotDefenseTool] = None,
    ) -> None:
        """Initialize PlaywrightCrawlerTool.

        Args:
            config: Optional configuration for the crawler
            bot_defense: Optional bot defense tool
        """
        self.config = config or PlaywrightConfig()
        self.bot_defense = bot_defense if self.config.use_bot_defense else None
        self._page: Optional[Page] = None
        self._browser: Optional[Browser] = None

    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch a page using Playwright.

        Args:
            url: URL to fetch

        Returns:
            Dict containing page info (url, html)

        Raises:
            PlaywrightError: If page fetch fails
        """
        try:
            if not self._page:
                if self.bot_defense:
                    self._page = await self.bot_defense.get_new_page()
                else:
                    async with async_playwright() as playwright:
                        browser = await playwright.chromium.launch()
                        self._browser = browser
                        self._page = await browser.new_page()

            await self._page.goto(url)
            await self._page.wait_for_load_state(self.config.wait_until)

            if self.bot_defense:
                await self.bot_defense.handle_page(self._page, url)

            html = await self._page.content()
            return {"url": url, "html": html}
        except Exception as e:
            raise PlaywrightError(str(e)) from e

    async def cleanup(self):
        """Clean up resources."""
        if self._page:
            await self._page.close()
            self._page = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self.bot_defense:
            await self.bot_defense.cleanup()

    def run(self, url: str) -> Dict[str, Any]:
        """Run the crawler synchronously.

        Args:
            url: The URL to fetch content from.

        Returns:
            A dictionary containing the HTML content and URL.

        Raises:
            PlaywrightError: If there is an error during fetching.
        """
        import asyncio

        try:
            return asyncio.run(self.fetch(url))
        except Exception as e:
            raise PlaywrightError(str(e)) from e
