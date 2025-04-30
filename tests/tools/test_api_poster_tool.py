"""Tests for the APIPosterTool."""

from unittest.mock import Mock

import pytest
import requests

from src.tools.api_poster_tool import APIPosterTool


@pytest.fixture
def api_poster():
    """Create an APIPosterTool instance for testing."""
    return APIPosterTool(
        api_url="https://api.example.com/products",
        validator=Mock(),
    )


@pytest.fixture
def valid_product_data():
    """Create valid test data."""
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


def test_successful_post(api_poster, valid_product_data):
    """Test successful data posting."""
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "status": "success"}
    mock_response.status_code = 200

    api_poster._session.post = Mock(return_value=mock_response)
    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )

    success, data, error = api_poster.post_data(valid_product_data)
    assert success is True
    assert data == {"id": "123", "status": "success"}
    assert error is None


def test_invalid_data_post(api_poster):
    """Test posting invalid data."""
    invalid_data = {
        "title": "",  # Invalid: empty title
        "price": -10,  # Invalid: negative price
    }
    api_poster.validator.validate.return_value = (
        False,
        None,
        "Validation failed",
    )

    success, data, error = api_poster.post_data(invalid_data)
    assert success is False
    assert data is None
    assert error == "Validation failed: Validation failed"


def test_api_error_handling(api_poster, valid_product_data):
    """Test handling of API errors."""
    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )
    api_poster._session.post.side_effect = requests.RequestException(
        "API Error"
    )

    success, data, error = api_poster.post_data(valid_product_data)
    assert success is False
    assert data is None
    assert "API Error" in str(error)


def test_api_error_with_json_response(api_poster, valid_product_data):
    """Test handling of API errors with JSON response."""
    mock_response = Mock()
    mock_response.json.return_value = {"error": "Invalid request"}
    mock_error = requests.RequestException("HTTP Error")
    mock_error.response = mock_response

    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )
    api_poster._session.post.side_effect = mock_error

    success, data, error = api_poster.post_data(valid_product_data)
    assert success is False
    assert data is None
    assert "Invalid request" in str(error)


def test_health_check_success(api_poster):
    """Test successful health check."""
    mock_response = Mock()
    mock_response.status_code = 200
    api_poster._session.get = Mock(return_value=mock_response)

    assert api_poster.health_check() is True


def test_health_check_failure(api_poster):
    """Test failed health check."""
    api_poster._session.get.side_effect = requests.RequestException()
    assert api_poster.health_check() is False
