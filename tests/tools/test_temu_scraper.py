"""Tests for TemuScraper."""

from unittest.mock import AsyncMock, Mock

import pytest

from tools.scrapers.temu_scraper import TemuScraperTool


@pytest.fixture
def mock_crawler():
    """Create a mock PlaywrightCrawlerTool."""
    crawler = Mock()
    crawler.fetch = AsyncMock()
    crawler.cleanup = AsyncMock()
    return crawler


@pytest.fixture
def temu_scraper(mock_crawler):
    """Create a TemuScraperTool instance."""
    return TemuScraperTool(crawler=mock_crawler)


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
                <p>A great test product description</p>
            </div>
            <div class="DetailSpecs">
                <div class="DetailSpecs_item">
                    <span class="DetailSpecs_label">Material</span>
                    <span class="DetailSpecs_value">Cotton</span>
                </div>
                <div class="DetailSpecs_item">
                    <span class="DetailSpecs_label">Style</span>
                    <span class="DetailSpecs_value">Casual</span>
                </div>
            </div>
            <div class="DetailSize">
                <div class="DetailSize_item">
                    <span class="DetailSize_label">Size</span>
                    <span class="DetailSize_value">S</span>
                </div>
                <div class="DetailSize_item">
                    <span class="DetailSize_label">Size</span>
                    <span class="DetailSize_value">M</span>
                </div>
                <div class="DetailSize_item">
                    <span class="DetailSize_label">Size</span>
                    <span class="DetailSize_value">L</span>
                </div>
            </div>
            <div class="DetailColor">
                <div class="DetailColor_item">
                    <span class="DetailColor_label">Color</span>
                    <span class="DetailColor_value">Red</span>
                </div>
                <div class="DetailColor_item">
                    <span class="DetailColor_label">Color</span>
                    <span class="DetailColor_value">Blue</span>
                </div>
            </div>
            <div class="DetailSpecs">
                <div class="DetailSpecs_item">
                    <div class="DetailSpecs_key">Material</div>
                    <div class="DetailSpecs_value">Cotton</div>
                </div>
                <div class="DetailSpecs_item">
                    <div class="DetailSpecs_key">Style</div>
                    <div class="DetailSpecs_value">Casual</div>
                </div>
            </div>
            <div class="DetailSize">
                <div class="DetailSize_size">S</div>
                <div class="DetailSize_size">M</div>
                <div class="DetailSize_size">L</div>
            </div>
            <div class="DetailColor">
                <div class="DetailColor_color">Red</div>
                <div class="DetailColor_color">Blue</div>
            </div>
            <div class="DetailRating">
                <div class="DetailRating_rating">4.5</div>
                <div class="DetailRating_count">(123)</div>
            </div>
            <div class="DetailReviews">
                <div class="DetailReviews_summary">
                    <div class="DetailReviews_rating">4.5</div>
                    <div class="DetailReviews_count">123 reviews</div>
                </div>
            </div>
            <div class="product-image">
                <img src="https://img.temu.com/image1.jpg">
            </div>
            <div class="product-image">
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
    assert product["specifications"] == {
        "Material": "Cotton",
        "Style": "Casual",
    }
    assert product["size_info"] == ["S", "M", "L"]
    assert product["color_options"] == ["Red", "Blue"]
    assert product["reviews_summary"] == {"rating": 4.5, "review_count": 123}
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
        temu_scraper.extract_description({"html": "<div></div>"})


def test_extract_specifications(temu_scraper):
    """Test specifications extraction."""
    content = {
        "html": """
        <div class='DetailSpecs'>
            <div class='DetailSpecs_item'>
                <span class='DetailSpecs_label'>Material</span>
                <span class='DetailSpecs_value'>Cotton</span>
            </div>
            <div class='DetailSpecs_item'>
                <span class='DetailSpecs_label'>Style</span>
                <span class='DetailSpecs_value'>Casual</span>
            </div>
        </div>
        """
    }
    specs = temu_scraper.extract_specifications(content)
    assert specs == {"Material": "Cotton", "Style": "Casual"}


def test_extract_size_info(temu_scraper):
    """Test size info extraction."""
    content = {
        "html": """
        <div class='DetailSize'>
            <div class='DetailSize_item'>
                <span class='DetailSize_label'>Size</span>
                <span class='DetailSize_value'>S</span>
            </div>
            <div class='DetailSize_item'>
                <span class='DetailSize_label'>Size</span>
                <span class='DetailSize_value'>M</span>
            </div>
            <div class='DetailSize_item'>
                <span class='DetailSize_label'>Size</span>
                <span class='DetailSize_value'>L</span>
            </div>
        </div>
        """
    }
    sizes = temu_scraper.extract_size_info(content)
    assert sizes == ["S", "M", "L"]


def test_extract_color_options(temu_scraper):
    """Test color options extraction."""
    content = {
        "html": """
        <div class='DetailColor'>
            <div class='DetailColor_item'>
                <span class='DetailColor_label'>Color</span>
                <span class='DetailColor_value'>Red</span>
            </div>
            <div class='DetailColor_item'>
                <span class='DetailColor_label'>Color</span>
                <span class='DetailColor_value'>Blue</span>
            </div>
        </div>
        """
    }
    colors = temu_scraper.extract_color_options(content)
    assert colors == ["Red", "Blue"]


def test_extract_reviews_summary(temu_scraper):
    """Test reviews summary extraction."""
    content = {
        "html": """
        <div class='DetailReviews'>
            <div class='DetailReviews_summary'>
                <div class='DetailReviews_rating'>4.5</div>
                <div class='DetailReviews_count'>123 reviews</div>
            </div>
        </div>
        """
    }
    reviews = temu_scraper.extract_reviews_summary(content)
    assert reviews == {"rating": 4.5, "review_count": 123}


def test_extract_reviews_summary_missing(temu_scraper):
    """Test reviews summary extraction with missing elements."""
    with pytest.raises(ValueError, match="Could not find reviews summary"):
        temu_scraper.extract_reviews_summary({"html": "<div></div>"})


def test_extract_reviews_summary_invalid_format(temu_scraper):
    """Test reviews summary extraction with invalid format."""
    content = {
        "html": """
        <div class='DetailReviews'>
            <div class='DetailReviews_summary'>
                <div class='DetailReviews_rating'>invalid</div>
                <div class='DetailReviews_count'>not a number reviews</div>
            </div>
        </div>
        """
    }
    with pytest.raises(ValueError, match="Invalid reviews summary format"):
        temu_scraper.extract_reviews_summary(content)


def test_extract_size_info_missing(temu_scraper):
    """Test size info extraction with missing elements."""
    with pytest.raises(ValueError, match="Could not find product sizes"):
        temu_scraper.extract_size_info({"html": "<div></div>"})


def test_extract_color_options_missing(temu_scraper):
    """Test color options extraction with missing elements."""
    with pytest.raises(ValueError, match="Could not find product colors"):
        temu_scraper.extract_color_options({"html": "<div></div>"})
