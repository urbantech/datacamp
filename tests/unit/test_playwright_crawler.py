"""Unit tests for PlaywrightCrawlerTool."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from playwright.async_api import Page, Response, Browser, BrowserContext

from tools.playwright_crawler import PlaywrightCrawlerTool, PlaywrightCrawlerConfig


@pytest.fixture
def mock_response():
    """Create a mock Playwright Response."""
    response = AsyncMock(spec=Response)
    response.ok = True
    response.status = 200
    response.status_text = "OK"
    response.headers = {"Content-Type": "text/html"}
    return response


@pytest.fixture
def mock_page(mock_response):
    """Create a mock Playwright Page."""
    page = AsyncMock(spec=Page)
    page.goto = AsyncMock(return_value=mock_response)
    page.content = AsyncMock(return_value="<html><body>Test content</body></html>")
    page.title = AsyncMock(return_value="Test Page")
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_context(mock_page):
    """Create a mock Playwright BrowserContext."""
    context = AsyncMock(spec=BrowserContext)
    context.new_page = AsyncMock(return_value=mock_page)
    context.set_extra_http_headers = AsyncMock()
    return context


@pytest.fixture
def mock_browser(mock_context):
    """Create a mock Playwright Browser."""
    browser = AsyncMock(spec=Browser)
    browser.new_context = AsyncMock(return_value=mock_context)
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_chromium(mock_browser):
    """Create a mock Playwright Chromium instance."""
    chromium = AsyncMock()
    chromium.launch = AsyncMock(return_value=mock_browser)
    return chromium


@pytest.fixture
def mock_playwright_instance(mock_chromium):
    """Create a mock Playwright instance."""
    playwright = AsyncMock()
    playwright.chromium = mock_chromium
    return playwright


@pytest.fixture
def mock_playwright_factory(mock_playwright_instance):
    """Create a mock Playwright factory."""
    factory = AsyncMock()
    factory.start = AsyncMock(return_value=mock_playwright_instance)
    return factory


def test_playwright_crawler_initialization():
    """Test PlaywrightCrawlerTool initialization."""
    crawler = PlaywrightCrawlerTool()
    assert crawler.name == "PlaywrightCrawlerTool"
    assert crawler.config.timeout == 30000
    assert crawler.config.wait_until == "networkidle"
    assert crawler.config.viewport_width == 1920
    assert crawler.config.viewport_height == 1080
    assert crawler.config.use_bot_defense is True


def test_playwright_crawler_custom_config():
    """Test PlaywrightCrawlerTool with custom configuration."""
    config = PlaywrightCrawlerConfig(
        timeout=60000,
        wait_until="load",
        viewport_width=1280,
        viewport_height=720,
        use_bot_defense=False
    )
    crawler = PlaywrightCrawlerTool(config)
    
    assert crawler.config.timeout == 60000
    assert crawler.config.wait_until == "load"
    assert crawler.config.viewport_width == 1280
    assert crawler.config.viewport_height == 720
    assert crawler.config.use_bot_defense is False
    assert crawler.bot_defense is None


@pytest.mark.asyncio
async def test_playwright_crawler_fetch(mock_playwright_factory, mock_page, mock_context, mock_browser):
    """Test PlaywrightCrawlerTool fetch method."""
    with patch("playwright.async_api.async_playwright", return_value=mock_playwright_factory):
        crawler = PlaywrightCrawlerTool()
        
        # Mock the browser instance
        crawler._browser = mock_browser
        
        result = await crawler.fetch("https://example.com")
        
        # Verify the page configuration
        mock_browser.new_context.assert_called_once_with(
            viewport={
                "width": 1920,
                "height": 1080
            }
        )
        mock_context.new_page.assert_called_once()
        
        # Verify the page interactions
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            timeout=30000,
            wait_until="networkidle"
        )
        mock_page.content.assert_called_once()
        mock_page.title.assert_called_once()
        mock_page.close.assert_called_once()
        
        # Verify the result
        assert result["url"] == "https://example.com"
        assert result["status"] == 200
        assert result["content"] == "<html><body>Test content</body></html>"
        assert result["title"] == "Test Page"
        assert result["headers"] == {"Content-Type": "text/html"}


def test_playwright_crawler_run():
    """Test PlaywrightCrawlerTool run method."""
    crawler = PlaywrightCrawlerTool()
    
    with patch.object(crawler, "fetch") as mock_fetch:
        mock_fetch.return_value = {
            "url": "https://example.com",
            "status": 200,
            "content": "<html><body>Test content</body></html>",
            "title": "Test Page",
            "headers": {"Content-Type": "text/html"}
        }
        
        result = crawler.run(url="https://example.com")
        
        assert result["url"] == "https://example.com"
        assert result["status"] == 200
        assert result["content"] == "<html><body>Test content</body></html>"
        assert result["title"] == "Test Page"
        assert result["headers"] == {"Content-Type": "text/html"}


def test_playwright_crawler_run_missing_url():
    """Test PlaywrightCrawlerTool run method with missing URL."""
    crawler = PlaywrightCrawlerTool()
    
    with pytest.raises(ValueError) as exc_info:
        crawler.run()
    
    assert "1 validation error for PlaywrightCrawlerInput" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_playwright_crawler_cleanup(mock_browser):
    """Test PlaywrightCrawlerTool cleanup method."""
    crawler = PlaywrightCrawlerTool()
    crawler._browser = mock_browser
    
    await crawler.cleanup()
    
    mock_browser.close.assert_called_once()
    assert crawler._browser is None
