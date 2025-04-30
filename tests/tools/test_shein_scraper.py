"""Tests for SheinScraper."""

from unittest.mock import AsyncMock, Mock

import pytest

from tools.scrapers.shein_scraper import SheinScraper


@pytest.fixture
def mock_crawler():
    """Create a mock PlaywrightCrawlerTool."""
    crawler = Mock()
    crawler.fetch = AsyncMock()
    crawler.cleanup = AsyncMock()
    return crawler


@pytest.fixture
def shein_scraper(mock_crawler):
    """Create a SheinScraper instance."""
    return SheinScraper(crawler=mock_crawler)


@pytest.fixture
def product_html():
    """Sample product page HTML."""
    return """
    <html>
        <head>
            <script type="application/ld+json">
                {
                    "name": "Test Product",
                    "image": [
                        "https://img.shein.com/image1.jpg",
                        "https://img.shein.com/image2.jpg"
                    ]
                }
            </script>
        </head>
        <body>
            <h1 class="product-intro__head-name">Test Product</h1>
            <div class="product-intro__head-price">
                <span class="from">$29.99</span>
            </div>
            <nav class="j-bread-crumb">
                <a href="#">Women</a>
                <a href="#">Clothing</a>
                <a href="#">Dresses</a>
            </nav>
            <div class="product-intro__description">
                A beautiful test product description
            </div>
            <div class="product-intro__thumbs-item">
                <img src="https://img.shein.com/image1_thumbnail.jpg">
            </div>
            <div class="product-intro__thumbs-item">
                <img src="https://img.shein.com/image2_thumbnail.jpg">
            </div>
        </body>
    </html>
    """


def test_get_domain(shein_scraper):
    """Test domain getter."""
    assert shein_scraper.get_domain() == "shein.com"


@pytest.mark.asyncio
async def test_scrape_product(shein_scraper, product_html):
    """Test full product scraping."""
    url = "https://us.shein.com/product"
    shein_scraper.crawler.fetch.return_value = {"html": product_html}

    product = await shein_scraper.scrape_product(url)

    assert product["title"] == "Test Product"
    assert product["price"] == 29.99
    assert product["currency"] == "USD"
    assert product["category"] == "Dresses"
    assert product["description"] == "A beautiful test product description"
    assert product["images"] == [
        "https://img.shein.com/image1.jpg",
        "https://img.shein.com/image2.jpg",
    ]
    assert product["source_url"] == url


def test_extract_title_missing(shein_scraper):
    """Test title extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product title"):
        shein_scraper.extract_title({"html": "<html></html>"})


def test_extract_price_missing(shein_scraper):
    """Test price extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product price"):
        shein_scraper.extract_price({"html": "<html></html>"})


def test_extract_images_missing(shein_scraper):
    """Test image extraction with missing elements."""
    with pytest.raises(ValueError, match="Could not find product images"):
        shein_scraper.extract_images({"html": "<html></html>"})


def test_extract_category_missing(shein_scraper):
    """Test category extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product category"):
        shein_scraper.extract_category({"html": "<html></html>"})


def test_extract_description_missing(shein_scraper):
    """Test description extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product description"):
        shein_scraper.extract_description({"html": "<html></html>"})
