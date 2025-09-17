"""
IndexForSearchProcessor for Cyoda Client Application

Indexes HN item content for search functionality as specified in workflow requirements.
"""

import logging
import re
from typing import Any

from application.entity.hnitem.version_1.hnitem import HNItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class IndexForSearchProcessor(CyodaProcessor):
    """
    Processor for indexing HNItem content for search functionality.

    Extracts searchable content, creates search indices, and updates search database.
    """

    def __init__(self) -> None:
        super().__init__(
            name="index_for_search",
            description="Indexes item content for search functionality",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Index the HNItem for search according to functional requirements.

        Args:
            entity: The HNItem to index
            **kwargs: Additional processing parameters

        Returns:
            The entity with search indexing status
        """
        try:
            self.logger.info(
                f"Indexing HNItem {getattr(entity, 'technical_id', '<unknown>')} for search"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Extract searchable content
            search_content_parts = []

            # Add title if present
            if hn_item.title:
                clean_title = self._clean_html(hn_item.title)
                search_content_parts.append(clean_title)

            # Add text content if present
            if hn_item.text:
                clean_text = self._clean_html(hn_item.text)
                search_content_parts.append(clean_text)

            # Add URL domain if present
            if hn_item.url:
                domain = self._extract_domain(hn_item.url)
                if domain:
                    search_content_parts.append(domain)

            # Add author if present
            if hn_item.by:
                search_content_parts.append(hn_item.by)

            # Combine all searchable content
            search_content = " ".join(search_content_parts).strip()

            # Set search content
            hn_item.set_search_content(search_content)

            # Mark as indexed
            hn_item.set_indexed()

            # Add indexing metadata
            if not hn_item.metadata:
                hn_item.metadata = {}
            hn_item.metadata["search_indexed"] = True
            hn_item.metadata["search_content_length"] = len(search_content)
            hn_item.metadata["indexing_timestamp"] = hn_item.indexed_at

            # Create search keywords for better matching
            keywords = self._extract_keywords(search_content)
            hn_item.metadata["search_keywords"] = keywords

            self.logger.info(
                f"HNItem {hn_item.technical_id} indexed successfully. "
                f"Content length: {len(search_content)}, Keywords: {len(keywords)}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error indexing HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean up content for search indexing"""
        if not html_content:
            return ""

        # Remove HTML tags
        clean_text = re.sub(r"<[^>]+>", "", html_content)

        # Decode common HTML entities
        clean_text = clean_text.replace("&amp;", "&")
        clean_text = clean_text.replace("&lt;", "<")
        clean_text = clean_text.replace("&gt;", ">")
        clean_text = clean_text.replace("&quot;", '"')
        clean_text = clean_text.replace("&#x27;", "'")
        clean_text = clean_text.replace("&#x2F;", "/")

        # Normalize whitespace
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return clean_text

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for search indexing"""
        if not url:
            return ""

        # Simple domain extraction
        try:
            # Remove protocol
            domain = url.replace("http://", "").replace("https://", "")
            # Remove path and query parameters
            domain = domain.split("/")[0]
            # Remove www prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def _extract_keywords(self, content: str) -> list[str]:
        """Extract keywords from content for search indexing"""
        if not content:
            return []

        # Convert to lowercase and split into words
        words = re.findall(r"\b\w+\b", content.lower())

        # Filter out common stop words and short words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)

        # Limit to top 50 keywords
        return unique_keywords[:50]
