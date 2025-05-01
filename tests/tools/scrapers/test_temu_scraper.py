"""Tests for TemuScraper."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from tools.playwright_crawler.tool import PlaywrightCrawlerTool
from tools.scrapers.temu_scraper import TemuScraperTool


@pytest.fixture
def mock_html():
    """Create mock HTML content."""
    return """
    <html>
        <body>
            <h1 class="DetailName_title">Test Product</h1>
            <div class="DetailPrice_price">$29.99</div>
            <div class="DetailBreadcrumb">
                <span class="DetailBreadcrumb_item">Home</span>
                <span class="DetailBreadcrumb_item">Fashion</span>
                <span class="DetailBreadcrumb_item">Accessories</span>
            </div>
            <div class="product-image">
                <img src="https://img.temu.com/image1.jpg" />
                <img src="https://img.temu.com/image2.jpg" />
            </div>
            <div class="DetailDescription_content">
                A beautiful test product description
            </div>
            <div class="DetailSpecs_item">
                <span class="DetailSpecs_label">Material</span>
                <span class="DetailSpecs_value">Cotton</span>
            </div>
            <div class="DetailSpecs_item">
                <span class="DetailSpecs_label">Style</span>
                <span class="DetailSpecs_value">Casual</span>
            </div>
            <div class="DetailSize_item">
                <span class="DetailSize_value">S</span>
            </div>
            <div class="DetailSize_item">
                <span class="DetailSize_value">M</span>
            </div>
            <div class="DetailColor_item">
                <span class="DetailColor_value">Red</span>
            </div>
            <div class="DetailColor_item">
                <span class="DetailColor_value">Blue</span>
            </div>
            <div class="DetailReviews_summary">
                <span class="DetailReviews_rating">4.5</span>
                <span class="DetailReviews_count">123 reviews</span>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_content(mock_html):
    """Create mock content dictionary."""
    return {
        "html": mock_html,
        "status": 200,
        "headers": {"Content-Type": "text/html"},
    }


@pytest.fixture
def crawler():
    """Create a PlaywrightCrawlerTool instance."""
    return Mock(spec=PlaywrightCrawlerTool)


@pytest.fixture
def scraper(crawler):
    """Create a TemuScraper instance."""
    return TemuScraperTool(crawler=crawler)


def test_get_domain(scraper):
    """Test get_domain method."""
    assert scraper.get_domain() == "temu.com"


def test_extract_title(scraper, mock_content):
    """Test title extraction."""
    title = scraper.extract_title(mock_content)
    assert title == "Test Product"


def test_extract_title_not_found(scraper, mock_content):
    """Test title extraction when element not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product title"):
        scraper.extract_title(mock_content)


def test_extract_price(scraper, mock_content):
    """Test price extraction."""
    price = scraper.extract_price(mock_content)
    assert price == "29.99"


def test_extract_price_not_found(scraper, mock_content):
    """Test price extraction when element not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product price"):
        scraper.extract_price(mock_content)


def test_extract_price_invalid_format(scraper, mock_content):
    """Test price extraction with invalid format."""
    mock_content[
        "html"
    ] = """
    <html>
        <div class="DetailPrice_price">invalid</div>
    </html>
    """
    with pytest.raises(ValueError, match="Invalid price format: invalid"):
        scraper.extract_price(mock_content)


def test_extract_currency(scraper, mock_content):
    """Test currency extraction."""
    currency = scraper.extract_currency(mock_content)
    assert currency == "USD"


def test_extract_category(scraper, mock_content):
    """Test category extraction."""
    # Add category element to mock content
    mock_content[
        "html"
    ] = """
    <html>
        <div class="DetailBreadcrumb">
            <a class="DetailBreadcrumb_item"
               href="/category/clothing">Clothing</a>
            <a class="DetailBreadcrumb_item"
               href="/category/dresses">Dresses</a>
        </div>
    </html>
    """
    category = scraper.extract_category(mock_content)
    assert category == "Dresses"


def test_extract_images(scraper, mock_content):
    """Test image extraction."""
    images = scraper.extract_images(mock_content)
    assert images == [
        "https://img.temu.com/image1.jpg",
        "https://img.temu.com/image2.jpg",
    ]


def test_extract_images_not_found(scraper, mock_content):
    """Test image extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product images"):
        scraper.extract_images(mock_content)


def test_extract_description(scraper, mock_content):
    """Test description extraction."""
    description = scraper.extract_description(mock_content)
    assert description == "A beautiful test product description"


def test_extract_description_not_found(scraper, mock_content):
    """Test description extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product description"):
        scraper.extract_description(mock_content)


def test_extract_specifications(scraper, mock_content):
    """Test specifications extraction."""
    specs = scraper.extract_specifications(mock_content)
    assert specs == {
        "Material": "Cotton",
        "Style": "Casual",
    }


def test_extract_specifications_not_found(scraper, mock_content):
    """Test specifications extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(
        ValueError, match="Could not find product specifications"
    ):
        scraper.extract_specifications(mock_content)


def test_extract_size_info(scraper, mock_content):
    """Test size info extraction."""
    sizes = scraper.extract_size_info(mock_content)
    assert "S" in sizes
    assert "M" in sizes
    assert isinstance(sizes, dict)


def test_extract_size_info_not_found(scraper, mock_content):
    """Test size info extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product sizes"):
        scraper.extract_size_info(mock_content)


def test_extract_color_options(scraper, mock_content):
    """Test color options extraction."""
    colors = scraper.extract_color_options(mock_content)
    assert colors == ["Red", "Blue"]


def test_extract_color_options_not_found(scraper, mock_content):
    """Test color options extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product colors"):
        scraper.extract_color_options(mock_content)


def test_extract_reviews_summary(scraper, mock_content):
    """Test reviews summary extraction."""
    summary = scraper.extract_reviews_summary(mock_content)
    assert summary == {
        "rating": 4.5,
        "review_count": 123,
    }


def test_extract_reviews_summary_not_found(scraper, mock_content):
    """Test reviews summary extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find reviews summary"):
        scraper.extract_reviews_summary(mock_content)


def test_extract_reviews_summary_invalid_values(scraper, mock_content):
    """Test reviews summary extraction with invalid values."""
    mock_content[
        "html"
    ] = """
    <html>
        <div class="DetailReviews_summary">
            <span class="DetailReviews_rating">invalid</span>
            <span class="DetailReviews_count">invalid</span>
        </div>
    </html>
    """
    with pytest.raises(ValueError, match="Invalid reviews summary format"):
        scraper.extract_reviews_summary(mock_content)


def test_extract_reviews_summary_missing_elements(scraper, mock_content):
    """Test reviews summary extraction with missing rating or count elements."""
    # Test with missing rating element
    mock_content[
        "html"
    ] = """
    <html>
        <div class="DetailReviews_summary">
            <span class="DetailReviews_count">123 reviews</span>
        </div>
    </html>
    """
    with pytest.raises(
        ValueError, match="Could not find rating or review count"
    ):
        scraper.extract_reviews_summary(mock_content)

    # Test with missing count element
    mock_content[
        "html"
    ] = """
    <html>
        <div class="DetailReviews_summary">
            <span class="DetailReviews_rating">4.5</span>
        </div>
    </html>
    """
    with pytest.raises(
        ValueError, match="Could not find rating or review count"
    ):
        scraper.extract_reviews_summary(mock_content)


def test_extract_category_not_found(scraper, mock_content):
    """Test category extraction when not found."""
    mock_content["html"] = "<html></html>"
    with pytest.raises(ValueError, match="Could not find product category"):
        scraper.extract_category(mock_content)


@pytest.mark.asyncio
async def test_run_with_html_content(scraper, mock_content):
    """Test run method with provided HTML content."""
    input_data = {
        "url": "https://temu.com/product",
        "html_content": mock_content["html"],
    }
    result = await scraper._async_run(input_data)

    # Check each field individually to allow for additional fields
    assert result["title"] == "Test Product"
    assert result["price"] == "29.99"
    assert result["currency"] == "USD"
    assert result["images"] == [
        "https://img.temu.com/image1.jpg",
        "https://img.temu.com/image2.jpg",
    ]
    assert result["description"] == "A beautiful test product description"
    assert result["specifications"] == {
        "Material": "Cotton",
        "Style": "Casual",
    }
    assert result["size_info"] == {"S": "Size option 1", "M": "Size option 2"}
    assert result["color_options"] == ["Red", "Blue"]
    assert result["reviews_summary"] == {
        "rating": 4.5,
        "review_count": 123,
    }
    assert result["source_url"] == "https://temu.com/product"

    # Check for new fields added for backward compatibility
    assert "url" in result
    assert "category" in result


@pytest.mark.asyncio
async def test_run_with_crawler(scraper, mock_content):
    """Test run method with crawler."""
    scraper.crawler.fetch = AsyncMock(return_value=mock_content)
    input_data = {"url": "https://temu.com/product"}
    result = await scraper._async_run(input_data)

    # Check each field individually to allow for additional fields
    assert result["title"] == "Test Product"
    assert result["price"] == "29.99"
    assert result["currency"] == "USD"
    assert result["images"] == [
        "https://img.temu.com/image1.jpg",
        "https://img.temu.com/image2.jpg",
    ]
    assert result["description"] == "A beautiful test product description"
    assert result["specifications"] == {
        "Material": "Cotton",
        "Style": "Casual",
    }
    assert result["size_info"] == {"S": "Size option 1", "M": "Size option 2"}
    assert result["color_options"] == ["Red", "Blue"]
    assert result["reviews_summary"] == {
        "rating": 4.5,
        "review_count": 123,
    }
    assert result["source_url"] == "https://temu.com/product"

    # Check for new fields added for backward compatibility
    assert "url" in result
    assert "category" in result


def test_run_method(scraper, mock_content):
    """Test the synchronous run method that wraps the async implementation."""
    # Mock the asyncio.run function to avoid actually running the event loop
    with patch("asyncio.run") as mock_run:
        mock_run.return_value = {"title": "Test Product"}

        # Call the synchronous run method
        result = scraper.run({"url": "https://temu.com/product"})

        # Verify that asyncio.run was called with the _async_run method
        mock_run.assert_called_once()
        assert result == {"title": "Test Product"}


@pytest.mark.asyncio
async def test_can_handle_url(scraper):
    """Test URL handling check."""
    assert scraper.can_handle_url("https://temu.com/product")
    assert scraper.can_handle_url("https://us.temu.com/product")
    assert not scraper.can_handle_url("https://other-site.com/product")


@pytest.mark.asyncio
async def test_cleanup(scraper):
    """Test cleanup method."""
    scraper.crawler.cleanup = AsyncMock()
    await scraper.cleanup()
    scraper.crawler.cleanup.assert_called_once()
