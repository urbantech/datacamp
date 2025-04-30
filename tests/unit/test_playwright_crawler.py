"""Unit tests for the PlaywrightCrawlerTool."""

from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Browser, Page, Response

from tools.bot_defense.tool import BotDefenseTool
from tools.playwright_crawler.config import PlaywrightConfig
from tools.playwright_crawler.tool import PlaywrightCrawlerTool


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = AsyncMock(spec=Page)
    page.url = "https://example.com"
    page.content.return_value = "<html><body>Test content</body></html>"
    return page


@pytest.fixture
def mock_browser():
    """Create a mock Playwright browser."""
    browser = AsyncMock(spec=Browser)
    return browser


@pytest.fixture
def mock_response():
    """Create a mock Playwright response."""
    response = AsyncMock(spec=Response)
    response.ok = True
    response.status = 200
    response.headers = {"content-type": "text/html"}
    response.text.return_value = "<html><body>Test content</body></html>"
    return response


@pytest.fixture
def mock_bot_defense():
    """Create a mock BotDefenseTool."""
    bot_defense = AsyncMock(spec=BotDefenseTool)
    return bot_defense


@pytest.fixture
def crawler(mock_browser, mock_bot_defense):
    """Create a PlaywrightCrawlerTool instance with mocks."""
    config = PlaywrightConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=720,
        user_agent="Mozilla/5.0",
        timeout=30000,
    )
    return PlaywrightCrawlerTool(
        browser=mock_browser,
        bot_defense=mock_bot_defense,
        config=config,
    )


@pytest.mark.asyncio
async def test_fetch_success(crawler, mock_page, mock_response):
    """Test successful page fetch."""
    mock_page.goto.return_value = mock_response
    crawler._browser.new_page.return_value = mock_page

    result = await crawler.fetch("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["content"] == "<html><body>Test content</body></html>"
    assert result["status"] == 200
    assert result["headers"] == {"content-type": "text/html"}
    assert result["error"] is None


@pytest.mark.asyncio
async def test_fetch_failure_no_response(crawler, mock_page):
    """Test fetch failure when no response is received."""
    mock_page.goto.return_value = None
    crawler._browser.new_page.return_value = mock_page

    result = await crawler.fetch("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["content"] is None
    assert result["status"] is None
    assert result["headers"] == {}
    assert result["error"] == "Failed to get response"


@pytest.mark.asyncio
async def test_fetch_failure_not_ok(crawler, mock_page, mock_response):
    """Test fetch failure when response is not OK."""
    mock_response.ok = False
    mock_response.status = 404
    mock_page.goto.return_value = mock_response
    crawler._browser.new_page.return_value = mock_page

    result = await crawler.fetch("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["content"] is None
    assert result["status"] == 404
    assert result["headers"] == {"content-type": "text/html"}
    assert result["error"] == "Response not OK: 404"


@pytest.mark.asyncio
async def test_fetch_with_bot_defense(crawler, mock_page, mock_response):
    """Test fetch with bot defense enabled."""
    mock_page.goto.return_value = mock_response
    crawler._browser.new_page.return_value = mock_page

    result = await crawler.fetch("https://example.com")

    crawler._bot_defense.handle_page.assert_called_once_with(
        mock_page, "https://example.com"
    )
    assert result["url"] == "https://example.com"
    assert result["content"] == "<html><body>Test content</body></html>"


@pytest.mark.asyncio
async def test_cleanup(crawler):
    """Test cleanup method."""
    await crawler.cleanup()
    crawler._browser.close.assert_called_once()
