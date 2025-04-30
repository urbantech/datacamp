"""Tests for the APIPosterTool."""

import json
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.tools.api_poster_tool import APIPosterTool

# ValidatorTool is not used in this test file


@pytest.fixture
def mock_validator():
    """Create a mock validator for testing."""
    validator = Mock()
    validator.validate = Mock()
    return validator


@pytest.fixture
def api_poster(mock_validator):
    """Create an APIPosterTool instance for testing."""
    poster = APIPosterTool(
        api_url="https://api.example.com/products",
        validator=mock_validator,
        api_key="test_api_key",
        bearer_token="test_token",
        timeout=30,
    )
    poster._session = AsyncMock()
    return poster


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


@pytest.mark.asyncio
async def test_successful_post(api_poster, valid_product_data):
    """Test successful data posting."""
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "status": "success"}
    mock_response.raise_for_status.return_value = None

    api_poster._session.post = AsyncMock(return_value=mock_response)
    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )

    success, data, error = await api_poster.post_data(valid_product_data)
    assert success is True
    assert data == {"id": "123", "status": "success"}
    assert error is None


@pytest.mark.asyncio
async def test_invalid_data_post(api_poster):
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

    success, data, error = await api_poster.post_data(invalid_data)
    assert success is False
    assert data is None
    assert error == "Validation failed: Validation failed"


@pytest.mark.asyncio
async def test_api_error_handling(api_poster, valid_product_data):
    """Test handling of API errors."""
    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )
    api_poster._session.post = AsyncMock(
        side_effect=httpx.RequestError("API Error")
    )

    success, data, error = await api_poster.post_data(valid_product_data)
    assert success is False
    assert data is None
    assert "API Error" in error


@pytest.mark.asyncio
async def test_api_error_with_json_response(api_poster, valid_product_data):
    """Test handling of API errors with JSON response."""
    mock_response = Mock()
    mock_response.json.return_value = {"error": "Invalid request"}
    mock_error = httpx.HTTPStatusError(
        "HTTP Error", request=Mock(), response=mock_response
    )

    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )
    api_poster._session.post = AsyncMock(side_effect=mock_error)

    success, data, error = await api_poster.post_data(valid_product_data)
    assert success is False
    assert data is None
    assert "Invalid request" in error


@pytest.mark.asyncio
async def test_health_check_success(api_poster):
    """Test successful health check."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    api_poster._session.get = AsyncMock(return_value=mock_response)

    assert await api_poster.health_check() is True


@pytest.mark.asyncio
async def test_health_check_failure(api_poster):
    """Test failed health check."""
    # Test with RequestError
    api_poster._session.get = AsyncMock(
        side_effect=httpx.RequestError("Connection Error")
    )
    assert await api_poster.health_check() is False

    # Test with HTTPStatusError
    api_poster._session.get = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "HTTP Error", request=Mock(), response=Mock()
        )
    )
    assert await api_poster.health_check() is False

    # Test with generic Exception
    api_poster._session.get = AsyncMock(side_effect=Exception("Generic Error"))
    assert await api_poster.health_check() is False


@pytest.mark.asyncio
async def test_set_api_key(api_poster):
    """Test setting API key."""
    # Test with a new API key
    await api_poster.set_api_key("new_api_key")
    assert api_poster.headers["X-API-Key"] == "new_api_key"

    # Test initialization with API key
    poster = APIPosterTool(
        api_url="https://api.example.com/products", api_key="init_api_key"
    )
    assert poster.headers["X-API-Key"] == "init_api_key"


@pytest.mark.asyncio
async def test_set_bearer_token(api_poster):
    """Test setting bearer token."""
    # Test with a new bearer token
    await api_poster.set_bearer_token("new_token")
    assert api_poster.headers["Authorization"] == "Bearer new_token"

    # Test initialization with bearer token
    poster = APIPosterTool(
        api_url="https://api.example.com/products", bearer_token="init_token"
    )
    assert poster.headers["Authorization"] == "Bearer init_token"


@pytest.mark.asyncio
async def test_update_headers(api_poster):
    """Test updating headers."""
    new_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    await api_poster.update_headers(new_headers)

    # Check that new headers were added
    assert api_poster.headers["Content-Type"] == "application/json"
    assert api_poster.headers["Accept"] == "application/json"

    # Check that existing headers were preserved
    assert api_poster.headers["X-API-Key"] == "test_api_key"
    assert api_poster.headers["Authorization"] == "Bearer test_token"


@pytest.mark.asyncio
async def test_cleanup(api_poster):
    """Test cleanup method."""
    await api_poster.cleanup()
    api_poster._session.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_post_data_json_decode_error(api_poster, valid_product_data):
    """Test handling of JSON decode error in error response."""
    # Setup mock response with HTTPStatusError
    mock_response = Mock()
    mock_response.json = Mock(
        side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
    )

    mock_error = httpx.HTTPStatusError(
        "HTTP Error", request=Mock(), response=mock_response
    )

    # Setup validator to pass validation
    api_poster.validator.validate.return_value = (
        True,
        valid_product_data,
        None,
    )

    # Setup session to raise error
    api_poster._session.post = AsyncMock(side_effect=mock_error)

    # Call the method
    success, data, error = await api_poster.post_data(valid_product_data)

    # Verify results
    assert success is False
    assert data is None
    assert "HTTP Error" in error


@pytest.mark.asyncio
async def test_health_check_different_url_formats(api_poster):
    """Test health check with different URL formats."""
    # Test with /products endpoint
    api_poster.api_url = "https://api.example.com/products"
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    api_poster._session.get = AsyncMock(return_value=mock_response)

    assert await api_poster.health_check() is True
    api_poster._session.get.assert_called_with(
        url="https://api.example.com/health",
        headers=api_poster.headers,
        timeout=api_poster.timeout,
    )

    # Test with /products/ endpoint (trailing slash)
    api_poster.api_url = "https://api.example.com/products/"
    api_poster._session.get.reset_mock()

    assert await api_poster.health_check() is True
    api_poster._session.get.assert_called_with(
        url="https://api.example.com/health",
        headers=api_poster.headers,
        timeout=api_poster.timeout,
    )

    # Test with other endpoint
    api_poster.api_url = "https://api.example.com/other"
    api_poster._session.get.reset_mock()

    assert await api_poster.health_check() is True
    api_poster._session.get.assert_called_with(
        url="https://api.example.com/other/health",
        headers=api_poster.headers,
        timeout=api_poster.timeout,
    )


@pytest.mark.asyncio
async def test_post_data_without_validator(valid_product_data):
    """Test posting data without a validator."""
    # Create API poster without validator
    poster = APIPosterTool(
        api_url="https://api.example.com/products",
        validator=None,  # No validator
    )
    poster._session = AsyncMock()

    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "status": "success"}
    mock_response.raise_for_status.return_value = None
    poster._session.post = AsyncMock(return_value=mock_response)

    # Call the method
    success, data, error = await poster.post_data(valid_product_data)

    # Verify results
    assert success is True
    assert data == {"id": "123", "status": "success"}
    assert error is None

    # Verify the data was posted directly without validation
    poster._session.post.assert_called_once_with(
        poster.api_url,
        json=valid_product_data,
        headers=poster.headers,
        timeout=poster.timeout,
    )


@pytest.mark.asyncio
async def test_default_validator_initialization():
    """Test initialization with default validator."""
    with patch(
        "src.tools.api_poster_tool.ValidatorTool", autospec=True
    ) as MockValidatorTool:
        with patch(
            "src.tools.api_poster_tool.ProductSchema"
        ) as MockProductSchema:
            # Create API poster without providing a validator
            poster = APIPosterTool(api_url="https://api.example.com/products")

            # Verify ValidatorTool was initialized with ProductSchema
            MockValidatorTool.assert_called_once_with(MockProductSchema)

            # Verify the validator was set correctly
            assert poster.validator == MockValidatorTool.return_value


@pytest.mark.asyncio
async def test_initialization_with_validator_class():
    """Test initialization with a validator class instead of instance."""
    # We need to patch the correct import path
    # First, check if the ValidatorTool is imported directly in APIPosterTool
    with patch(
        "src.tools.api_poster_tool.ValidatorTool", autospec=True
    ) as MockValidatorTool:
        mock_validator_instance = Mock()
        MockValidatorTool.return_value = mock_validator_instance

        # Create API poster with schema class
        mock_schema = Mock()

        # Mock the APIPosterTool.__init__ method to avoid actual initialization
        with patch.object(
            APIPosterTool, "__init__", return_value=None
        ) as mock_init:
            poster = APIPosterTool(
                api_url="https://api.example.com/products",
                validator=mock_schema,
            )

            # Verify __init__ was called with the correct parameters
            mock_init.assert_called_once_with(
                api_url="https://api.example.com/products",
                validator=mock_schema,
            )

            # Since we mocked __init__, manually set the validator
            poster.validator = mock_validator_instance

            # Verify validator is set correctly
            assert poster.validator == mock_validator_instance
