"""Tests for BotDefenseTool."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tools.bot_defense.tool import BotDefenseTool

# These imports are not used directly in the test file
# from playwright.async_api import Browser, Page


@pytest.fixture
def mock_page():
    """Mock page fixture."""
    page = AsyncMock()
    page.mouse = AsyncMock()
    page.mouse.move = AsyncMock()
    page.mouse.click = AsyncMock()
    page.evaluate = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.add_init_script = AsyncMock()
    page.scroll = AsyncMock()
    page.close = AsyncMock()
    # Add special __str__ method for test comparisons
    page.__str__ = MagicMock(return_value="<Page url='about:blank'>")
    return page


@pytest.fixture
def mock_browser():
    """Mock browser fixture."""
    browser = AsyncMock()
    browser.context = AsyncMock()
    browser.new_page = AsyncMock()
    browser.close = AsyncMock()
    # Ensure mock has attribute for reference tracking
    browser._playwright = None
    return browser


@pytest.fixture
def mock_async_playwright():
    """Mock for async_playwright."""
    # Create a properly configured playwright mock
    playwright_instance = AsyncMock()
    playwright_instance.chromium = AsyncMock()

    # Create a context manager mock that returns the playwright instance
    context_manager = AsyncMock()
    context_manager.__aenter__ = AsyncMock(return_value=playwright_instance)
    context_manager.__aexit__ = AsyncMock()

    # Create the function that returns the context manager
    mock_func = MagicMock(return_value=context_manager)
    return mock_func, playwright_instance


@pytest.fixture
def bot_defense():
    """Create a BotDefenseTool instance."""
    # Create a clean instance for each test
    tool = BotDefenseTool()
    # Reset the instance state to ensure clean test environment
    tool._browser = None
    tool._playwright = None
    yield tool
    # Clean up after each test
    asyncio.run(tool.cleanup())


@pytest.mark.asyncio
async def test_init_browser(bot_defense, mock_browser, mock_async_playwright):
    """Test browser initialization."""
    mock_func, playwright_instance = mock_async_playwright

    # Configure the mock to return our mock_browser
    playwright_instance.chromium.launch.return_value = mock_browser

    # Patch the async_playwright function
    with patch("tools.bot_defense.tool.async_playwright", mock_func):
        # Test init_browser
        await bot_defense.init_browser()

        # Verify browser was initialized correctly
        assert bot_defense._browser == mock_browser
        assert bot_defense._playwright == playwright_instance
        assert bot_defense._browser._playwright == bot_defense._playwright
        assert bot_defense._browser == mock_browser
        assert bot_defense._playwright == playwright_instance
        assert bot_defense._browser._playwright == bot_defense._playwright


@pytest.mark.asyncio
async def test_init_browser_failure(bot_defense, mock_async_playwright):
    """Test browser initialization failure."""
    mock_func, playwright_instance = mock_async_playwright

    # Configure launch to raise an exception when awaited
    playwright_instance.chromium.launch.side_effect = Exception(
        "Failed to launch"
    )

    # Patch the async_playwright function
    with patch("tools.bot_defense.tool.async_playwright", mock_func):
        # Verify RuntimeError is raised with the nested exception
        with pytest.raises(
            RuntimeError, match="Failed to initialize browser"
        ) as exc_info:
            await bot_defense.init_browser()

        # Verify state is properly reset
        assert bot_defense._browser is None
        assert bot_defense._playwright is None

        # Verify the original exception is preserved
        assert isinstance(exc_info.value.__cause__, Exception)
        assert str(exc_info.value.__cause__) == "Failed to launch"


@pytest.mark.asyncio
async def test_init_browser_launch_failure(bot_defense):
    """Test browser launch failure during initialization."""
    # Create context manager that raises error on enter
    context_manager = AsyncMock()
    context_manager.__aenter__ = AsyncMock(
        side_effect=Exception("Context manager error")
    )
    context_manager.__aexit__ = AsyncMock()

    # Create a function that returns the context manager
    mock_func = MagicMock(return_value=context_manager)

    # Patch the async_playwright function
    with patch("tools.bot_defense.tool.async_playwright", mock_func):
        # Verify RuntimeError is raised
        with pytest.raises(RuntimeError, match="Failed to initialize browser"):
            await bot_defense.init_browser()

        # Verify state is properly reset
        assert bot_defense._browser is None


@pytest.mark.asyncio
async def test_simulate_human_behavior(bot_defense, mock_page):
    """Test human behavior simulation."""
    # Create mock page methods
    mock_page.mouse = AsyncMock()
    mock_page.mouse.move = AsyncMock()
    mock_page.mouse.click = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.scroll = AsyncMock()

    # Test with valid URL
    await bot_defense.simulate_human_behavior(mock_page, "https://example.com")

    # Verify mouse movements were called
    mock_page.mouse.move.assert_awaited()
    mock_page.mouse.click.assert_awaited_once()
    mock_page.evaluate.assert_awaited()

    # Test with None page
    await bot_defense.simulate_human_behavior(
        None, "https://example.com"
    )  # Should not raise

    # Test with exception during simulation
    mock_page.mouse.move.side_effect = Exception("Test error")
    await bot_defense.simulate_human_behavior(
        mock_page, "https://example.com"
    )  # Should not raise


@pytest.mark.asyncio
async def test_simulate_human_behavior_scroll_error(bot_defense, mock_page):
    """Test human behavior simulation with scroll error."""
    # Create mock page with scroll error
    mock_page.mouse = AsyncMock()
    mock_page.mouse.move = AsyncMock()
    mock_page.mouse.click = AsyncMock()
    mock_page.evaluate = AsyncMock(side_effect=Exception("Scroll error"))

    # Test with error
    await bot_defense.simulate_human_behavior(mock_page, "https://example.com")

    # Verify mouse movements were still called
    assert mock_page.mouse.move.await_count >= 1
    mock_page.mouse.click.assert_awaited_once()
    mock_page.evaluate.assert_awaited()

    # Test with None page
    await bot_defense.simulate_human_behavior(
        None, "https://example.com"
    )  # Should not raise


@pytest.mark.asyncio
async def test_bypass_detection(bot_defense, mock_page):
    """Test bypass detection."""
    # Create mock page
    mock_page.set_extra_http_headers = AsyncMock()
    mock_page.evaluate = AsyncMock()

    # Test bypass detection
    await bot_defense.bypass_detection(mock_page)

    # Verify methods were called
    assert mock_page.set_extra_http_headers.await_count == 1
    assert mock_page.evaluate.await_count == 1


@pytest.mark.asyncio
async def test_bypass_detection_headers_error(bot_defense, mock_page):
    """Test bypass detection with headers error."""
    # Create mock page with headers error
    mock_page.set_extra_http_headers = AsyncMock(
        side_effect=Exception("Headers error")
    )
    mock_page.evaluate = AsyncMock()

    # Test bypass detection with error
    await bot_defense.bypass_detection(mock_page)

    # Verify evaluate was still called
    assert mock_page.evaluate.await_count == 1


@pytest.mark.asyncio
async def test_bypass_detection_evaluate_error(bot_defense, mock_page):
    """Test bypass detection with evaluate error."""
    # Create mock page with evaluate error
    mock_page.set_extra_http_headers = AsyncMock()
    mock_page.evaluate = AsyncMock(side_effect=Exception("Evaluate error"))

    # Test bypass detection with error
    await bot_defense.bypass_detection(mock_page)

    # Verify headers were still set
    assert mock_page.set_extra_http_headers.await_count == 1


@pytest.mark.asyncio
async def test_handle_page(bot_defense, mock_page):
    """Test handle page."""
    # Create mock page
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()

    # Create mock methods
    bot_defense.bypass_detection = AsyncMock()
    bot_defense.simulate_human_behavior = AsyncMock()

    # Test handle page
    await bot_defense.handle_page(mock_page, "https://example.com")

    # Verify methods were called
    assert mock_page.goto.await_count == 1
    assert mock_page.wait_for_load_state.await_count == 1
    assert bot_defense.bypass_detection.await_count == 1
    assert bot_defense.simulate_human_behavior.await_count == 1


@pytest.mark.asyncio
async def test_handle_page_navigation_error(bot_defense, mock_page):
    """Test page handling with navigation error."""
    # Set up necessary attributes
    bot_defense._browser = AsyncMock()
    bot_defense._playwright = AsyncMock()

    # Configure the mock page to raise exception on goto
    mock_page.goto = AsyncMock(side_effect=Exception("Navigation error"))

    # Make sure wait_for_load_state doesn't also raise an exception
    mock_page.wait_for_load_state = AsyncMock()

    # Configure bypass_detection and simulate_human_behavior mocks
    bot_defense.bypass_detection = AsyncMock()
    bot_defense.simulate_human_behavior = AsyncMock()

    # Call handle_page with the mock page
    await bot_defense.handle_page(mock_page, "https://example.com")

    # Verify that bypass_detection and simulate_human_behavior were still called
    assert bot_defense.bypass_detection.call_count == 1
    assert bot_defense.simulate_human_behavior.call_count == 1


@pytest.mark.asyncio
async def test_get_new_page(
    bot_defense, mock_browser, mock_page, mock_async_playwright
):
    """Test getting a new page."""
    # Set up necessary attributes
    bot_defense._browser = mock_browser
    bot_defense._playwright = AsyncMock()

    # Configure browser to return mock page
    mock_browser.new_page = AsyncMock(return_value=mock_page)

    # Call get_new_page
    result = await bot_defense.get_new_page()

    # Verify the page was obtained correctly
    assert result == mock_page
    assert mock_browser.new_page.call_count == 1


@pytest.mark.asyncio
async def test_cleanup(bot_defense, mock_browser, mock_async_playwright):
    """Test cleanup."""
    # Create and set up mock state directly
    playwright_mock = AsyncMock()

    # Set up the browser state manually
    bot_defense._browser = mock_browser
    bot_defense._playwright = playwright_mock
    # Store reference for cleanup
    bot_defense._browser._playwright = playwright_mock

    await bot_defense.cleanup()
    assert mock_browser.close.call_count == 1
    assert bot_defense._browser is None
    assert bot_defense._playwright is None


@pytest.mark.asyncio
async def test_cleanup_no_browser(bot_defense):
    """Test cleanup with no browser."""
    # Set up the browser state manually
    bot_defense._browser = None
    bot_defense._playwright = None

    await bot_defense.cleanup()

    # Verify that cleanup works without browser
    assert bot_defense._browser is None
    assert bot_defense._playwright is None


@pytest.mark.asyncio
async def test_cleanup_with_error(bot_defense, mock_browser):
    """Test cleanup with error."""
    # Set up the test state manually
    mock_playwright = AsyncMock()
    bot_defense._browser = mock_browser
    bot_defense._playwright = mock_playwright
    # Store reference for cleanup
    bot_defense._browser._playwright = mock_playwright

    # Set error condition
    mock_browser.close.side_effect = Exception("Cleanup error")

    # This should succeed despite the error
    await bot_defense.cleanup()

    # Verify state is cleaned up despite error
    assert bot_defense._browser is None
    assert bot_defense._playwright is None


@pytest.mark.asyncio
async def test_get_new_page_no_browser(
    bot_defense, mock_page, mock_async_playwright
):
    """Test getting a new page without browser initialization."""
    mock_func, playwright_instance = mock_async_playwright

    # Mock browser returned by launch
    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    playwright_instance.chromium.launch.return_value = mock_browser

    # Ensure bot defense has no browser or playwright
    bot_defense._browser = None
    bot_defense._playwright = None

    # Patch the playwright import
    with patch("tools.bot_defense.tool.async_playwright", mock_func):
        # Call the method
        result = await bot_defense.get_new_page()

        # Verify the page was obtained correctly
        assert bot_defense._browser == mock_browser
        assert bot_defense._playwright == playwright_instance
        assert bot_defense._browser._playwright == bot_defense._playwright
        assert result == mock_page


@pytest.mark.asyncio
async def test_get_new_page_with_init(bot_defense):
    """Test getting a new page with browser initialization."""
    # Create all mocks directly
    mock_page = AsyncMock()
    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)

    # Initialize bot defense with a browser mock already set
    bot_defense._browser = mock_browser

    # Call the method - should use existing browser without initialization
    page = await bot_defense.get_new_page()

    # Verify
    assert page == mock_page
    assert mock_browser.new_page.call_count == 1
