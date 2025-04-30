"""PlaywrightCrawlerTool for fetching content from websites using Playwright."""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from tools.bot_defense import BotDefenseTool


@dataclass
class PlaywrightCrawlerConfig:
    """Configuration for PlaywrightCrawlerTool."""

    timeout: int = 30000
    wait_until: str = "networkidle"
    viewport_width: int = 1280
    viewport_height: int = 720
    use_bot_defense: bool = True


class PlaywrightCrawlerTool:
    """Tool for fetching content from websites using Playwright."""

    def __init__(self, config: Optional[PlaywrightCrawlerConfig] = None):
        """Initialize PlaywrightCrawlerTool."""
        self.config = config or PlaywrightCrawlerConfig()
        self._browser: Optional[Browser] = None
        self.bot_defense = (
            BotDefenseTool() if self.config.use_bot_defense else None
        )

    async def _get_browser(self) -> Browser:
        """Get or create a browser instance."""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch()
        return self._browser

    async def _get_page(self) -> Page:
        """Get a new page instance."""
        browser = await self._get_browser()
        context: BrowserContext = await browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            }
        )

        if self.bot_defense:
            headers = self.bot_defense.run()["headers"]
            await context.set_extra_http_headers(headers)

        return await context.new_page()

    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            Dictionary containing:
            - content: HTML content of the page
            - status: HTTP status code
            - headers: Response headers
            - url: Final URL after redirects

        Raises:
            Exception: If page load fails or response is not OK
        """
        page = await self._get_page()
        try:
            # Navigate to URL and wait for network idle
            response = await page.goto(
                url,
                wait_until=self.config.wait_until,
                timeout=self.config.timeout,
            )

            if not response:
                raise Exception("No response received from page")

            if not response.ok:
                raise Exception(f"Response not OK. Status: {response.status}")

            # Get page content
            content = await page.content()
            title = await page.title()

            result: Dict[str, Any] = {
                "url": url,
                "status": response.status,
                "content": content,
                "title": title,
                "headers": dict(response.headers),
            }

            return result

        finally:
            await page.close()

    async def cleanup(self):
        """Clean up resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    def run(self, url: str) -> Dict[str, Any]:
        """Run the crawler on a URL."""
        try:
            result = asyncio.run(self.fetch(url))
            return result
        finally:
            asyncio.run(self.cleanup())
