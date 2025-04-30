"""Tests for the ValidatorTool."""

import pytest

from src.tools.schemas import ProductSchema
from src.tools.validator_tool import ValidatorTool


@pytest.fixture
def validator():
    """Create a ValidatorTool instance for testing."""
    return ValidatorTool(schema=ProductSchema)


@pytest.fixture
def valid_data():
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


def test_valid_product_data(validator, valid_data):
    """Test validation of valid product data."""
    is_valid, validated_data, error = validator.validate(valid_data)
    assert is_valid is True
    assert validated_data is not None
    assert error is None
    assert validated_data["title"] == valid_data["title"]
    assert validated_data["price"] == valid_data["price"]
    assert validated_data["sku"] == valid_data["sku"]
    assert validated_data["brand"] == valid_data["brand"]


def test_invalid_product_data(validator):
    """Test validation of invalid product data."""
    data = {
        "title": "",  # Invalid: empty string
        "price": -10,  # Invalid: negative price
        "currency": "USDD",  # Invalid: too long
        "images": [],  # Invalid: empty list
        "category": "Electronics",
        "description": "A test product description",
        "source_url": "not-a-url",  # Invalid: not a URL
        "sku": "TEST@123",  # Invalid: special characters
        "brand": "",  # Invalid: empty string
    }
    is_valid, validated_data, error = validator.validate(data)
    assert is_valid is False
    assert validated_data is None
    assert error is not None
    assert "title" in str(error)
    assert "price" in str(error)
    assert "currency" in str(error)
    assert "images" in str(error)
    assert "source_url" in str(error)
    assert "sku" in str(error)
    assert "brand" in str(error)


def test_missing_required_fields(validator):
    """Test validation with missing required fields."""
    data = {
        "title": "Test Product",
        "price": 29.99,
        # Missing other required fields
    }
    is_valid, validated_data, error = validator.validate(data)
    assert is_valid is False
    assert validated_data is None
    assert error is not None


def test_optional_fields(validator, valid_data):
    """Test validation with optional fields removed."""
    # Remove optional fields
    del valid_data["sku"]
    del valid_data["brand"]
    del valid_data["variants"]

    is_valid, validated_data, error = validator.validate(valid_data)
    assert is_valid is True
    assert validated_data is not None
    assert error is None
    assert "sku" not in validated_data
    assert "brand" not in validated_data
    assert validated_data["variants"] == []


def test_invalid_sku_format(validator, valid_data):
    """Test validation with invalid SKU format."""
    valid_data["sku"] = "TEST@123#"  # Invalid: contains special characters
    is_valid, validated_data, error = validator.validate(valid_data)
    assert is_valid is False
    assert validated_data is None
    assert "sku" in str(error)


def test_default_availability(validator, valid_data):
    """Test default availability value."""
    del valid_data["availability"]
    is_valid, validated_data, error = validator.validate(valid_data)
    assert is_valid is True
    assert validated_data["availability"] is True  # Default value
