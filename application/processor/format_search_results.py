"""
FormatSearchResults Processor for SearchQuery

Formats search results for API response with proper structure,
metadata, and hierarchy information.
"""

import logging
from typing import Any, Dict, List

from application.entity.searchquery.version_1.searchquery import SearchQuery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class FormatSearchResults(CyodaProcessor):
    """
    Processor for formatting SearchQuery results for API response.
    Adds metadata, hierarchy information, and proper structure.
    """

    def __init__(self) -> None:
        super().__init__(
            name="format_search_results",
            description="Formats SearchQuery results for API response",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Format the search results for API response.

        Args:
            entity: The SearchQuery with raw results to format
            **kwargs: Additional processing parameters

        Returns:
            The query with formatted results
        """
        try:
            self.logger.info(
                f"Formatting search results for SearchQuery {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to SearchQuery for type-safe operations
            search_query = cast_entity(entity, SearchQuery)

            if not search_query.results:
                self.logger.info(
                    f"No results to format for SearchQuery {search_query.technical_id}"
                )
                return search_query

            # Format each result
            formatted_results = []
            for result in search_query.results:
                formatted_result = self._format_single_result(result, search_query)
                formatted_results.append(formatted_result)

            # Update results with formatted data
            search_query.results = formatted_results

            # Add search metadata
            search_query.search_index_used = self._determine_search_index(search_query)
            search_query.cache_key = self._generate_cache_key(search_query)

            self.logger.info(
                f"Formatted {len(formatted_results)} results for SearchQuery {search_query.technical_id}"
            )

            return search_query

        except Exception as e:
            self.logger.error(
                f"Error formatting search results for SearchQuery {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _format_single_result(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> Dict[str, Any]:
        """Format a single search result."""
        formatted = {
            # Core HN item data
            "id": result.get("id"),
            "type": result.get("type"),
            "by": result.get("by"),
            "time": result.get("time"),
            "title": result.get("title"),
            "text": result.get("text"),
            "url": result.get("url"),
            "score": result.get("score"),
            "descendants": result.get("descendants"),
            # Relationship data
            "parent": result.get("parent"),
            "kids": result.get("kids"),
            "poll": result.get("poll"),
            "parts": result.get("parts"),
            # Status fields
            "deleted": result.get("deleted"),
            "dead": result.get("dead"),
            # Search metadata
            "search_metadata": {
                "relevance_score": self._calculate_relevance_score(
                    result, search_query
                ),
                "match_fields": self._identify_match_fields(result, search_query),
                "hierarchy_level": self._determine_hierarchy_level(
                    result, search_query
                ),
                "result_type": self._classify_result_type(result, search_query),
            },
        }

        # Add hierarchy information if requested
        if search_query.include_hierarchy:
            formatted["hierarchy_info"] = self._build_hierarchy_info(
                result, search_query
            )

        # Add display text for UI
        formatted["display_text"] = self._generate_display_text(result)

        # Remove None values to keep response clean
        return {k: v for k, v in formatted.items() if v is not None}

    def _calculate_relevance_score(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> float:
        """Calculate relevance score for the result."""
        score = 0.0

        # Base score from HN score
        if result.get("score"):
            score += min(result["score"] / 100.0, 1.0)  # Normalize to 0-1

        # Boost for exact matches in title
        if search_query.query_text and result.get("title"):
            if search_query.query_text.lower() in result["title"].lower():
                score += 0.5

        # Boost for matches in text
        if search_query.query_text and result.get("text"):
            if search_query.query_text.lower() in result["text"].lower():
                score += 0.3

        # Boost for recent items
        if result.get("time"):
            # Simple recency boost (this is simplified)
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _identify_match_fields(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> List[str]:
        """Identify which fields matched the search query."""
        match_fields = []

        if not search_query.query_text:
            return match_fields

        query_lower = search_query.query_text.lower()

        # Check each searchable field
        for field in search_query.search_fields or ["title", "text"]:
            if result.get(field) and query_lower in result[field].lower():
                match_fields.append(field)

        return match_fields

    def _determine_hierarchy_level(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> int:
        """Determine the hierarchy level of the result."""
        if not search_query.include_hierarchy:
            return 0

        # Count parent chain length
        parent_chain = result.get("parent_chain", [])
        return len(parent_chain)

    def _classify_result_type(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> str:
        """Classify the type of search result."""
        if search_query.include_hierarchy:
            if result.get("parent"):
                return "child_item"
            elif result.get("kids"):
                return "parent_item"
            else:
                return "leaf_item"
        else:
            return "direct_match"

    def _build_hierarchy_info(
        self, result: Dict[str, Any], search_query: SearchQuery
    ) -> Dict[str, Any]:
        """Build hierarchy information for the result."""
        hierarchy_info = {
            "has_parent": bool(result.get("parent")),
            "has_children": bool(result.get("kids")),
            "child_count": len(result.get("kids", [])),
            "parent_chain_length": len(result.get("parent_chain", [])),
        }

        # Add parent info if available
        if result.get("parent"):
            hierarchy_info["parent_id"] = result["parent"]

        # Add children info if available
        if result.get("kids"):
            hierarchy_info["child_ids"] = result["kids"][:5]  # Limit for response size
            if len(result["kids"]) > 5:
                hierarchy_info["more_children"] = len(result["kids"]) - 5

        return hierarchy_info

    def _generate_display_text(self, result: Dict[str, Any]) -> str:
        """Generate display text for the result."""
        if result.get("title"):
            return result["title"]
        elif result.get("text"):
            text = result["text"]
            # Truncate long text
            if len(text) > 150:
                return text[:147] + "..."
            return text
        else:
            return f"HN Item {result.get('id', 'Unknown')}"

    def _determine_search_index(self, search_query: SearchQuery) -> str:
        """Determine which search index was used."""
        if search_query.include_hierarchy:
            return "hierarchy_index"
        elif search_query.filters:
            return "filtered_index"
        else:
            return "text_index"

    def _generate_cache_key(self, search_query: SearchQuery) -> str:
        """Generate cache key for the search query."""
        import hashlib

        # Create a string representation of the query
        query_parts = [
            search_query.query_text,
            str(search_query.filters),
            str(search_query.sort_order),
            str(search_query.limit),
            str(search_query.offset),
            str(search_query.include_hierarchy),
            str(search_query.search_fields),
        ]

        query_string = "|".join(str(part) for part in query_parts)

        # Generate hash
        return hashlib.md5(query_string.encode()).hexdigest()[:16]
