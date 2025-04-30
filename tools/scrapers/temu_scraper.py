"""Temu product scraper implementation."""

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class TemuScraper(BaseScraper):
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
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        title_elem = soup.select_one("h1.DetailName_title")
        return str(title_elem.text.strip()) if title_elem else ""

    def extract_price(self, content: Dict[str, Any]) -> str:
        """Extract product price.

        Args:
            content: Page content dictionary

        Returns:
            str: Product price
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        price_elem = soup.select_one(".DetailPrice_price")
        return (
            str(price_elem.text.strip().replace("$", "").replace(",", ""))
            if price_elem
            else ""
        )

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
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        image_elements = soup.select(".product-image img")
        return [img["src"] for img in image_elements if "src" in img.attrs]

    def extract_category(self, content: Dict[str, Any]) -> str:
        """Extract product category.

        Args:
            content: Page content dictionary

        Returns:
            str: Product category
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        breadcrumbs = soup.select(".DetailBreadcrumb_item")
        if not breadcrumbs:
            raise ValueError("Could not find product category")
        # Use the last breadcrumb as the category
        return str(breadcrumbs[-1].text.strip())

    def extract_description(self, content: Dict[str, Any]) -> str:
        """Extract product description.

        Args:
            content: Page content dictionary

        Returns:
            str: Product description
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        desc_elem = soup.select_one(".DetailDescription_content")
        return str(desc_elem.text.strip()) if desc_elem else ""
