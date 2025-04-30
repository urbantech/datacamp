"""Tests for BaseScraper."""

from unittest.mock import AsyncMock, Mock

import pytest

from tools.scrapers.base_scraper import BaseScraper


class TestScraper(BaseScraper):
    """Test implementation of BaseScraper."""

    def get_domain(self) -> str:
        """Get domain name."""
        return "example.com"

    def extract_title(self, content):
        """Extract product title."""
        return "Test Title"

    def extract_price(self, content):
        """Extract product price."""
        return 99.99

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


@pytest.fixture
def mock_crawler():
    """Create a mock PlaywrightCrawlerTool."""
    crawler = Mock()
    crawler.fetch = AsyncMock(return_value={"html": "<html></html>"})
    crawler.cleanup = AsyncMock()
    return crawler


@pytest.fixture
def test_scraper(mock_crawler):
    """Create a TestScraper instance."""
    return TestScraper(crawler=mock_crawler)


def test_can_handle_url(test_scraper):
    """Test URL handling check."""
    assert test_scraper.can_handle_url("https://example.com/product")
    assert test_scraper.can_handle_url("http://www.example.com/product")
    assert not test_scraper.can_handle_url("https://other.com/product")


@pytest.mark.asyncio
async def test_scrape_product(test_scraper):
    """Test product scraping."""
    url = "https://example.com/product"
    product = await test_scraper.scrape_product(url)

    assert product["title"] == "Test Title"
    assert product["price"] == 99.99
    assert product["currency"] == "USD"
    assert product["images"] == ["https://example.com/image1.jpg"]
    assert product["category"] == "Test Category"
    assert product["description"] == "Test Description"
    assert product["source_url"] == url

    test_scraper.crawler.fetch.assert_awaited_once_with(url)


@pytest.mark.asyncio
async def test_scrape_product_invalid_url(test_scraper):
    """Test scraping with invalid URL."""
    with pytest.raises(ValueError, match="This scraper cannot handle URL"):
        await test_scraper.scrape_product("https://other.com/product")


@pytest.mark.asyncio
async def test_cleanup(test_scraper):
    """Test cleanup."""
    await test_scraper.cleanup()
    test_scraper.crawler.cleanup.assert_awaited_once()
