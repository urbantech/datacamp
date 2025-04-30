"""BotDefenseTool for simulating human behavior."""

import asyncio
import random
from typing import Optional

from playwright.async_api import Browser, Page, async_playwright


class BotDefenseTool:
    """Tool for simulating human behavior to avoid bot detection."""

    def __init__(self):
        """Initialize BotDefenseTool."""
        self._browser: Optional[Browser] = None

    async def init_browser(self) -> None:
        """Initialize browser if not already initialized."""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)

    async def get_new_page(self) -> Page:
        """Get a new browser page.

        Returns:
            Page: A new Playwright page

        Raises:
            RuntimeError: If browser initialization fails
        """
        if not self._browser:
            await self.init_browser()
        if not self._browser:
            raise RuntimeError("Failed to initialize browser")
        return await self._browser.new_page()

    async def simulate_human_behavior(self, page: Page, url: str) -> None:
        """Simulate human behavior on a page.

        Args:
            page: Playwright page to interact with
            url: URL of the page
        """
        if not page:
            return

        try:
            # Random mouse movements
            for _ in range(random.randint(3, 7)):  # nosec B311
                x = random.randint(100, 800)  # nosec B311
                y = random.randint(100, 600)  # nosec B311
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.5))  # nosec B311

            # Scroll behavior
            await page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight * 0.3)"
            )
            await asyncio.sleep(random.uniform(0.5, 1.0))  # nosec B311

            # Random click
            await page.mouse.click(
                random.randint(100, 800),  # nosec B311
                random.randint(100, 600),  # nosec B311
            )
        except Exception as e:
            print(f"Error in simulate_human_behavior: {e}")

    async def bypass_detection(self, page: Page) -> None:
        """Bypass bot detection mechanisms.

        Args:
            page: Playwright page to interact with
        """
        # Set user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        await page.set_extra_http_headers({"User-Agent": user_agent})

        # Disable webdriver flag
        script = (
            "Object.defineProperty(navigator, 'webdriver', "
            "{get: () => undefined})"
        )
        await page.evaluate(script)

    async def handle_page(self, page: Page, url: str) -> None:
        """Handle a page with bot detection.

        Args:
            page: Playwright page to interact with
            url: URL of the page
        """
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await self.bypass_detection(page)
        await self.simulate_human_behavior(page, url)

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._browser:
            await self._browser.close()
