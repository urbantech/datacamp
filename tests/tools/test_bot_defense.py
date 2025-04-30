"""Tests for BotDefenseTool."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from tools.bot_defense.tool import BotDefenseTool


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = Mock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.evaluate = AsyncMock()
    page.mouse = Mock()
    page.mouse.move = AsyncMock()
    page.mouse.click = AsyncMock()
    page.keyboard = Mock()
    page.keyboard.type = AsyncMock()
    page.keyboard.press = AsyncMock()
    return page


@pytest.fixture
def mock_browser():
    """Create a mock Playwright Browser."""
    browser = Mock()
    browser.new_page = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright():
    """Create a mock Playwright instance."""
    playwright = Mock()
    playwright.chromium = Mock()
    playwright.chromium.launch = AsyncMock()
    return playwright


@pytest.fixture
def mock_async_playwright():
    """Create a mock async_playwright function."""

    async def mock_start():
        return Mock()

    mock = Mock()
    mock.start = AsyncMock(return_value=mock)
    mock.chromium = Mock()
    mock.chromium.launch = AsyncMock()

    async def _async_playwright():
        return mock

    return _async_playwright


@pytest.fixture
def bot_defense():
    """Create a BotDefenseTool instance."""
    return BotDefenseTool()


@pytest.mark.asyncio
async def test_init_browser(bot_defense, mock_async_playwright):
    """Test browser initialization."""
    with patch(
        "playwright.async_api.async_playwright",
        return_value=mock_async_playwright(),
    ):
        await bot_defense.init_browser()
        assert bot_defense._browser is not None


@pytest.mark.asyncio
async def test_simulate_human_behavior(bot_defense, mock_page):
    """Test human behavior simulation."""
    await bot_defense.simulate_human_behavior(mock_page)

    # Check mouse movements
    mock_page.mouse.move.assert_awaited()
    mock_page.mouse.click.assert_awaited()

    # Check keyboard interactions
    mock_page.keyboard.type.assert_awaited()
    mock_page.keyboard.press.assert_awaited()


@pytest.mark.asyncio
async def test_bypass_detection(bot_defense, mock_page):
    """Test bot detection bypass."""
    await bot_defense.bypass_detection(mock_page)

    # Check that page evaluation was called
    mock_page.evaluate.assert_awaited()


@pytest.mark.asyncio
async def test_handle_page(bot_defense, mock_page):
    """Test page handling."""
    url = "https://example.com"
    await bot_defense.handle_page(mock_page, url)

    # Check page navigation
    mock_page.goto.assert_awaited_once_with(url)
    mock_page.wait_for_load_state.assert_awaited()


@pytest.mark.asyncio
async def test_cleanup(bot_defense):
    """Test cleanup."""
    bot_defense._browser = Mock()
    bot_defense._browser.close = AsyncMock()

    await bot_defense.cleanup()
    bot_defense._browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_no_browser(bot_defense):
    """Test cleanup with no browser."""
    bot_defense._browser = None
    await bot_defense.cleanup()  # Should not raise any errors


@pytest.mark.asyncio
async def test_get_new_page(bot_defense, mock_browser):
    """Test getting a new page."""
    bot_defense._browser = mock_browser
    await bot_defense.get_new_page()
    mock_browser.new_page.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_new_page_no_browser(bot_defense, mock_async_playwright):
    """Test getting a new page when browser is not initialized."""
    with patch(
        "playwright.async_api.async_playwright",
        return_value=mock_async_playwright(),
    ):
        await bot_defense.get_new_page()
        assert bot_defense._browser is not None
