"""APIPosterTool for sending validated product data to API endpoints."""

from typing import Dict, Optional, Tuple, Any
import requests
from .validator_tool import ValidatorTool


class APIPosterTool:
    """Tool for posting validated product data to API endpoints."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ):
        """Initialize the APIPosterTool.

        Args:
            api_url: The base URL for the API endpoint
            api_key: Optional API key for authentication
            bearer_token: Optional bearer token for authentication
            custom_headers: Optional custom headers to include
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.headers = self._build_headers(api_key, bearer_token, custom_headers)
        self.validator = ValidatorTool()

    def _build_headers(
        self,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Build request headers with authentication.

        Args:
            api_key: Optional API key for authentication
            bearer_token: Optional bearer token for authentication
            custom_headers: Optional custom headers to include

        Returns:
            Dict of headers to use in requests
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if api_key:
            headers["X-API-Key"] = api_key

        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        if custom_headers:
            headers.update(custom_headers)

        return headers

    def post_data(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Post validated data to the API endpoint.

        Args:
            data: Product data to validate and post

        Returns:
            Tuple of (success, response_data, error_message)
        """
        # Validate data first
        is_valid, validated_data, error = self.validator.validate(data)
        if not is_valid:
            return False, None, f"Validation failed: {error}"

        try:
            response = requests.post(
                url=self.api_url,
                json=validated_data,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True, response.json(), None

        except requests.exceptions.RequestException as e:
            error_msg = "API request failed"
            if hasattr(e, "response") and e.response:
                try:
                    error_data = e.response.json()
                    if isinstance(error_data, dict) and "message" in error_data:
                        error_msg = error_data["message"]
                except (ValueError, AttributeError):
                    error_msg = str(e)
            return False, None, error_msg

    def health_check(self) -> bool:
        """Check if the API endpoint is accessible.

        Returns:
            True if the API is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/health", headers=self.headers, timeout=self.timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def update_auth(
        self,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Update authentication credentials.

        Args:
            api_key: New API key
            bearer_token: New bearer token
            custom_headers: New custom headers
        """
        self.headers = self._build_headers(api_key, bearer_token, custom_headers)
