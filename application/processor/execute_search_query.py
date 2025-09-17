"""
ExecuteSearchQueryProcessor for Cyoda Client Application

Executes search queries against HN items database as specified in workflow requirements.
"""

import logging
import time
from typing import Any, Dict, List

from application.entity.hnitem.version_1.hnitem import HNItem
from application.entity.searchquery.version_1.searchquery import SearchQuery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class ExecuteSearchQueryProcessor(CyodaProcessor):
    """
    Processor for executing search queries against HN items database.

    Parses query, applies filters, searches indices, and ranks results.
    """

    def __init__(self) -> None:
        super().__init__(
            name="execute_search_query",
            description="Executes search query against HN items database",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Execute search query according to functional requirements.

        Args:
            entity: The SearchQuery to execute
            **kwargs: Additional processing parameters

        Returns:
            Search query with results and metadata
        """
        try:
            start_time = time.time()

            self.logger.info(
                f"Executing SearchQuery {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to SearchQuery for type-safe operations
            search_query = cast_entity(entity, SearchQuery)

            # Get entity service for searching
            entity_service = get_entity_service()

            # Build search conditions
            search_conditions = await self._build_search_conditions(search_query)

            # Execute search
            search_results = await entity_service.search(
                entity_class=HNItem.ENTITY_NAME,
                condition=search_conditions,
                entity_version=str(HNItem.ENTITY_VERSION),
            )

            # Process and rank results
            processed_results = await self._process_search_results(
                search_results, search_query
            )

            # Apply pagination
            paginated_results = self._apply_pagination(
                processed_results, search_query.offset, search_query.limit
            )

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Set results and execution metadata
            search_query.set_results(paginated_results)
            search_query.set_executed(execution_time_ms)

            # Generate cache key for future caching
            cache_key = search_query.generate_cache_key()
            search_query.cache_key = cache_key

            self.logger.info(
                f"SearchQuery {search_query.technical_id} executed successfully. "
                f"Found {len(paginated_results)} results in {execution_time_ms}ms"
            )

            return search_query

        except Exception as e:
            self.logger.error(
                f"Error executing SearchQuery {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _build_search_conditions(
        self, search_query: SearchQuery
    ) -> SearchConditionRequest:
        """
        Build search conditions from SearchQuery parameters.

        Args:
            search_query: The search query entity

        Returns:
            SearchConditionRequest for entity service
        """
        builder = SearchConditionRequest.builder()

        # Apply type filter
        if search_query.has_type_filter():
            item_type = search_query.get_filter_value("type")
            builder.equals("type", item_type)

        # Apply author filter
        if search_query.has_author_filter():
            author = search_query.get_filter_value("author")
            builder.equals("by", author)

        # Apply score filter
        if search_query.has_score_filter():
            min_score = search_query.get_filter_value("min_score")
            # Note: This is a simplified implementation
            # In a real system, you'd use a proper range query
            builder.equals("score", str(min_score))

        # Apply state filter (only search active items by default)
        builder.equals("state", "active")

        return builder.build()

    async def _process_search_results(
        self, search_results: List[Any], search_query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """
        Process and rank search results.

        Args:
            search_results: Raw search results from entity service
            search_query: The search query entity

        Returns:
            Processed and ranked results
        """
        processed_results = []

        for result in search_results:
            try:
                # Extract HNItem data
                hn_item_data = (
                    result.data.model_dump(by_alias=True)
                    if hasattr(result.data, "model_dump")
                    else result.data
                )

                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(
                    hn_item_data, search_query
                )

                # Create result entry
                result_entry = {
                    "item_id": (
                        result.metadata.id
                        if result.metadata
                        else hn_item_data.get("entity_id")
                    ),
                    "relevance_score": relevance_score,
                    "data": hn_item_data,
                }

                # Include children if requested
                if search_query.include_children and hn_item_data.get("kids"):
                    result_entry["children"] = await self._fetch_children(
                        hn_item_data.get("kids", [])
                    )

                processed_results.append(result_entry)

            except Exception as e:
                self.logger.warning(f"Error processing search result: {str(e)}")
                continue

        # Sort by relevance score and sort criteria
        processed_results = self._sort_results(processed_results, search_query.sort_by)

        return processed_results

    def _calculate_relevance_score(
        self, item_data: Dict[str, Any], search_query: SearchQuery
    ) -> float:
        """
        Calculate relevance score for search result.

        Args:
            item_data: HN item data
            search_query: The search query

        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        query_terms = search_query.query_text.lower().split()

        # Check title match
        title = item_data.get("title", "").lower()
        for term in query_terms:
            if term in title:
                score += 0.4  # Title matches are highly relevant

        # Check text content match
        text = item_data.get("text", "").lower()
        for term in query_terms:
            if term in text:
                score += 0.3  # Text matches are moderately relevant

        # Check author match
        author = item_data.get("by", "").lower()
        for term in query_terms:
            if term in author:
                score += 0.2  # Author matches are less relevant

        # Boost score based on item score/popularity
        item_score = item_data.get("score", 0)
        if item_score > 0:
            score += min(item_score / 1000.0, 0.1)  # Small boost for popular items

        # Normalize score to 0-1 range
        return min(score, 1.0)

    def _sort_results(
        self, results: List[Dict[str, Any]], sort_by: str
    ) -> List[Dict[str, Any]]:
        """
        Sort search results by specified criteria.

        Args:
            results: List of search results
            sort_by: Sort criteria (relevance, score, time)

        Returns:
            Sorted results
        """
        if sort_by == "relevance":
            return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
        elif sort_by == "score":
            return sorted(
                results, key=lambda x: x["data"].get("score", 0), reverse=True
            )
        elif sort_by == "time":
            return sorted(results, key=lambda x: x["data"].get("time", 0), reverse=True)
        else:
            # Default to relevance
            return sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    def _apply_pagination(
        self, results: List[Dict[str, Any]], offset: int, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Apply pagination to search results.

        Args:
            results: List of search results
            offset: Pagination offset
            limit: Maximum number of results

        Returns:
            Paginated results
        """
        start_index = offset
        end_index = offset + limit
        return results[start_index:end_index]

    async def _fetch_children(self, child_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Fetch child items for parent hierarchy.

        Args:
            child_ids: List of child item IDs

        Returns:
            List of child item data
        """
        # This is a simplified implementation
        # In a real system, you'd fetch the actual child items
        return [
            {"id": child_id, "type": "comment"} for child_id in child_ids[:10]
        ]  # Limit to 10 children
