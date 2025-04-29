from typing import Dict, Any, Optional
from pydantic import ValidationError
from .schemas import ProductSchema

class ValidatorTool:
    """Tool for validating product data against defined schemas."""

    def __init__(self):
        self.schema = ProductSchema

    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate product data against the schema.

        Args:
            data: Dictionary containing product data to validate

        Returns:
            tuple containing:
            - bool: True if validation successful, False otherwise
            - Dict[str, Any] | None: Validated data if successful, None if failed
            - str | None: Error message if validation failed, None if successful
        """
        try:
            validated_data = self.schema(**data)
            return True, validated_data.model_dump(exclude_none=True, exclude_defaults=False), None
        except ValidationError as e:
            error_msg = self._format_validation_error(e)
            return False, None, error_msg

    def _format_validation_error(self, error: ValidationError) -> str:
        """Format validation error into a readable message."""
        errors = []
        for err in error.errors():
            location = " -> ".join(str(loc) for loc in err["loc"])
            message = err["msg"]
            errors.append(f"{location}: {message}")
        return "\n".join(errors)
