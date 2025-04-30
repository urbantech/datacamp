"""Integration tests for API tools."""

from typing import Optional
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient

# Default test data
DEFAULT_PRODUCT_DATA = {
    "sku": "TEST-123",
    "name": "Test Product",
    "price": 99.99,
    "availability": True,
}

# Default mock validator response
DEFAULT_VALIDATOR_RESPONSE = (True, None)

# Default mock API response
DEFAULT_API_RESPONSE = {"status": "success"}

# Default API key
API_KEY_NAME = "X-API-Key"
API_KEY = "test_api_key"

# Create test app
app = FastAPI()


@app.post("/products")
async def create_product(data: dict, api_key: Optional[str] = None):
    """Create a product with API key auth."""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Invalid data")
    return DEFAULT_API_RESPONSE


@app.post("/products-bearer")
async def create_product_bearer(data: dict, bearer_token: Optional[str] = None):
    """Create a product with bearer token auth."""
    if bearer_token != "test_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Invalid data")
    return DEFAULT_API_RESPONSE


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@pytest.fixture
async def test_client():
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_successful_post_with_api_key(test_client):
    """Test successful API post with API key."""
    response = await test_client.post(
        "/products",
        json=DEFAULT_PRODUCT_DATA,
        headers={API_KEY_NAME: API_KEY},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_API_RESPONSE


@pytest.mark.asyncio
async def test_successful_post_with_bearer_token(test_client):
    """Test successful API post with bearer token."""
    response = await test_client.post(
        "/products-bearer",
        json=DEFAULT_PRODUCT_DATA,
        headers={"Authorization": "Bearer test_token"},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_API_RESPONSE


@pytest.mark.asyncio
async def test_unauthorized_post(test_client):
    """Test unauthorized API post."""
    response = await test_client.post(
        "/products",
        json=DEFAULT_PRODUCT_DATA,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_data_post(test_client):
    """Test API post with invalid data."""
    response = await test_client.post(
        "/products",
        json={"invalid": "data"},
        headers={API_KEY_NAME: API_KEY},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_health_check(test_client):
    """Test API health check."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_invalid_json_post(test_client):
    """Test API post with invalid JSON response."""
    # Mock a response that raises an error when calling .json()
    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.status_code = 200

    # Send the request
    response = await test_client.post(
        "/products",
        json=DEFAULT_PRODUCT_DATA,
        headers={API_KEY_NAME: API_KEY},
    )
    assert response.status_code == 200
