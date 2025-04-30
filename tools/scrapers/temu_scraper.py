"""TemuScraper - Extracts product data from Temu product pages.

This scraper implements the ToolInterface and is responsible for parsing Temu
HTML and extracting required product data fields.
"""

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..api_poster_tool import ToolInterface
from .base_scraper import BaseScraper


class TemuScraperTool(ToolInterface, BaseScraper):
    """Temu product scraper tool.

    This tool extracts product data from Temu product pages.
    """

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the scraper tool with the provided input data.

        Args:
            input_data: Dictionary containing:
                - url: URL of the Temu product page
                - html_content: Optional HTML content if already fetched

        Returns:
            Dict[str, Any]: Extracted product data
        """
        import asyncio

        # Use the input_data directly for async implementation
        return asyncio.run(self._async_run(input_data))

    async def _async_run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the scraper tool with the provided input data.

        Args:
            input_data: Dictionary containing:
                - url: URL of the Temu product page
                - html_content: Optional HTML content if already fetched

        Returns:
            Dict[str, Any]: Extracted product data
        """
        if "html_content" in input_data:
            content = {"html": input_data["html_content"]}
        else:
            content = await self.crawler.fetch(input_data["url"])

        # Extract data from content
        result = {
            "title": self.extract_title(content),
            "price": self.extract_price(content),
            "currency": self.extract_currency(content),
            "images": self.extract_images(content),
            "description": self.extract_description(content),
            "specifications": self.extract_specifications(content),
            "size_info": self.extract_size_info(content),
            "color_options": self.extract_color_options(content),
            "reviews_summary": self.extract_reviews_summary(content),
            "source_url": input_data["url"],
            # Include url field for backward compatibility
            "url": input_data["url"],
        }

        # Add category if available (needed for some tests)
        try:
            result["category"] = self.extract_category(content)
        except ValueError:
            # Category is optional, so don't fail if it's not found
            pass

        return result

    """Scraper for Temu product pages."""

    def get_domain(self) -> str:
        """Get Temu domain name.

        Returns:
            str: Domain name
        """
        return "temu.com"

    def extract_title(self, content: Dict[str, Any]) -> str:
        """Extract product title.

        Args:
            content: Page content dictionary

        Returns:
            str: Product title

        Raises:
            ValueError: If title element is not found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        title_elem = soup.select_one("h1.DetailName_title")
        if not title_elem:
            raise ValueError("Could not find product title")
        return str(title_elem.text.strip())

    def extract_price(self, content: Dict[str, Any]) -> str:
        """Extract product price.

        Args:
            content: Page content dictionary

        Returns:
            str: Product price as a string

        Raises:
            ValueError: If price element is not found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        price_elem = soup.select_one(".DetailPrice_price")
        if not price_elem:
            raise ValueError("Could not find product price")

        price_text = price_elem.text.strip().replace("$", "").replace(",", "")
        try:
            # Validate that it's a valid number but return as string
            float(price_text)
            return str(price_text)
        except ValueError:
            raise ValueError(f"Invalid price format: {price_text}")

    def extract_currency(self, content: Dict[str, Any]) -> str:
        """Extract price currency.

        Args:
            content: Page content dictionary

        Returns:
            str: Currency code
        """
        # Temu US site always uses USD
        return "USD"

    def extract_images(self, content: Dict[str, Any]) -> List[str]:
        """Extract product images.

        Args:
            content: Page content

        Returns:
            List[str]: List of image URLs

        Raises:
            ValueError: If no image elements are found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        image_elements = soup.select(".product-image img")
        if not image_elements:
            raise ValueError("Could not find product images")
        return [img["src"] for img in image_elements if "src" in img.attrs]

    def extract_category(self, content: Dict[str, Any]) -> str:
        """Extract product category.

        Args:
            content: Page content dictionary

        Returns:
            str: Product category

        Raises:
            ValueError: If category element is not found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        breadcrumb = soup.select(".DetailBreadcrumb_item")
        if not breadcrumb:
            raise ValueError("Could not find product category")
        # Return the last breadcrumb item as the category
        return str(breadcrumb[-1].text.strip())

    def extract_description(self, content: Dict[str, Any]) -> str:
        """Extract product description.

        Args:
            content: Page content dictionary

        Returns:
            str: Product description

        Raises:
            ValueError: If description element is not found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        description_elem = soup.select_one(".DetailDescription_content")
        if not description_elem:
            raise ValueError("Could not find product description")
        return str(description_elem.text.strip())

    def extract_specifications(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Extract product specifications.

        Args:
            content: Page content

        Returns:
            Dict[str, str]: Dictionary of specifications

        Raises:
            ValueError: If no specification elements are found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        specs = {}

        # Extract specifications from the product page
        spec_elements = soup.select(".DetailSpecs_item")
        if not spec_elements:
            raise ValueError("Could not find product specifications")

        for spec in spec_elements:
            label = spec.select_one(".DetailSpecs_label")
            value = spec.select_one(".DetailSpecs_value")
            if label and value:
                specs[label.text.strip()] = value.text.strip()

        return specs

    def extract_size_info(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Extract product size information.

        Args:
            content: Page content dictionary

        Returns:
            Dict[str, str]: Dictionary of size information

        Raises:
            ValueError: If no size elements are found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        size_elements = soup.select(".DetailSize_item")
        if not size_elements:
            raise ValueError("Could not find product sizes")

        sizes = {}
        for i, size_elem in enumerate(size_elements):
            size_value = size_elem.text.strip()
            sizes[size_value] = f"Size option {i+1}"
        return sizes

    def extract_color_options(self, content: Dict[str, Any]) -> List[str]:
        """Extract product color options.

        Args:
            content: Page content dictionary

        Returns:
            List[str]: Available colors

        Raises:
            ValueError: If no color elements are found
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        color_elements = soup.select(".DetailColor_item")
        if not color_elements:
            raise ValueError("Could not find product colors")

        colors = []
        for color in color_elements:
            value = color.select_one(".DetailColor_value")
            if value:
                colors.append(value.text.strip())

        return colors

    def extract_reviews_summary(
        self, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract product reviews summary.

        Args:
            content: Page content

        Returns:
            Dict[str, Any]: Reviews summary with rating and review count

        Raises:
            ValueError: If no reviews elements are found
        """
        soup = BeautifulSoup(content["html"], "html.parser")

        # Extract reviews summary from the product page
        reviews_elem = soup.select_one(".DetailReviews_summary")
        if not reviews_elem:
            raise ValueError("Could not find reviews summary")

        rating_elem = reviews_elem.select_one(".DetailReviews_rating")
        count_elem = reviews_elem.select_one(".DetailReviews_count")

        if not rating_elem or not count_elem:
            raise ValueError("Could not find rating or review count")

        try:
            rating = float(rating_elem.text.strip())
            count = int(count_elem.text.strip().split()[0])
            return {"rating": rating, "review_count": count}
        except (ValueError, TypeError):
            raise ValueError("Invalid reviews summary format")
