"""Data models for extracted entities."""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Book:
    """Represent structured information for a scraped book product.

    Attributes:
        title: The full title of the book.
        price: The displayed price string (e.g. '£51.77').
        availability: Stock status (e.g. 'In stock').
        url: Absolute URL to the product detail page.
        rating: Integer star rating from 1 to 5 if available (or None).
    """

    title: str
    price: str
    availability: str
    url: str
    rating: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance into a standard dictionary.

        Returns:
            Dictionary mapping attribute names to values.
        """
        return asdict(self)
