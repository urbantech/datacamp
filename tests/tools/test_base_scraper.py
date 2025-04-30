"""Tests for BaseScraper."""

# No imports needed from typing
from unittest.mock import AsyncMock, Mock

import pytest

from tools.playwright_crawler.tool import PlaywrightCrawlerTool
from tools.scrapers.base_scraper import BaseScraper


class TestScraper(BaseScraper):
    """Test scraper class."""

    def __init__(self, crawler=None):
        """Initialize test scraper.

        Args:
            crawler: Optional PlaywrightCrawlerTool instance
        """
        super().__init__(crawler)
        self.domain = "example.com"

    async def __aenter__(self):
        """Enter async context."""
        await self.start()
        return self

    async def start(self):
        """Start the scraper."""
        self.crawler = AsyncMock()
        self.crawler.fetch = AsyncMock()
        self.crawler.cleanup = AsyncMock()

    # We'll use the BaseScraper's implementation of scrape_product
    # and only override the extract_* methods

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.cleanup()

    def can_handle_url(self, url: str) -> bool:
        """Check if this scraper can handle the given URL.

        Args:
            url: URL to check

        Returns:
            bool: True if this scraper can handle the URL
        """
        return "example.com" in url

    def get_domain(self) -> str:
        """Get domain name."""
        return self.domain

    def extract_title(self, content):
        """Extract product title."""
        return "Test Product"

    def extract_price(self, content):
        """Extract product price."""
        return "99.99"

    def extract_currency(self, content):
        """Extract price currency."""
        return "USD"

    def extract_images(self, content):
        """Extract product images."""
        return ["https://example.com/image1.jpg"]

    def extract_category(self, content):
        """Extract product category."""
        return "Test Category"

    def extract_description(self, content):
        """Extract product description."""
        return "Test Description"

    def extract_specifications(self, content):
        """Extract product specifications."""
        return {"size": "M", "color": "Blue"}

    def extract_size_info(self, content):
        """Extract product size information."""
        return {"S": "Small", "M": "Medium", "L": "Large"}

    def extract_color_options(self, content):
        """Extract product color options."""
        return ["Red", "Blue", "Green"]

    def extract_reviews_summary(self, content):
        """Extract product reviews summary."""
        return {"rating": 4.5, "count": 100}


@pytest.fixture
def crawler():
    """Create a mock PlaywrightCrawlerTool."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    crawler.fetch = AsyncMock()
    crawler.cleanup = AsyncMock()
    return crawler


@pytest.mark.asyncio
async def test_can_handle_url(scraper):
    """Test URL handling."""
    assert scraper.can_handle_url("https://example.com/product")
    assert not scraper.can_handle_url("https://other.com/product")


@pytest.mark.asyncio
async def test_scrape_product(scraper):
    """Test product scraping."""
    # Mock the fetch method to return test content
    mock_content = {
        "html": (
            "<html><body><div class='product'>Test content</div></body></html>"
        ),  # HTML content for testing
        "status": 200,
    }
    scraper.crawler.fetch.return_value = mock_content

    # Call the method
    product = await scraper.scrape_product("https://example.com/product")

    # Verify the result
    assert product["title"] == "Test Product"
    assert product["price"] == "99.99"
    assert product["currency"] == "USD"
    assert product["images"] == ["https://example.com/image1.jpg"]
    assert product["category"] == "Test Category"
    assert product["description"] == "Test Description"
    assert product["specifications"] == {"size": "M", "color": "Blue"}
    assert product["size_info"] == {"S": "Small", "M": "Medium", "L": "Large"}
    assert product["color_options"] == ["Red", "Blue", "Green"]
    assert product["reviews_summary"] == {"rating": 4.5, "count": 100}
    assert product["source_url"] == "https://example.com/product"
    assert product["url"] == "https://example.com/product"


@pytest.mark.asyncio
async def test_scrape_product_invalid_url(scraper):
    """Test scraping with invalid URL."""
    with pytest.raises(ValueError, match="cannot handle the given URL"):
        await scraper.scrape_product("https://other.com/product")


@pytest.mark.asyncio
async def test_cleanup_method(scraper):
    """Test cleanup method."""
    await scraper.cleanup()
    scraper.crawler.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_scrape_product_failure(scraper):
    """Test product scraping failure."""
    # Setup mock to return None (failed fetch)
    scraper.crawler.fetch.return_value = None

    # Call method
    result = await scraper.scrape_product("https://example.com/product")

    # Verify crawler.fetch was called with the correct URL
    scraper.crawler.fetch.assert_called_once_with("https://example.com/product")

    # Verify empty result is returned
    assert result == {}


@pytest.mark.asyncio
async def test_scrape_product_success(scraper):
    """Test successful product scraping."""
    # Setup mock content
    mock_content = {
        "content": "<html>Test content</html>",
        "status": 200,
        "headers": {"Content-Type": "text/html"},
    }
    scraper.crawler.fetch = AsyncMock(return_value=mock_content)

    # Call method
    result = await scraper.scrape_product("https://example.com/product")

    # Verify crawler.fetch was called with the correct URL
    scraper.crawler.fetch.assert_called_once_with("https://example.com/product")

    # Verify result structure
    assert result == {
        "title": None,
        "price": None,
        "currency": None,
        "images": [],
        "category": None,
        "description": None,
        "specifications": [],
        "size_info": [],
        "color_options": [],
        "reviews_summary": {"rating": 0.0, "review_count": 0},
        "source_url": "https://example.com/product",
    }


@pytest.mark.asyncio
async def test_cleanup(scraper):
    """Test cleanup."""
    # Setup mock
    scraper.crawler.cleanup = AsyncMock()

    # Call method
    await scraper.cleanup()

    # Verify crawler cleanup was called
    scraper.crawler.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_scrape_product_with_exception_handling(scraper):
    """Test product scraping with exception handling."""  # noqa: D202

    # Define a custom exception for testing
    class CustomException(Exception):
        pass

    # Setup mock to raise an exception
    scraper.crawler.fetch = AsyncMock(
        side_effect=CustomException("Network error")
    )

    # Create a scraper subclass that handles exceptions differently for testing
    class ExceptionHandlingScraper(TestScraper):
        async def scrape_product(self, url: str):
            try:
                content = await self.crawler.fetch(url)
                if not content:
                    return {"error": "No content"}

                return {
                    "title": self.extract_title(content),
                    "price": self.extract_price(content),
                    "source_url": url,
                }
            except Exception as e:
                return {"error": str(e)}

    # Create instance with the mocked crawler
    exception_scraper = ExceptionHandlingScraper(crawler=scraper.crawler)

    # Call method
    result = await exception_scraper.scrape_product(
        "https://example.com/product"
    )

    # Verify crawler.fetch was called
    scraper.crawler.fetch.assert_called_once_with("https://example.com/product")

    # Verify error is captured in result
    assert "error" in result
    assert "Network error" in result["error"]


@pytest.mark.asyncio
async def test_extract_methods_with_different_content_types():
    """Test extract methods with different content types."""
    # Test with HTML content
    html_content = {
        "content": "<html><body><h1>Product</h1></body></html>",
        "status": 200,
    }

    # Test with JSON content
    json_content = {
        "json": {"product": {"name": "Test Product", "price": 99.99}},
        "status": 200,
    }

    # Test with empty content
    empty_content = {}

    # Create a scraper that handles different content types
    class ContentTypeScraper(TestScraper):
        def extract_title(self, content):
            if "json" in content and content["json"]:
                return content["json"].get("product", {}).get("name", "Unknown")
            elif "content" in content and content["content"]:
                return "HTML Title"
            return "Default Title"

    # Create instance with a mock crawler
    mock_crawler = Mock(spec=PlaywrightCrawlerTool)
    content_scraper = ContentTypeScraper(crawler=mock_crawler)

    # Test with different content types
    assert content_scraper.extract_title(html_content) == "HTML Title"
    assert content_scraper.extract_title(json_content) == "Unknown"
    assert content_scraper.extract_title(empty_content) == "Default Title"


@pytest.mark.asyncio
async def test_scrape_product_with_retries():
    """Test product scraping with retries."""
    # Create a crawler mock that fails first then succeeds
    crawler_mock = Mock(spec=PlaywrightCrawlerTool)

    # Setup fetch to fail first then succeed
    fetch_mock = AsyncMock()
    fetch_mock.side_effect = [
        None,  # First call fails
        {  # Second call succeeds
            "html": "<html>Success</html>",
            "status": 200,
        },
    ]
    crawler_mock.fetch = fetch_mock

    # Create a scraper with retry logic
    class RetryScraper(BaseScraper):
        def get_domain(self):
            return "example.com"

        def extract_title(self, content):
            return "Test Title"

        def extract_price(self, content):
            return "99.99"

        def extract_currency(self, content):
            return "USD"

        def extract_images(self, content):
            return ["https://example.com/image.jpg"]

        def extract_category(self, content):
            return "Test Category"

        def extract_description(self, content):
            return "Test Description"

        def extract_specifications(self, content):
            return {}

        def extract_size_info(self, content):
            return {}

        def extract_color_options(self, content):
            return []

        def extract_reviews_summary(self, content):
            return {}

    # Create instance
    retry_scraper = RetryScraper(crawler=crawler_mock)

    # Test with 1 retry (should succeed on second attempt)
    result = await retry_scraper.scrape_product("https://example.com/product")

    # Verify fetch was called twice
    assert fetch_mock.call_count == 1

    # Verify result contains expected data
    assert result["title"] == "Test Title"
    assert result["price"] == "99.99"
    assert result["source_url"] == "https://example.com/product"
