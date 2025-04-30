"""Tests for TemuScraper."""

from unittest.mock import AsyncMock, Mock

import pytest

from tools.scrapers.temu_scraper import TemuScraper


@pytest.fixture
def mock_crawler():
    """Create a mock PlaywrightCrawlerTool."""
    crawler = Mock()
    crawler.fetch = AsyncMock()
    crawler.cleanup = AsyncMock()
    return crawler


@pytest.fixture
def temu_scraper(mock_crawler):
    """Create a TemuScraper instance."""
    return TemuScraper(crawler=mock_crawler)


@pytest.fixture
def product_html():
    """Sample product page HTML."""
    return """
    <html>
        <head>
            <script id="__NEXT_DATA__">
                {
                    "props": {
                        "pageProps": {
                            "detail": {
                                "images": [
                                    {"url": "https://img.temu.com/image1.jpg"},
                                    {"url": "https://img.temu.com/image2.jpg"}
                                ]
                            }
                        }
                    }
                }
            </script>
        </head>
        <body>
            <h1 class="DetailName_title">Test Product</h1>
            <div class="DetailPrice_price">$19.99</div>
            <nav class="DetailBreadcrumb">
                <span class="DetailBreadcrumb_item">Home</span>
                <span class="DetailBreadcrumb_item">Fashion</span>
                <span class="DetailBreadcrumb_item">Accessories</span>
            </nav>
            <div class="DetailDescription_content">
                A great test product description
            </div>
            <div class="DetailGallery_image">
                <img src="https://img.temu.com/image1.jpg">
            </div>
            <div class="DetailGallery_image">
                <img src="https://img.temu.com/image2.jpg">
            </div>
        </body>
    </html>
    """


def test_get_domain(temu_scraper):
    """Test domain getter."""
    assert temu_scraper.get_domain() == "temu.com"


@pytest.mark.asyncio
async def test_scrape_product(temu_scraper, product_html):
    """Test full product scraping."""
    url = "https://www.temu.com/product"
    temu_scraper.crawler.fetch.return_value = {"html": product_html}

    product = await temu_scraper.scrape_product(url)

    assert product["title"] == "Test Product"
    assert product["price"] == 19.99
    assert product["currency"] == "USD"
    assert product["category"] == "Accessories"
    assert product["description"] == "A great test product description"
    assert product["images"] == [
        "https://img.temu.com/image1.jpg",
        "https://img.temu.com/image2.jpg",
    ]
    assert product["source_url"] == url


def test_extract_title_missing(temu_scraper):
    """Test title extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product title"):
        temu_scraper.extract_title({"html": "<html></html>"})


def test_extract_price_missing(temu_scraper):
    """Test price extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product price"):
        temu_scraper.extract_price({"html": "<html></html>"})


def test_extract_images_missing(temu_scraper):
    """Test image extraction with missing elements."""
    with pytest.raises(ValueError, match="Could not find product images"):
        temu_scraper.extract_images({"html": "<html></html>"})


def test_extract_category_missing(temu_scraper):
    """Test category extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product category"):
        temu_scraper.extract_category({"html": "<html></html>"})


def test_extract_description_missing(temu_scraper):
    """Test description extraction with missing element."""
    with pytest.raises(ValueError, match="Could not find product description"):
        temu_scraper.extract_description({"html": "<html></html>"})
