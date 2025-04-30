"""Tests for TemuScraperTool."""

from unittest.mock import AsyncMock, Mock

import pytest

from tools.playwright_crawler.tool import PlaywrightCrawlerTool
from tools.scrapers.temu_scraper import TemuScraperTool


def test_temu_scraper_tool_initialization():
    """Test initialization of TemuScraperTool."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    tool = TemuScraperTool(crawler=crawler)
    assert tool.get_domain() == "temu.com"


@pytest.mark.asyncio
async def test_required_fields(mock_html_content):
    """Test that required fields are returned in scrape_product method."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    crawler.fetch = AsyncMock(
        return_value={
            "html": mock_html_content,
            "status": 200,
            "headers": {"Content-Type": "text/html"},
        }
    )

    tool = TemuScraperTool(crawler=crawler)

    # Check that the method returns a dictionary with expected keys
    result = await tool._async_run({"url": "https://temu.com/product"})

    assert "title" in result
    assert "price" in result
    assert "images" in result


@pytest.mark.asyncio
async def test_extract_product_data(mock_html_content):
    """Test extracting product data from HTML content."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    tool = TemuScraperTool(crawler=crawler)

    # Create a content dictionary
    content = {
        "html": mock_html_content,
        "status": 200,
        "headers": {"Content-Type": "text/html"},
    }

    # Test individual extraction methods
    title = tool.extract_title(content)
    price = tool.extract_price(content)
    images = tool.extract_images(content)

    assert title == "Test Product"
    assert price == "19.99"
    assert len(images) == 2
    assert "image1.jpg" in images


@pytest.mark.asyncio
async def test_run(mock_input_data, mock_html_content):
    """Test running the tool with input data."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    crawler.fetch = AsyncMock(
        return_value={
            "html": mock_html_content,
            "status": 200,
            "headers": {"Content-Type": "text/html"},
        }
    )

    tool = TemuScraperTool(crawler=crawler)

    result = await tool._async_run(mock_input_data)

    assert isinstance(result, dict)
    assert result["title"] == "Test Product"
    assert result["price"] == "19.99"
    assert len(result["images"]) == 2
    assert result["source_url"] == mock_input_data["url"]


@pytest.mark.asyncio
async def test_validation():
    """Test error handling in the run method."""
    crawler = Mock(spec=PlaywrightCrawlerTool)
    tool = TemuScraperTool(crawler=crawler)

    # Test with missing required field (url)
    invalid_input = {}

    # The run method should handle missing url gracefully
    with pytest.raises(KeyError):
        # We need to use _async_run directly since run is a synchronous wrapper
        await tool._async_run(invalid_input)


@pytest.fixture
def mock_html_content():
    """Mock HTML content for testing."""
    return """
    <html>
        <body>
            <h1 class="DetailName_title">Test Product</h1>
            <div class="DetailPrice_price">$19.99</div>
            <div class="product-image">
                <img src="image1.jpg" />
                <img src="image2.jpg" />
            </div>
            <div class="DetailDescription_content">Test description</div>
            <div class="DetailBreadcrumb">
                <a class="DetailBreadcrumb_item" href="#">Home</a>
                <a class="DetailBreadcrumb_item" href="#">Category</a>
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
def mock_input_data():
    """Mock input data for testing."""
    return {"url": "https://temu.com/product"}


# These fixtures are no longer needed with the new implementation
