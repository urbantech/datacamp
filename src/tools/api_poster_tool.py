from typing import Dict, Any, Optional, Tuple
import requests
from requests.exceptions import RequestException
from .validator_tool import ValidatorTool

class APIPosterTool:
    """Tool for sending validated product data to an API endpoint."""

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize the APIPosterTool.

        Args:
            api_url: The URL of the API endpoint
            api_key: Optional API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.validator = ValidatorTool()

    def post_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate and post data to the API endpoint.

        Args:
            data: Dictionary containing product data to validate and post

        Returns:
            tuple containing:
            - bool: True if post successful, False otherwise
            - Dict[str, Any] | None: Response data if successful, None if failed
            - str | None: Error message if failed, None if successful
        """
        # First validate the data
        is_valid, validated_data, error = self.validator.validate(data)
        if not is_valid:
            return False, None, f"Validation failed: {error}"

        # Prepare headers
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        try:
            # Send POST request
            response = requests.post(
                self.api_url,
                json=validated_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return True, response.json(), None

        except RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, 'json'):
                try:
                    error_msg = e.response.json().get('message', str(e))
                except ValueError:
                    pass
            return False, None, f"API request failed: {error_msg}"

    def health_check(self) -> bool:
        """Check if the API endpoint is accessible."""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else None,
                timeout=5
            )
            return response.status_code == 200
        except RequestException:
            return False
