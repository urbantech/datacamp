"""Unit tests for the PlaywrightCrawlerTool."""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest

from tools.playwright_crawler import (
    PlaywrightCrawlerConfig,
    PlaywrightCrawlerTool,
    PlaywrightError,
)

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
def mock_page():
    """Create a mock page."""
    page = AsyncMock()
    page.content = AsyncMock()
    page.title = AsyncMock()
    page.goto = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_context():
    """Create a mock context."""
    context = AsyncMock()
    context.new_page = AsyncMock()
    context.set_extra_http_headers = AsyncMock()
    context.close = AsyncMock()
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
async def test_get_browser(mock_chromium, mock_playwright_instance):
    """Test _get_browser method."""
    print("\n=== Starting Get Browser Test ===")

    try:
        # Configure mock chromium
        mock_browser = AsyncMock()

        # Create a function that returns a coroutine
        def mock_launch():
            async def _launch():
                return mock_browser

            return _launch()

        mock_chromium.launch = mock_launch

        # Configure mock playwright
        mock_playwright_instance.chromium = mock_chromium

        # Create a function that returns a coroutine
        def mock_start():
            async def _start():
                return mock_playwright_instance

            return _start()

        mock_playwright_instance.start = mock_start

        print("Configured mocks")

        # Create crawler
        crawler = PlaywrightCrawlerTool()
        print("Created crawler")

        # Create mock async_playwright function that returns a coroutine
        def mock_async_playwright():
            async def _async_playwright():
                return mock_playwright_instance

            return _async_playwright()

        # Patch playwright
        with patch(
            "playwright.async_api.async_playwright", mock_async_playwright
        ):
            print("Patched playwright")

            # Get browser
            browser = await crawler._get_browser()
            print("Got browser")

            # Verify browser was created
            assert crawler._browser == browser

            # Get browser again (should reuse existing)
            browser2 = await crawler._get_browser()
            assert browser2 == browser

            print("Test completed successfully")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise


@pytest.mark.asyncio
async def test_get_page(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
):
    """Test _get_page method."""
    # Configure mock page
    mock_page.goto = AsyncMock()
    mock_page.close = AsyncMock()

    # Configure mock context
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.set_extra_http_headers = AsyncMock()
    mock_context.close = AsyncMock()

    # Configure mock browser
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    # Configure mock chromium
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    # Create crawler with custom config
    config = PlaywrightCrawlerConfig(
        viewport_width=1024, viewport_height=768, user_agent=None
    )
    crawler = PlaywrightCrawlerTool(config)
    crawler._browser = mock_browser

    # Test _get_page
    page = await crawler._get_page()

    # Verify browser.new_context was called with correct arguments
    mock_browser.new_context.assert_called_once_with(
        viewport={"width": 1024, "height": 768}, user_agent=None
    )

    # Verify context.new_page was called
    mock_context.new_page.assert_called_once()

    # Verify we got the mock page back
    assert page == mock_page


@pytest.mark.asyncio
async def test_fetch_failure_no_response(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
):
    """Test fetch method when page.goto returns None."""
    print("\n=== Starting Fetch No Response Test ===")

    # Configure mock page
    mock_page.goto = AsyncMock(return_value=None)
    mock_page.close = AsyncMock()

    # Configure mock context
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    # Configure mock browser
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    # Configure mock chromium
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    # Create crawler instance
    crawler = PlaywrightCrawlerTool()
    crawler._browser = mock_browser

    # Test fetch with no response
    with pytest.raises(PlaywrightError) as exc_info:
        await crawler.fetch("https://example.com")

    assert str(exc_info.value) == "Failed to get response from page.goto()"


@pytest.mark.asyncio
async def test_fetch_failure_not_ok(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
):
    """Test fetch method when response is not OK."""
    print("\n=== Starting Fetch Not OK Test ===")

    # Configure mock response
    mock_response = AsyncMock()
    mock_response.ok = False
    mock_response.status = 404
    mock_response.status_text = "Not Found"

    # Configure mock page
    mock_page.goto = AsyncMock(return_value=mock_response)
    mock_page.close = AsyncMock()

    # Configure mock context
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    # Configure mock browser
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    # Configure mock chromium
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    # Create crawler instance
    crawler = PlaywrightCrawlerTool()
    crawler._browser = mock_browser

    # Test fetch with not OK response
    with pytest.raises(PlaywrightError) as exc_info:
        await crawler.fetch("https://example.com")

    assert str(exc_info.value) == "HTTP 404: Not Found for https://example.com"


def test_basic_crawler(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
    mock_response,
):
    """Basic test for crawler functionality."""
    print("\n=== Starting Basic Crawler Test ===")

    try:
        # Configure test data
        test_content = "<html><body>Test</body></html>"
        test_title = "Test Page"

        # Configure mock page
        mock_page.content.return_value = test_content
        mock_page.title.return_value = test_title
        mock_page.goto.return_value = mock_response
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

            # Mock fetch method to return test data
            async def mock_fetch(url):
                return {
                    "url": url,
                    "status": 200,
                    "content": test_content,
                    "title": test_title,
                    "headers": {"Content-Type": "text/html"},
                }

            crawler.fetch = mock_fetch

            # Run crawler
            result = crawler.run(url="http://example.com")
            print(f"Got result: {result}")

            # Basic assertions
            assert isinstance(result, dict), "Result should be a dictionary"
            assert result["content"] == test_content
            assert result["title"] == test_title
            assert result["status"] == 200

            print("Test completed successfully")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise


def test_fixture_crawler(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
    mock_response,
):
    """Test crawler with fixture content."""
    print("\n=== Starting Fixture Crawler Test ===")

    try:
        # Load fixture first to catch any file issues
        fixture_content = read_fixture("simple_page.html")
        print("Loaded fixture content")

        # Configure mock page
        mock_page.content.return_value = fixture_content
        mock_page.title.return_value = "Simple Test Page"
        mock_page.goto.return_value = mock_response
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

            # Mock fetch method to return fixture data
            async def mock_fetch(url):
                return {
                    "url": url,
                    "status": 200,
                    "content": fixture_content,
                    "title": "Simple Test Page",
                    "headers": {"Content-Type": "text/html"},
                }

            crawler.fetch = mock_fetch

            # Run crawler
            result = crawler.run(url="http://example.com")
            print(f"Got result: {result}")

            # Assertions
            assert result["content"] == fixture_content
            assert result["title"] == "Simple Test Page"
            assert "Welcome to the Test Page" in result["content"]

            print("Test completed successfully")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise


def test_crawler_with_config():
    """Test crawler with custom configuration."""
    print("\n=== Starting Config Test ===")

    # Create custom config
    config = PlaywrightCrawlerConfig(
        timeout=60000,
        wait_until="load",
        viewport_width=1024,
        viewport_height=768,
        use_bot_defense=False,
    )

    # Create crawler with config
    crawler = PlaywrightCrawlerTool(config=config)

    # Verify config was applied
    assert crawler.config.timeout == 60000
    assert crawler.config.wait_until == "load"
    assert crawler.config.viewport_width == 1024
    assert crawler.config.viewport_height == 768
    assert crawler.config.use_bot_defense is False
    assert crawler.bot_defense is None

    print("Test completed successfully")


def test_crawler_error_handling(
    mock_page,
    mock_context,
    mock_browser,
    mock_chromium,
    mock_playwright_instance,
):
    """Test crawler error handling."""
    print("\n=== Starting Error Handling Test ===")

    try:
        # Configure mock page
        mock_page.goto.side_effect = Exception("Failed to load page")
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

            # Mock fetch method to simulate error
            async def mock_fetch(url):
                raise Exception("Failed to load page")

            crawler.fetch = mock_fetch

            # Run crawler and expect exception
            with pytest.raises(Exception) as exc_info:
                crawler.run(url="http://example.com")

            assert str(exc_info.value) == "Failed to load page"

            print("Test completed successfully")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Traceback:")
        import traceback

        traceback.print_exc()
        raise


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
        mock_context.close.return_value = None

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
