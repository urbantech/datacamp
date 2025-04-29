"""ValidatorTool for validating product data using Pydantic schema."""

from typing import Dict, Optional, Tuple, Any
from pydantic import ValidationError
from .schemas import ProductSchema


class ValidatorTool:
    """Tool for validating product data against the schema."""

    def __init__(self):
        """Initialize the validator with ProductSchema."""
        self.schema = ProductSchema

    def _format_validation_error(self, error: ValidationError) -> str:
        """Format validation error into a readable message.

        Args:
            error: The validation error from Pydantic

        Returns:
            Formatted error message string
        """
        messages = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            msg = err["msg"]
            messages.append(f"{field}: {msg}")
        return "; ".join(messages)

    def validate(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate product data against the schema.

        Args:
            data: Product data to validate

        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        try:
            validated_data = self.schema(**data)
            return (
                True,
                validated_data.model_dump(exclude_none=True, exclude_defaults=False),
                None,
            )
        except ValidationError as e:
            error_msg = self._format_validation_error(e)
            return False, None, error_msg
