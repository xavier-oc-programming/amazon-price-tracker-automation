import re
import requests
from bs4 import BeautifulSoup

from config import PRODUCT_URL, BROWSER_HEADERS, PRICE_CSS_CLASS


class AmazonScraper:
    """Fetches an Amazon product page and extracts the current price."""

    def __init__(self, url: str = PRODUCT_URL, headers: dict = BROWSER_HEADERS):
        self._url = url
        self._headers = headers

    def get_price(self) -> float:
        """
        Fetch the product page and return the current price as a float.

        Returns:
            float: current price in USD.

        Raises:
            requests.HTTPError: if the page request fails.
            ValueError: if the price element or a valid price string is not found.
        """
        response = requests.get(self._url, headers=self._headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.find("span", class_=PRICE_CSS_CLASS)

        if price_tag is None:
            raise ValueError("Could not find price element on the page.")

        return self._parse_price(price_tag.get_text().strip())

    @staticmethod
    def _parse_price(text: str) -> float:
        """
        Extract and normalise a price string into a float.

        Handles both EU (€, comma-decimal) and US ($, dot-decimal) formats:
            "$1,299.99"  → 1299.99
            "€59,99"     → 59.99
            "€1.299,99"  → 1299.99

        Args:
            text: raw string containing the price.

        Returns:
            float: normalised price.

        Raises:
            ValueError: if no valid price pattern is found.
        """
        pattern = r"[€£$]\s?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}"
        match = re.search(pattern, text)

        if not match:
            raise ValueError(f"No valid price found in: {text!r}")

        raw = match.group().replace("€", "").replace("$", "").replace("£", "").replace(" ", "")

        if "," in raw and "." in raw:
            raw = raw.replace(".", "").replace(",", ".")
        elif "," in raw:
            raw = raw.replace(",", ".")
        else:
            raw = raw.replace(",", "")

        return float(raw)
