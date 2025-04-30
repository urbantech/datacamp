"""Unit tests for the PlaywrightCrawlerTool."""

import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from tools.playwright_crawler import (
    PlaywrightConfig,
    PlaywrightCrawlerTool,
    PlaywrightError,
)


@pytest.fixture
def mock_page():
    """Mock Playwright page."""
    page = Mock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.content = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_bot_defense():
    """Mock BotDefenseTool."""
    bot_defense = Mock()
    bot_defense.simulate_human_behavior = AsyncMock()
    return bot_defense


@pytest.fixture
def crawler(mock_page, mock_bot_defense):
    """Create PlaywrightCrawlerTool instance."""
    config = PlaywrightConfig(use_bot_defense=True)
    crawler = PlaywrightCrawlerTool(config=config, bot_defense=mock_bot_defense)
    crawler._page = mock_page
    return crawler


@pytest.mark.asyncio
async def test_fetch_success(crawler):
    """Test successful page fetch."""
    url = "https://example.com"
    html = "<html><body>Test</body></html>"
    crawler._page.content = AsyncMock(return_value=html)
    crawler._page.url = url

    result = await crawler.fetch(url)

    assert result["html"] == html
    assert result["url"] == url
    crawler._page.goto.assert_awaited_once_with(url)
    crawler._page.wait_for_load_state.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_with_bot_defense(crawler):
    """Test page fetch with bot defense."""
    url = "https://example.com"
    crawler.config.use_bot_defense = True

    await crawler.fetch(url)

    crawler.bot_defense.simulate_human_behavior.assert_awaited_once_with(
        crawler._page, url
    )


@pytest.mark.asyncio
async def test_fetch_no_page(crawler, mock_bot_defense):
    """Test fetch when page is not initialized."""
    url = "https://example.com"
    mock_new_page = Mock()
    mock_new_page.goto = AsyncMock()
    mock_new_page.wait_for_load_state = AsyncMock()
    mock_new_page.content = AsyncMock(
        return_value="<html><body>Test</body></html>"
    )
    mock_new_page.url = url

    mock_bot_defense.get_new_page = AsyncMock(return_value=mock_new_page)
    result = await crawler.fetch(url)

    assert result["html"] == "<html><body>Test</body></html>"
    assert result["url"] == url
    mock_bot_defense.get_new_page.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_navigation_timeout(crawler):
    """Test fetch with navigation timeout."""
    url = "https://example.com"
    crawler._page.goto.side_effect = TimeoutError("Navigation timeout")

    with pytest.raises(Exception, match="Navigation timeout"):
        await crawler.fetch(url)


@pytest.mark.asyncio
async def test_fetch_page_crash(crawler):
    """Test fetch with page crash."""
    url = "https://example.com"
    crawler._page.goto.side_effect = Exception("Page crashed")

    with pytest.raises(Exception, match="Page crashed"):
        await crawler.fetch(url)


@pytest.mark.asyncio
async def test_cleanup(crawler):
    """Test cleanup."""
    crawler._page.close = AsyncMock()

    await crawler.cleanup()

    crawler._page.close.assert_awaited_once()
    crawler.bot_defense.cleanup.assert_awaited_once()


@pytest.mark.asyncio
async def test_cleanup_no_page(crawler):
    """Test cleanup with no page."""
    crawler._page = None
    await crawler.cleanup()  # Should not raise any errors
    crawler.bot_defense.cleanup.assert_awaited_once()


def test_run_success(crawler):
    """Test synchronous run method."""
    url = "https://example.com"
    mock_result = {"html": "<html></html>", "url": url}

    with patch("asyncio.run") as mock_run:
        mock_run.return_value = mock_result
        result = crawler.run(url)
        assert result == mock_result


def test_run_error(crawler):
    """Test synchronous run method with error."""
    url = "https://example.com"

    with patch("asyncio.run") as mock_run:
        mock_run.side_effect = Exception("Test error")
        with pytest.raises(Exception, match="Test error"):
            crawler.run(url)


# Fixture directory path
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "html")


def read_fixture(filename):
    """Read fixture file with error handling."""
    try:
        print("\n=== Reading Fixture ===")
        fixture_path = os.path.join(FIXTURE_DIR, filename)
        print("Fixture path: {}".format(fixture_path))
        print("Directory exists: {}".format(os.path.exists(FIXTURE_DIR)))
        print("File exists: {}".format(os.path.exists(fixture_path)))

        with open(fixture_path, "r", encoding="utf-8") as f:
            content = f.read()
            print("Successfully read fixture ({} chars)".format(len(content)))
            return content
    except Exception as e:
        print("Error reading fixture: {}".format(e))
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise


@pytest.fixture
def mock_response():
    """Create a mock response."""
    response = AsyncMock()
    response.ok = True
    response.status = 200
    response.status_text = "OK"
    response.headers = {"Content-Type": "text/html"}
    return response


@pytest.fixture
def mock_context():
    """Create a mock context."""
    context = AsyncMock()
    context.new_page = AsyncMock()
    context.set_extra_http_headers = AsyncMock()
    return context


@pytest.fixture
def mock_browser():
    """Create a mock browser."""
    browser = AsyncMock()
    browser.new_context = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_chromium():
    """Create a mock chromium instance."""
    chromium = AsyncMock()
    return chromium


@pytest.fixture
def mock_playwright_instance():
    """Create a mock playwright instance."""
    playwright = AsyncMock()
    playwright.chromium = AsyncMock()
    playwright.start = AsyncMock(return_value=playwright)
    return playwright


@pytest.mark.asyncio
async def test_fetch_failure_no_response(crawler):
    """Test fetch method when goto returns no response."""
    url = "http://example.com"
    crawler._page.goto = AsyncMock(
        side_effect=Exception("Failed to load http://example.com")
    )

    with pytest.raises(
        PlaywrightError, match="Failed to load http://example.com"
    ):
        await crawler.fetch(url)


@pytest.mark.asyncio
async def test_fetch_failure_not_ok(crawler):
    """Test fetch method when response is not OK."""
    url = "http://example.com"
    crawler._page.goto = AsyncMock(
        side_effect=Exception("HTTP 404: Not Found for http://example.com")
    )

    with pytest.raises(
        PlaywrightError, match="HTTP 404: Not Found for http://example.com"
    ):
        await crawler.fetch(url)


@pytest.mark.asyncio
async def test_fixture_crawler(crawler):
    """Test crawler with fixture content."""
    url = "http://example.com"
    fixture_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
</head>
<body>
    <h1>Welcome to the Test Page</h1>
    <p>This is a test page for the PlaywrightCrawlerTool.</p>
</body>
</html>"""

    crawler._page.content = AsyncMock(return_value=fixture_content)
    crawler._page.url = url

    result = await crawler.fetch(url)

    assert result["html"] == fixture_content
    assert result["url"] == url
    assert "Welcome to the Test Page" in result["html"]
    crawler._page.goto.assert_awaited_once_with(url)
    crawler._page.wait_for_load_state.assert_awaited_once()


def test_crawler_with_config():
    """Test crawler with custom configuration."""
    # Create custom config
    config = PlaywrightConfig(
        wait_until="load",
        use_bot_defense=False,
    )

    # Create crawler with config
    crawler = PlaywrightCrawlerTool(config=config)

    # Verify config was applied
    assert crawler.config.wait_until == "load"
    assert crawler.config.use_bot_defense is False


@pytest.mark.asyncio
async def test_crawler_error_handling(crawler):
    """Test crawler error handling."""
    url = "https://example.com"
    crawler._page.goto.side_effect = Exception("Failed to load page")

    with pytest.raises(PlaywrightError, match="Failed to load page"):
        await crawler.fetch(url)


def test_crawler_cleanup(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
):
    """Test crawler cleanup."""
    print("\n=== Starting Cleanup Test ===")

    try:
        # Configure mock page
        mock_page.close.return_value = None

        # Configure mock context
        mock_context.new_page.return_value = mock_page
        mock_context.set_extra_http_headers.return_value = None

        # Configure mock browser
        mock_browser.new_context.return_value = mock_context
        mock_browser.close.return_value = None

        # Configure mock chromium
        mock_chromium.launch.return_value = mock_browser

        # Configure mock playwright
        mock_playwright_instance.chromium = mock_chromium
        mock_playwright_instance.start.return_value = mock_playwright_instance

        print("Configured mocks")

        # Patch playwright
        with patch(
            "playwright.async_api.async_playwright",
            return_value=mock_playwright_instance,
        ):
            print("Patched playwright")

            # Create crawler
            crawler = PlaywrightCrawlerTool()
            print("Created crawler")

            # Set browser
            crawler._browser = mock_browser

            # Run cleanup
            asyncio.run(crawler.cleanup())

            # Verify browser was closed
            mock_browser.close.assert_called_once()
            assert crawler._browser is None

            print("Test completed successfully")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise
