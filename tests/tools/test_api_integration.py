"""Integration tests for the APIPosterTool with a mock API server."""

import json
from typing import Dict, Any, Generator
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from src.tools.api_poster_tool import APIPosterTool


@pytest.fixture
def mock_api() -> Generator[FastAPI, None, None]:
    """Create a mock FastAPI server for testing."""
    app = FastAPI()

    @app.post("/products")
    async def create_product(request: Request) -> JSONResponse:
        """Handle product creation requests."""
        try:
            data = await request.json()
            auth_header = request.headers.get("Authorization")
            api_key = request.headers.get("X-API-Key")

            # Check authentication
            if not auth_header and not api_key:
                raise HTTPException(
                    status_code=401, detail="Authentication required"
                )

            # Validate required fields
            required_fields = [
                "title",
                "price",
                "currency",
                "images",
                "category",
                "description",
                "source_url",
            ]
            for field in required_fields:
                if field not in data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}",
                    )

            # Simulate successful creation
            return JSONResponse(
                status_code=201,
                content={
                    "id": "123",
                    "status": "created",
                    "data": data,
                },
            )

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid JSON payload"
            )

    @app.get("/health")
    async def health_check() -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "healthy"})

    yield app


@pytest.fixture
def mock_api_client(mock_api: FastAPI) -> TestClient:
    """Create a TestClient for the mock API."""
    return TestClient(mock_api)


@pytest.fixture
def valid_product_data() -> Dict[str, Any]:
    """Provide valid test product data."""
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


def test_successful_post_with_api_key(
    mock_api_client: TestClient, valid_product_data: Dict[str, Any]
) -> None:
    """Test successful product creation with API key auth."""
    poster = APIPosterTool(api_url="http://test/products", api_key="test-key")
    poster._session = mock_api_client

    success, response, error = poster.post_data(valid_product_data)

    assert success is True
    assert response is not None
    assert response["status"] == "created"
    assert response["data"] == valid_product_data
    assert error is None


def test_successful_post_with_bearer_token(
    mock_api_client: TestClient, valid_product_data: Dict[str, Any]
) -> None:
    """Test successful product creation with bearer token auth."""
    poster = APIPosterTool(api_url="http://test/products", bearer_token="test-token")
    poster._session = mock_api_client

    success, response, error = poster.post_data(valid_product_data)

    assert success is True
    assert response is not None
    assert response["status"] == "created"
    assert response["data"] == valid_product_data
    assert error is None


def test_unauthorized_post(
    mock_api_client: TestClient, valid_product_data: Dict[str, Any]
) -> None:
    """Test posting without authentication."""
    poster = APIPosterTool(api_url="http://test/products")
    poster._session = mock_api_client

    success, response, error = poster.post_data(valid_product_data)

    assert success is False
    assert response is None
    assert "Authentication required" in str(error)


def test_invalid_data_post(mock_api_client: TestClient) -> None:
    """Test posting invalid product data."""
    poster = APIPosterTool(api_url="http://test/products", api_key="test-key")
    poster._session = mock_api_client

    invalid_data = {
        "title": "",  # Invalid: empty title
        "price": -10,  # Invalid: negative price
    }

    success, response, error = poster.post_data(invalid_data)

    assert success is False
    assert response is None
    assert "Validation failed" in str(error)


def test_health_check(mock_api_client: TestClient) -> None:
    """Test health check endpoint."""
    poster = APIPosterTool(api_url="http://test", api_key="test-key")
    poster._session = mock_api_client

    assert poster.health_check() is True


def test_invalid_json_post(
    mock_api_client: TestClient, valid_product_data: Dict[str, Any]
) -> None:
    """Test handling of invalid JSON responses."""
    poster = APIPosterTool(api_url="http://test/products", api_key="test-key")
    poster._session = mock_api_client

    # Modify the data to make it invalid JSON
    data = valid_product_data.copy()
    data["images"] = object()  # This will cause JSON serialization to fail

    success, response, error = poster.post_data(data)

    assert success is False
    assert response is None
    assert "Validation failed" in str(error)
