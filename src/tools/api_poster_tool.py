"""API Poster Tool for sending data to endpoints."""

import json
from typing import Any, Dict, Optional, Tuple

import httpx
from httpx import HTTPStatusError, RequestError

from .schemas import ProductSchema
from .validator_tool import ValidatorTool


class APIPosterTool:
    """Tool for posting data to API endpoints."""

    def __init__(
        self,
        api_url: str,
        validator=None,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the API poster tool.

        Args:
            api_url: Base URL for the API
            validator: Optional validator for data
            api_key: Optional API key for authentication
            bearer_token: Optional bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.validator = (
            validator if validator else ValidatorTool(ProductSchema)
        )
        self._session = httpx.AsyncClient()
        self.headers: Dict[str, str] = {}
        self.timeout = timeout

        if api_key:
            self.headers["X-API-Key"] = api_key
        if bearer_token:
            self.headers["Authorization"] = f"Bearer {bearer_token}"

    async def set_api_key(self, api_key: str) -> None:
        """Set the API key for authentication.

        Args:
            api_key: The API key to use
        """
        self.headers["X-API-Key"] = api_key

    async def set_bearer_token(self, token: str) -> None:
        """Set the bearer token for authentication.

        Args:
            token: The bearer token to use
        """
        self.headers["Authorization"] = f"Bearer {token}"

    async def update_headers(self, headers: Dict[str, str]) -> None:
        """Update request headers.

        Args:
            headers: Dictionary of headers to update
        """
        self.headers.update(headers)

    async def post_data(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Post data to the API endpoint.

        Args:
            data: Dictionary containing data to post

        Returns:
            Tuple containing:
            - Success flag (bool)
            - Response data if successful (Dict or None)
            - Error message if failed (str or None)
        """
        if self.validator:
            is_valid, validated_data, error = self.validator.validate(data)
            if not is_valid:
                return False, None, f"Validation failed: {error}"
            data = validated_data

        try:
            response = await self._session.post(
                self.api_url,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True, response.json(), None
        except HTTPStatusError as e:
            if hasattr(e.response, "json"):
                try:
                    error_data = e.response.json()
                    return False, None, str(error_data)
                except json.JSONDecodeError:
                    pass
            return False, None, str(e)
        except RequestError as e:
            return False, None, str(e)

    async def health_check(self) -> bool:
        """Check if the API endpoint is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Extract base URL by removing endpoint path
            base_url = str(self.api_url)
            if base_url.endswith("/products"):
                base_url = base_url[:-9]  # Remove /products
            elif base_url.endswith("/products/"):
                base_url = base_url[:-10]  # Remove /products/
            health_url = f"{base_url}/health"
            response = await self._session.get(
                url=health_url, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def cleanup(self):
        """Clean up resources by closing the HTTP session."""
        await self._session.aclose()
