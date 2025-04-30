"""Shein product scraper implementation."""

import json
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class SheinScraper(BaseScraper):
    """Scraper for Shein product pages."""

    def get_domain(self) -> str:
        """Get Shein domain name.

        Returns:
            str: Domain name
        """
        return "shein.com"

    def extract_title(self, content: Dict[str, Any]) -> str:
        """Extract product title.

        Args:
            content: Page content dictionary

        Returns:
            str: Product title
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        title_elem = soup.select_one("h1.product-intro__head-name")
        return str(title_elem.text.strip()) if title_elem else ""

    def extract_price(self, content: Dict[str, Any]) -> str:
        """Extract product price.

        Args:
            content: Page content dictionary

        Returns:
            str: Product price
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        price_elem = soup.select_one(".product-intro__head-price .from")
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
        # Shein US site always uses USD
        return "USD"

    def extract_images(self, content: Dict[str, Any]) -> List[str]:
        """Extract product image URLs.

        Args:
            content: Page content dictionary

        Returns:
            List[str]: List of image URLs
        """
        soup = BeautifulSoup(content["html"], "html.parser")

        # Try to find image data in JSON-LD
        script = soup.find("script", {"type": "application/ld+json"})
        if script:
            try:
                data = json.loads(script.string)
                if "image" in data:
                    if isinstance(data["image"], list):
                        return [str(img) for img in data["image"]]
                    return [str(data["image"])]
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback to scraping image elements
        images = []
        for img in soup.select(".product-intro__thumbs-item img"):
            src = img.get("src") or img.get("data-src")
            if src:
                # Convert thumbnail URLs to full-size
                src = src.replace("_thumbnail_", "_")
                images.append(str(src))

        if not images:
            raise ValueError("Could not find product images")
        return images

    def extract_category(self, content: Dict[str, Any]) -> str:
        """Extract product category.

        Args:
            content: Page content dictionary

        Returns:
            str: Product category
        """
        soup = BeautifulSoup(content["html"], "html.parser")
        breadcrumbs = soup.select(".j-bread-crumb a")
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
        desc_elem = soup.select_one(".product-intro__description")
        return str(desc_elem.text.strip()) if desc_elem else ""
