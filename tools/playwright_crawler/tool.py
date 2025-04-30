"""PlaywrightCrawlerTool for fetching HTML content from JS-rendered pages."""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright

from tools.bot_defense import BotDefenseTool


class PlaywrightError(Exception):
    """Custom exception for Playwright-related errors."""

    pass


@dataclass
class PlaywrightCrawlerConfig:
    """Configuration for PlaywrightCrawlerTool.

    Attributes:
        headless: Whether to run the browser in headless mode.
        user_agent: Custom user agent string.
        viewport_width: Width of the viewport.
        viewport_height: Height of the viewport.
        timeout: Timeout in milliseconds.
        wait_until: Wait until condition for page loading.
        use_bot_defense: Whether to use bot defense.
    """

    headless: bool = True
    user_agent: Optional[str] = None
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000  # milliseconds
    wait_until: str = "networkidle"
    use_bot_defense: bool = False


class PlaywrightCrawlerTool:
    """Tool for fetching content from JavaScript-rendered pages.

    Attributes:
        config: Configuration for the crawler.
        _browser: Browser instance.
        _playwright: Playwright instance.
        bot_defense: Bot defense instance.
    """

    def __init__(self, config: Optional[PlaywrightCrawlerConfig] = None):
        """Initialize the PlaywrightCrawlerTool.

        Args:
            config: Optional configuration for the crawler.
        """
        self.config = config or PlaywrightCrawlerConfig()
        self._browser = None
        self._playwright = None
        self.bot_defense = (
            BotDefenseTool() if self.config.use_bot_defense else None
        )

    async def _get_browser(self):
        """Get or create a browser instance.

        Returns:
            A browser instance.

        Raises:
            PlaywrightError: If browser creation fails.
        """
        if not self._browser:
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=self.config.headless
                )
            except Exception as e:
                raise PlaywrightError(f"Failed to create browser: {str(e)}")
        return self._browser

    async def _get_page(self):
        """Get a new page instance.

        Returns:
            A page instance.

        Raises:
            PlaywrightError: If page creation fails.
        """
        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            user_agent=self.config.user_agent,
        )

        try:
            if self.bot_defense:
                headers = self.bot_defense.run()["headers"]
                await context.set_extra_http_headers(headers)

            return await context.new_page()
        except Exception as e:
            await context.close()
            raise PlaywrightError(f"Failed to create page: {str(e)}")

    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL using Playwright.

        Args:
            url: The URL to fetch content from.

        Returns:
            A dictionary containing:
                - content: The HTML content of the page
                - title: The page title
                - url: The final URL after any redirects
                - status: The HTTP status code
                - headers: Response headers

        Raises:
            PlaywrightError: If the fetch operation fails.
        """
        page = await self._get_page()

        try:
            response = await page.goto(
                url,
                wait_until=self.config.wait_until,
                timeout=self.config.timeout,
            )

            if not response:
                raise PlaywrightError("Failed to get response from page.goto()")

            if not response.ok:
                raise PlaywrightError(
                    f"HTTP {response.status}: {response.status_text} for {url}"
                )

            content = await page.content()
            title = await page.title()

            result = {
                "content": content,
                "title": title,
                "url": response.url,
                "status": response.status,
                "headers": dict(response.headers),
            }

            await page.close()
            return result

        except PlaywrightError:
            raise
        except Exception as e:
            raise PlaywrightError(f"Failed to load page: {str(e)}")
        finally:
            await page.close()

    async def cleanup(self):
        """Clean up resources by closing the browser and playwright instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def run(self, url: str) -> Dict[str, Any]:
        """Run the crawler on a URL.

        Args:
            url: The URL to fetch content from.

        Returns:
            A dictionary containing the page content and metadata.
        """
        try:
            return asyncio.run(self.fetch(url))
        finally:
            asyncio.run(self.cleanup())
