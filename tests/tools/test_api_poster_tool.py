import pytest
from unittest.mock import patch, Mock
import requests
from src.tools.api_poster_tool import APIPosterTool

@pytest.fixture
def api_poster():
    return APIPosterTool(
        api_url="https://api.example.com/products",
        api_key="test-api-key"
    )

@pytest.fixture
def valid_product_data():
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
        "variants": ["Red", "Blue"]
    }

def test_successful_post(api_poster, valid_product_data):
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "status": "success"}
    mock_response.status_code = 200

    with patch('requests.post') as mock_post:
        mock_post.return_value = mock_response
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is True
    assert response == {"id": "123", "status": "success"}
    assert error is None

def test_invalid_data_post(api_poster):
    invalid_data = {
        "title": "",  # Invalid: empty title
        "price": -10  # Invalid: negative price
    }
    success, response, error = api_poster.post_data(invalid_data)

    assert success is False
    assert response is None
    assert "Validation failed" in error

def test_api_error_handling(api_poster, valid_product_data):
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("API is down")
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is False
    assert response is None
    assert "API request failed" in error

def test_api_error_with_json_response(api_poster, valid_product_data):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Invalid API key"}
    mock_error = requests.exceptions.HTTPError("400 Client Error")
    mock_error.response = mock_response

    with patch('requests.post') as mock_post:
        mock_post.side_effect = mock_error
        success, response, error = api_poster.post_data(valid_product_data)

    assert success is False
    assert response is None
    assert "Invalid API key" in error

def test_health_check_success(api_poster):
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(status_code=200)
        assert api_poster.health_check() is True

def test_health_check_failure(api_poster):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException
        assert api_poster.health_check() is False
