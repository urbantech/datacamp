"""PlaywrightCrawlerTool for fetching HTML content from JavaScript-rendered pages."""

import asyncio
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright, Browser, Page

from ..interfaces import ToolInterface
from ..bot_defense.tool import BotDefenseTool


class PlaywrightCrawlerConfig(BaseModel):
    """Configuration for PlaywrightCrawlerTool."""
    
    timeout: int = Field(
        default=30000,
        description="Maximum time to wait for page load in milliseconds"
    )
    wait_until: str = Field(
        default="networkidle",
        description="When to consider navigation successful",
    )
    viewport_width: int = Field(
        default=1920,
        description="Browser viewport width"
    )
    viewport_height: int = Field(
        default=1080,
        description="Browser viewport height"
    )
    use_bot_defense: bool = Field(
        default=True,
        description="Whether to use BotDefenseTool for anti-detection"
    )


class PlaywrightCrawlerInput(BaseModel):
    """Input model for PlaywrightCrawlerTool."""
    url: str = Field(description="URL to fetch content from")


class PlaywrightCrawlerOutput(BaseModel):
    """Output model for PlaywrightCrawlerTool."""
    url: str = Field(description="URL that was fetched")
    status: int = Field(description="HTTP status code")
    content: str = Field(description="HTML content of the page")
    title: str = Field(description="Page title")
    headers: Dict[str, str] = Field(description="Response headers")


class PlaywrightCrawlerTool(ToolInterface):
    """Tool for fetching HTML content from JavaScript-rendered pages using Playwright."""

    name = "PlaywrightCrawlerTool"
    description = "Fetches HTML content from JavaScript-rendered pages using Playwright"
    
    @property
    def input_types(self) -> Dict[str, Type[BaseModel]]:
        """Get input types for the tool."""
        return {"input": PlaywrightCrawlerInput}
    
    @property
    def output_type(self) -> Type[BaseModel]:
        """Get output type for the tool."""
        return PlaywrightCrawlerOutput
    
    def __init__(self, config: Optional[PlaywrightCrawlerConfig] = None):
        """Initialize the PlaywrightCrawlerTool.
        
        Args:
            config: Optional configuration for the crawler
        """
        self.config = config or PlaywrightCrawlerConfig()
        self.bot_defense = BotDefenseTool() if self.config.use_bot_defense else None
        self._browser: Optional[Browser] = None
        self._context = None
    
    async def _get_browser(self) -> Browser:
        """Get or create a browser instance."""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch()
        return self._browser
    
    async def _get_page(self) -> Page:
        """Create and configure a new page."""
        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
        )
        
        if self.bot_defense:
            headers = self.bot_defense.run()["headers"]
            await context.set_extra_http_headers(headers)
        
        return await context.new_page()
    
    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL using Playwright.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            Dict containing HTML content and metadata
        """
        page = await self._get_page()
        
        try:
            response = await page.goto(
                url,
                timeout=self.config.timeout,
                wait_until=self.config.wait_until
            )
            
            if not response:
                raise Exception(f"Failed to load {url}")
            
            if not response.ok:
                raise Exception(
                    f"HTTP {response.status}: {response.status_text} for {url}"
                )
            
            content = await page.content()
            title = await page.title()
            
            return {
                "url": url,
                "status": response.status,
                "content": content,
                "title": title,
                "headers": dict(response.headers)
            }
            
        finally:
            await page.close()
    
    async def cleanup(self):
        """Clean up resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
    
    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the crawler on a URL.
        
        Args:
            url: The URL to crawl
            
        Returns:
            Dict containing the crawled content and metadata
        """
        input_model = PlaywrightCrawlerInput(**kwargs)
        
        try:
            result = asyncio.run(self.fetch(input_model.url))
            return PlaywrightCrawlerOutput(**result).model_dump()
        finally:
            asyncio.run(self.cleanup())
