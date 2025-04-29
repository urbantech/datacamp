"""Tool for posting validated product data to an API endpoint."""

from typing import Dict, Any, Optional, Tuple
import requests
from .schemas import ProductSchema
from .validator_tool import ValidatorTool


class APIPosterTool:
    """Tool for posting validated product data to an API endpoint."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the API poster tool.

        Args:
            api_url: The URL of the API endpoint
            api_key: Optional API key for authentication
            bearer_token: Optional bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
        self.headers = {}
        self.validator = ValidatorTool(ProductSchema)
        self._session = requests.Session()

        if api_key:
            self.set_api_key(api_key)
        if bearer_token:
            self.set_bearer_token(bearer_token)

    def set_api_key(self, api_key: str) -> None:
        """Set the API key for authentication.

        Args:
            api_key: The API key to use
        """
        self.headers["X-API-Key"] = api_key

    def set_bearer_token(self, token: str) -> None:
        """Set the bearer token for authentication.

        Args:
            token: The bearer token to use
        """
        self.headers["Authorization"] = f"Bearer {token}"

    def update_headers(self, headers: Dict[str, str]) -> None:
        """Update request headers.

        Args:
            headers: Dictionary of headers to update
        """
        self.headers.update(headers)

    def post_data(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Post data to the API endpoint.

        Args:
            data: Dictionary containing product data

        Returns:
            Tuple containing:
            - Success flag (bool)
            - Response data if successful (Dict or None)
            - Error message if failed (str or None)
        """
        # Validate data
        is_valid, validated_data, error = self.validator.validate(data)
        if not is_valid:
            return False, None, f"Validation failed: {error}"

        # Make API request
        try:
            response = self._session.post(
                url=self.api_url,
                json=validated_data,
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 401:
                return False, None, "Authentication required"
            response.raise_for_status()
            return True, response.json(), None

        except requests.exceptions.RequestException as e:
            return False, None, f"API request failed: {str(e)}"

    def health_check(self) -> bool:
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
            response = self._session.get(
                url=health_url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("status") == "healthy"
        except requests.exceptions.RequestException:
            return False
