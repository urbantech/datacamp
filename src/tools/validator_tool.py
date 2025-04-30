"""Tool for validating data against a schema."""

from typing import Any, Dict, Optional, Tuple, Type

from pydantic import BaseModel, ValidationError


class ValidatorTool:
    """Tool for validating data against a schema."""

    def __init__(self, schema: Type[BaseModel]) -> None:
        """Initialize the validator tool.

        Args:
            schema: Pydantic model class to use for validation
        """
        self.schema = schema

    def validate(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate data against the schema.

        Args:
            data: Dictionary containing data to validate

        Returns:
            Tuple containing:
            - Success flag (bool)
            - Validated data if successful (Dict or None)
            - Error message if validation failed (str or None)
        """
        try:
            validated = self.schema(**data)
            # Convert to dict and ensure URLs are strings
            validated_dict = validated.model_dump(exclude_none=True)
            if "images" in validated_dict:
                validated_dict["images"] = [
                    str(url) for url in validated_dict["images"]
                ]
            if "source_url" in validated_dict:
                validated_dict["source_url"] = str(validated_dict["source_url"])
            return True, validated_dict, None
        except ValidationError as e:
            return False, None, str(e)
