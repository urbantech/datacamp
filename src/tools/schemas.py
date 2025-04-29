"""Data validation schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ProductSchema(BaseModel):
    """Schema for validating product data.

    This schema defines both required and optional fields for a product.
    Required fields must be present and valid, while optional fields will
    be validated only if present.

    Required Fields:
        title (str): Product title
        price (float): Product price (must be > 0)
        currency (str): Currency code (e.g., USD)
        images (List[HttpUrl]): List of product image URLs
        category (str): Product category
        description (str): Product description
        source_url (HttpUrl): Original product URL

    Optional Fields:
        sku (str): Stock Keeping Unit
        brand (str): Product brand
        availability (bool): Product availability status
        variants (List[str]): List of product variants
    """

    # Required fields
    title: str = Field(
        ..., min_length=1, description="Product title"
    )
    price: float = Field(
        ..., gt=0, description="Product price"
    )
    currency: str = Field(
        ..., min_length=3, max_length=3, description="Currency code (e.g., USD)"
    )
    images: List[HttpUrl] = Field(
        ..., min_length=1, description="Product images"
    )
    category: str = Field(
        ..., min_length=1, description="Product category"
    )
    description: str = Field(
        ..., min_length=1, description="Description"
    )
    source_url: HttpUrl = Field(
        ..., description="Original product URL"
    )

    # Optional fields
    sku: Optional[str] = Field(
        None, pattern=r"^[A-Za-z0-9-]+$", description="SKU"
    )
    brand: Optional[str] = Field(None, min_length=1, description="Brand")
    availability: bool = Field(default=True, description="Product availability status")
    variants: List[str] = Field(
        default_factory=list, description="Product variants"
    )
