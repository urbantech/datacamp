"""BotDefenseTool for simulating human behavior."""

import asyncio
import logging
import random
from typing import Optional

from playwright.async_api import Browser, Page, async_playwright

# Configure logging
logger = logging.getLogger(__name__)


class BotDefenseTool:
    """Tool for simulating human behavior to avoid bot detection."""

    def __init__(self):
        """Initialize BotDefenseTool."""
        self._browser: Optional[Browser] = None

    async def init_browser(self) -> None:
        """Initialize the browser if not already initialized."""
        if not self._browser:
            try:
                self._playwright = await async_playwright().__aenter__()
                self._browser = await self._playwright.chromium.launch()
                self._browser._playwright = (
                    self._playwright
                )  # Store reference for cleanup
            except Exception as e:
                if self._browser:
                    try:
                        await self._browser.close()
                    except Exception as close_error:
                        logger.warning(f"Error closing browser: {close_error}")
                if self._playwright:
                    try:
                        await self._playwright.__aexit__(None, None, None)
                    except Exception as exit_error:
                        logger.warning(
                            f"Error exiting playwright: {exit_error}"
                        )
                self._browser = None
                self._playwright = None
                raise RuntimeError("Failed to initialize browser") from e

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
                try:
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.5))  # nosec B311
                except Exception as movement_error:
                    # Continue with other movements if one fails
                    logger.debug(f"Mouse movement failed: {movement_error}")
                    continue

            # Scroll behavior
            try:
                await page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight * 0.3)"
                )
                await asyncio.sleep(random.uniform(0.5, 1.0))  # nosec B311
            except Exception as scroll_error:
                # Continue if scroll fails
                logger.debug(f"Scroll failed: {scroll_error}")

            # Random click
            try:
                await page.mouse.click(
                    random.randint(100, 800),  # nosec B311
                    random.randint(100, 600),  # nosec B311
                )
            except Exception as click_error:
                # Continue if click fails
                logger.debug(f"Click failed: {click_error}")
        except Exception as e:
            print(f"Error in simulate_human_behavior: {e}")

    async def bypass_detection(self, page: Page) -> None:
        """Bypass bot detection mechanisms.

        Args:
            page: Playwright page to interact with
        """
        try:
            # Set user agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            await page.set_extra_http_headers({"User-Agent": user_agent})
        except Exception as headers_error:
            # Continue if setting headers fails
            logger.debug(f"Setting headers failed: {headers_error}")

        try:
            # Disable webdriver flag
            script = (
                "Object.defineProperty(navigator, 'webdriver', "
                "{get: () => undefined})"
            )
            await page.evaluate(script)
        except Exception as script_error:
            # Continue if script evaluation fails
            logger.debug(f"Script evaluation failed: {script_error}")

    async def handle_page(self, page: Page, url: str) -> None:
        """Handle a page with bot detection.

        Args:
            page: Playwright page to interact with
            url: URL of the page
        """
        try:
            await page.goto(url)
        except Exception as nav_error:
            # Continue if navigation fails
            logger.debug(f"Navigation failed: {nav_error}")

        try:
            await page.wait_for_load_state("networkidle")
        except Exception as wait_error:
            # Continue if waiting fails
            logger.debug(f"Wait for load state failed: {wait_error}")

        await self.bypass_detection(page)
        await self.simulate_human_behavior(page, url)

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._browser:
            try:
                await self._browser.close()
                if hasattr(self._browser, "_playwright"):
                    await self._browser._playwright.__aexit__(None, None, None)
            except Exception as cleanup_error:
                # Log cleanup errors
                logger.warning(f"Cleanup error: {cleanup_error}")
            self._browser = None
            self._playwright = None
