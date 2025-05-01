"""Base scraper class for e-commerce sites."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from tools.playwright_crawler.tool import PlaywrightCrawlerTool


class BaseScraper(ABC):
    """Base scraper class for e-commerce sites.

    This class provides common functionality for scraping product data
    from e-commerce sites. Site-specific scrapers should inherit from this
    class and implement the abstract methods.

    Attributes:
        crawler: PlaywrightCrawlerTool instance for web scraping
        domain: Domain name of the e-commerce site
    """

    def __init__(self, crawler: Optional[PlaywrightCrawlerTool] = None):
        """Initialize the scraper.

        Args:
            crawler: Optional PlaywrightCrawlerTool instance. If not provided,
                   a new instance will be created.
        """
        self.crawler = crawler or PlaywrightCrawlerTool()
        self.domain = self.get_domain()

    @abstractmethod
    def get_domain(self) -> str:
        """Get the domain name for this scraper.

        Returns:
            str: Domain name (e.g., 'shein.com')
        """
        pass

    @abstractmethod
    def extract_title(self, content: Dict[str, Any]) -> str:
        """Extract product title from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            str: Product title
        """
        pass

    @abstractmethod
    def extract_price(self, content: Dict[str, Any]) -> str:
        """Extract product price.

        Args:
            content: Page content

        Returns:
            str: Product price
        """
        pass

    @abstractmethod
    def extract_currency(self, content: Dict[str, Any]) -> str:
        """Extract price currency from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            str: Currency code (e.g., 'USD')
        """
        pass

    @abstractmethod
    def extract_images(self, content: Dict[str, Any]) -> List[str]:
        """Extract product image URLs from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            List[str]: List of image URLs
        """
        pass

    @abstractmethod
    def extract_category(self, content: Dict[str, Any]) -> str:
        """Extract product category from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            str: Product category
        """
        pass

    @abstractmethod
    def extract_description(self, content: Dict[str, Any]) -> str:
        """Extract product description from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            str: Product description
        """
        pass

    @abstractmethod
    def extract_specifications(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Extract product specifications from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            Dict[str, str]: Product specifications
        """
        pass

    @abstractmethod
    def extract_size_info(self, content: Dict[str, Any]) -> Dict[str, str]:
        """Extract product size information from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            Dict[str, str]: Product size information
        """
        pass

    @abstractmethod
    def extract_color_options(self, content: Dict[str, Any]) -> List[str]:
        """Extract product color options from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            List[str]: Product color options
        """
        pass

    @abstractmethod
    def extract_reviews_summary(
        self, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract product reviews summary from page content.

        Args:
            content: Dictionary containing page content and metadata

        Returns:
            Dict[str, Any]: Product reviews summary
        """
        pass

    def can_handle_url(self, url: str) -> bool:
        """Check if this scraper can handle the given URL.

        Args:
            url: URL to check

        Returns:
            bool: True if this scraper can handle the URL
        """
        # Fix line length issue
        return self.get_domain() in url

    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product data from URL.

        Args:
            url: Product URL

        Returns:
            Dict[str, Any]: Product data
        """
        content = await self.crawler.fetch(url)
        if not content:
            return {}

        return {
            "title": self.extract_title(content),
            "price": self.extract_price(content),
            "currency": self.extract_currency(content),
            "images": self.extract_images(content),
            "category": self.extract_category(content),
            "description": self.extract_description(content),
            "specifications": self.extract_specifications(content),
            "size_info": self.extract_size_info(content),
            "color_options": self.extract_color_options(content),
            "reviews_summary": self.extract_reviews_summary(content),
            "source_url": url,
            "url": url,
        }

    async def cleanup(self):
        """Clean up resources."""
        await self.crawler.cleanup()
