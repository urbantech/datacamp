from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict

class ProductSchema(BaseModel):
    """Schema for product data validation."""
    
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        str_max_length=1000,
        validate_default=True,
        json_schema_extra={
            'examples': [{
                'title': 'Example Product',
                'price': 99.99,
                'currency': 'USD',
                'images': ['https://example.com/image.jpg'],
                'category': 'Electronics',
                'description': 'An example product description',
                'source_url': 'https://example.com/product'
            }]
        }
    )
    # Required fields
    title: str = Field(..., min_length=1, description="Product title")
    price: float = Field(..., gt=0, description="Product price")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD)")
    images: List[HttpUrl] = Field(..., min_length=1, description="List of product image URLs")
    category: str = Field(..., min_length=1, description="Product category")
    description: str = Field(..., min_length=1, description="Full product description")
    source_url: HttpUrl = Field(..., description="Original product URL")
    
    # Optional fields
    sku: Optional[str] = Field(None, pattern=r'^[A-Za-z0-9-]+$', description="Product SKU (optional)")
    brand: Optional[str] = Field(None, min_length=1, description="Product brand (optional)")
    availability: bool = Field(default=True, description="Product availability status")
    variants: List[str] = Field(default_factory=list, description="List of product variants")
