"""Tests for the APIPosterTool."""

import pytest
from typing import Dict, Any
from unittest.mock import patch, Mock
import requests
from src.tools.api_poster_tool import APIPosterTool


@pytest.fixture
def api_poster() -> APIPosterTool:
    """Fixture providing a configured APIPosterTool instance."""
    return APIPosterTool(
        api_url="https://api.example.com/products", api_key="test-api-key"
    )


@pytest.fixture
def valid_product_data() -> Dict[str, Any]:
    """Fixture providing valid product test data."""
    return {
        "title": "Test Product",
        "price": 29.99,
        "currency": "USD",
        "images": ["https://example.com/image1.jpg"],
        "category": "Electronics",
        "description": "A test product description",
        "source_url": "https://example.com/product",
        "sku": "TEST-123",
        "brand": "TestBrand",
        "availability": True,
        "variants": ["Red", "Blue"],
    }


def test_successful_post(
    api_poster: APIPosterTool, valid_product_data: Dict[str, Any]
) -> None:
    """Test successful API post with valid data."""
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "status": "success"}
    mock_response.status_code = 200

    with patch("requests.post") as mock_post:
        mock_post.return_value = mock_response
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is True
    assert response == {"id": "123", "status": "success"}
    assert error is None
    mock_post.assert_called_once()
    headers = mock_post.call_args[1]["headers"]
    assert headers["X-API-Key"] == "test-api-key"


def test_bearer_token_auth() -> None:
    """Test bearer token authentication setup."""
    tool = APIPosterTool(
        api_url="https://api.example.com/products", bearer_token="test-token"
    )
    assert tool.headers["Authorization"] == "Bearer test-token"
    assert "X-API-Key" not in tool.headers


def test_custom_headers() -> None:
    """Test custom headers configuration."""
    custom_headers = {
        "X-Custom-Header": "custom-value",
        "User-Agent": "BoomScraper/1.0",
    }
    tool = APIPosterTool(
        api_url="https://api.example.com/products", custom_headers=custom_headers
    )
    assert tool.headers["X-Custom-Header"] == "custom-value"
    assert tool.headers["User-Agent"] == "BoomScraper/1.0"


def test_update_auth() -> None:
    """Test updating authentication credentials."""
    tool = APIPosterTool(api_url="https://api.example.com/products")
    tool.update_auth(api_key="new-key", bearer_token="new-token")
    assert tool.headers["X-API-Key"] == "new-key"
    assert tool.headers["Authorization"] == "Bearer new-token"


def test_invalid_data_post(api_poster: APIPosterTool) -> None:
    """Test handling of invalid data submission."""
    invalid_data = {
        "title": "",  # Invalid: empty title
        "price": -10,  # Invalid: negative price
    }
    success, response, error = api_poster.post_data(invalid_data)

    assert success is False
    assert response is None
    assert "Validation failed" in error


def test_api_error_handling(
    api_poster: APIPosterTool, valid_product_data: Dict[str, Any]
) -> None:
    """Test handling of API request errors."""
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("API is down")
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is False
    assert response is None
    assert "API request failed" in error


def test_api_error_with_json_response(
    api_poster: APIPosterTool, valid_product_data: Dict[str, Any]
) -> None:
    """Test handling of API errors with JSON response."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Invalid API key"}
    mock_error = requests.exceptions.HTTPError("400 Client Error")
    mock_error.response = mock_response

    with patch("requests.post") as mock_post:
        mock_post.side_effect = mock_error
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is False
    assert response is None
    assert "Invalid API key" in error


def test_health_check_success(api_poster: APIPosterTool) -> None:
    """Test successful health check."""
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200)
        assert api_poster.health_check() is True
        mock_get.assert_called_once()
        headers = mock_get.call_args[1]["headers"]
        assert headers["X-API-Key"] == "test-api-key"


def test_health_check_failure(api_poster: APIPosterTool) -> None:
    """Test failed health check."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException
        assert api_poster.health_check() is False


def test_multiple_auth_methods() -> None:
    """Test multiple authentication methods together."""
    tool = APIPosterTool(
        api_url="https://api.example.com/products",
        api_key="test-key",
        bearer_token="test-token",
        custom_headers={"X-Custom": "value"},
    )
    assert tool.headers["X-API-Key"] == "test-key"
    assert tool.headers["Authorization"] == "Bearer test-token"
    assert tool.headers["X-Custom"] == "value"
    assert tool.headers["Content-Type"] == "application/json"
