"""
PerformSearch Processor for SearchQuery

Executes the parsed and validated search query against HNItem data
with support for hierarchy traversal and complex filtering.
"""

import logging
from typing import Any, Dict, List

from application.entity.hnitem.version_1.hnitem import HNItem
from application.entity.searchquery.version_1.searchquery import SearchQuery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class PerformSearch(CyodaProcessor):
    """
    Processor for executing SearchQuery against HNItem data.
    Supports text search, filtering, and hierarchy traversal.
    """

    def __init__(self) -> None:
        super().__init__(
            name="perform_search",
            description="Executes SearchQuery against HNItem data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Execute the search query against HNItem data.

        Args:
            entity: The validated SearchQuery to execute
            **kwargs: Additional processing parameters

        Returns:
            The query with search results
        """
        try:
            self.logger.info(
                f"Executing SearchQuery {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to SearchQuery for type-safe operations
            search_query = cast_entity(entity, SearchQuery)

            # Start execution timing
            search_query.start_execution()

            # Build search conditions
            search_conditions = self._build_search_conditions(search_query)

            # Execute the search
            entity_service = get_entity_service()
            search_results = await entity_service.search(
                entity_class=HNItem.ENTITY_NAME,
                condition=search_conditions,
                entity_version=str(HNItem.ENTITY_VERSION),
            )

            # Convert results to dictionaries
            raw_results = [
                result.data.model_dump(by_alias=True) for result in search_results
            ]

            # Apply text filtering if needed
            filtered_results = self._apply_text_filtering(raw_results, search_query)

            # Apply hierarchy expansion if requested
            if search_query.include_hierarchy:
                filtered_results = await self._expand_hierarchy(
                    filtered_results, search_query, entity_service
                )

            # Apply sorting
            sorted_results = self._apply_sorting(filtered_results, search_query)

            # Apply pagination
            paginated_results = self._apply_pagination(sorted_results, search_query)

            # Complete execution with results
            search_query.complete_execution(len(paginated_results), paginated_results)

            self.logger.info(
                f"SearchQuery {search_query.technical_id} executed successfully. "
                f"Found {search_query.result_count} results in {search_query.execution_time_ms}ms"
            )

            return search_query

        except Exception as e:
            self.logger.error(
                f"Error executing SearchQuery {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _build_search_conditions(
        self, search_query: SearchQuery
    ) -> SearchConditionRequest:
        """Build search conditions from the query parameters."""
        builder = SearchConditionRequest.builder()

        # Apply filters
        if search_query.filters:
            for field, value in search_query.filters.items():
                if field in ["type", "by"]:  # Direct field matches
                    builder.equals(field, str(value))

        # Apply field searches from parsed query
        if search_query.parsed_query and "field_searches" in search_query.parsed_query:
            field_searches = search_query.parsed_query["field_searches"]
            for field, values in field_searches.items():
                for value in values:
                    if field in ["type", "by"]:
                        builder.equals(field, value)

        # Apply date range filter
        if search_query.date_range:
            if "from" in search_query.date_range:
                # Convert date to Unix timestamp for comparison
                # This is simplified - in practice you'd need proper date conversion
                builder.equals("time_from", search_query.date_range["from"])
            if "to" in search_query.date_range:
                builder.equals("time_to", search_query.date_range["to"])

        # Apply score range filter
        if search_query.score_range:
            if "min" in search_query.score_range:
                builder.equals("score_min", str(search_query.score_range["min"]))
            if "max" in search_query.score_range:
                builder.equals("score_max", str(search_query.score_range["max"]))

        return builder.build()

    def _apply_text_filtering(
        self, results: List[Dict[str, Any]], search_query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """Apply text-based filtering to results."""
        if not search_query.query_text or not search_query.parsed_query:
            return results

        filtered_results = []
        search_terms = search_query.parsed_query.get("terms", [])
        quoted_phrases = search_query.parsed_query.get("quoted_phrases", [])

        for result in results:
            search_fields = search_query.search_fields or ["title", "text"]
            if self._matches_text_criteria(
                result, search_terms, quoted_phrases, search_fields
            ):
                filtered_results.append(result)

        return filtered_results

    def _matches_text_criteria(
        self,
        item: Dict[str, Any],
        search_terms: List[str],
        quoted_phrases: List[str],
        search_fields: List[str],
    ) -> bool:
        """Check if an item matches the text search criteria."""
        # Get searchable text from specified fields
        searchable_text = ""
        for field in search_fields:
            if field in item and item[field]:
                searchable_text += f" {item[field]}"

        searchable_text = searchable_text.lower()

        # Check search terms (all must match)
        for term in search_terms:
            if term.lower() not in searchable_text:
                return False

        # Check quoted phrases (all must match exactly)
        for phrase in quoted_phrases:
            if phrase.lower() not in searchable_text:
                return False

        return True

    async def _expand_hierarchy(
        self,
        results: List[Dict[str, Any]],
        search_query: SearchQuery,
        entity_service: Any,
    ) -> List[Dict[str, Any]]:
        """Expand results to include hierarchy relationships."""
        expanded_results = list(results)  # Start with original results

        for result in results:
            # Include parents if requested
            if search_query.include_parents and result.get("parent"):
                parent_id = result["parent"]
                if isinstance(parent_id, int):
                    max_depth = search_query.max_depth or 5
                    parent_items = await self._get_parent_chain(
                        parent_id, max_depth, entity_service
                    )
                    expanded_results.extend(parent_items)

            # Include children if requested
            if search_query.include_children and result.get("kids"):
                kids = result["kids"]
                if isinstance(kids, list):
                    max_depth = search_query.max_depth or 5
                    child_items = await self._get_child_items(
                        kids, max_depth, entity_service
                    )
                    expanded_results.extend(child_items)

        # Remove duplicates based on HN item ID
        seen_ids = set()
        unique_results = []
        for result in expanded_results:
            item_id = result.get("id")
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_results.append(result)

        return unique_results

    async def _get_parent_chain(
        self, parent_id: int, max_depth: int, entity_service: Any
    ) -> List[Dict[str, Any]]:
        """Get parent chain up to max_depth."""
        parents = []
        current_parent_id = parent_id
        depth = 0

        while current_parent_id and depth < (max_depth or 5):
            try:
                # Search for parent by HN item ID
                parent_results = await entity_service.search(
                    entity_class=HNItem.ENTITY_NAME,
                    condition=SearchConditionRequest.builder()
                    .equals("id", str(current_parent_id))
                    .build(),
                    entity_version=str(HNItem.ENTITY_VERSION),
                )

                if parent_results:
                    parent_data = parent_results[0].data.model_dump(by_alias=True)
                    parents.append(parent_data)
                    current_parent_id = parent_data.get("parent")
                else:
                    break

            except Exception as e:
                self.logger.warning(
                    f"Error fetching parent {current_parent_id}: {str(e)}"
                )
                break

            depth += 1

        return parents

    async def _get_child_items(
        self, child_ids: List[int], max_depth: int, entity_service: Any
    ) -> List[Dict[str, Any]]:
        """Get child items up to max_depth."""
        children = []

        for child_id in child_ids[:10]:  # Limit to prevent excessive queries
            try:
                # Search for child by HN item ID
                child_results = await entity_service.search(
                    entity_class=HNItem.ENTITY_NAME,
                    condition=SearchConditionRequest.builder()
                    .equals("id", str(child_id))
                    .build(),
                    entity_version=str(HNItem.ENTITY_VERSION),
                )

                if child_results:
                    child_data = child_results[0].data.model_dump(by_alias=True)
                    children.append(child_data)

            except Exception as e:
                self.logger.warning(f"Error fetching child {child_id}: {str(e)}")

        return children

    def _apply_sorting(
        self, results: List[Dict[str, Any]], search_query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """Apply sorting to results."""
        if search_query.sort_order == "score":
            return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        elif search_query.sort_order == "time":
            return sorted(results, key=lambda x: x.get("time", 0), reverse=True)
        elif search_query.sort_order == "comments":
            return sorted(results, key=lambda x: x.get("descendants", 0), reverse=True)
        else:  # relevance or default
            return results  # Keep original order for relevance

    def _apply_pagination(
        self, results: List[Dict[str, Any]], search_query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """Apply pagination to results."""
        start = search_query.offset
        end = start + search_query.limit
        return results[start:end]
