"""
ParseAndValidateQuery Processor for SearchQuery

Parses and validates search query parameters and structure
before search execution can begin.
"""

import logging
import re
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.searchquery.version_1.searchquery import SearchQuery


class ParseAndValidateQuery(CyodaProcessor):
    """
    Processor for parsing and validating SearchQuery structure and parameters.
    Validates query syntax, filters, and search configuration.
    """

    def __init__(self) -> None:
        super().__init__(
            name="parse_and_validate_query",
            description="Parses and validates SearchQuery structure and parameters",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Parse and validate the SearchQuery structure and parameters.

        Args:
            entity: The SearchQuery to parse and validate
            **kwargs: Additional processing parameters

        Returns:
            The validated query with parsed structure
        """
        try:
            self.logger.info(
                f"Parsing and validating SearchQuery {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to SearchQuery for type-safe operations
            search_query = cast_entity(entity, SearchQuery)

            validation_errors = []

            # Parse and validate query text
            parsed_query = self._parse_query_text(search_query.query_text)
            
            # Validate search fields
            if search_query.search_fields:
                invalid_fields = [
                    field for field in search_query.search_fields 
                    if field not in SearchQuery.ALLOWED_SEARCH_FIELDS
                ]
                if invalid_fields:
                    validation_errors.append(
                        f"Invalid search fields: {invalid_fields}. "
                        f"Allowed fields: {SearchQuery.ALLOWED_SEARCH_FIELDS}"
                    )

            # Validate filters
            if search_query.filters:
                validation_errors.extend(self._validate_filters(search_query.filters))

            # Validate date range
            if search_query.date_range:
                validation_errors.extend(self._validate_date_range(search_query.date_range))

            # Validate score range
            if search_query.score_range:
                validation_errors.extend(self._validate_score_range(search_query.score_range))

            # Validate hierarchy options
            if search_query.include_hierarchy and search_query.max_depth:
                if search_query.max_depth > 10:
                    validation_errors.append("Max depth cannot exceed 10 for performance reasons")

            # Set parsed query structure
            search_query.parsed_query = {
                "original_text": search_query.query_text,
                "parsed_terms": parsed_query["terms"],
                "operators": parsed_query["operators"],
                "quoted_phrases": parsed_query["quoted_phrases"],
                "field_searches": parsed_query["field_searches"],
                "validation_errors": validation_errors
            }

            # Log validation results
            if validation_errors:
                error_message = "; ".join(validation_errors)
                self.logger.warning(
                    f"SearchQuery {search_query.technical_id} validation failed: {error_message}"
                )
            else:
                self.logger.info(
                    f"SearchQuery {search_query.technical_id} validation successful"
                )

            return search_query

        except Exception as e:
            self.logger.error(
                f"Error parsing SearchQuery {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _parse_query_text(self, query_text: str) -> Dict[str, Any]:
        """
        Parse query text into structured components.
        
        Args:
            query_text: The raw query text
            
        Returns:
            Dictionary with parsed query components
        """
        parsed = {
            "terms": [],
            "operators": [],
            "quoted_phrases": [],
            "field_searches": {}
        }

        # Extract quoted phrases
        quoted_pattern = r'"([^"]*)"'
        quoted_matches = re.findall(quoted_pattern, query_text)
        parsed["quoted_phrases"] = quoted_matches
        
        # Remove quoted phrases from text for further processing
        text_without_quotes = re.sub(quoted_pattern, '', query_text)

        # Extract field searches (e.g., "author:username", "type:story")
        field_pattern = r'(\w+):(\w+)'
        field_matches = re.findall(field_pattern, text_without_quotes)
        for field, value in field_matches:
            if field not in parsed["field_searches"]:
                parsed["field_searches"][field] = []
            parsed["field_searches"][field].append(value)
        
        # Remove field searches from text
        text_without_fields = re.sub(field_pattern, '', text_without_quotes)

        # Extract operators (AND, OR, NOT)
        operator_pattern = r'\b(AND|OR|NOT)\b'
        operator_matches = re.findall(operator_pattern, text_without_fields, re.IGNORECASE)
        parsed["operators"] = [op.upper() for op in operator_matches]

        # Extract remaining terms
        text_without_operators = re.sub(operator_pattern, '', text_without_fields, flags=re.IGNORECASE)
        terms = [term.strip() for term in text_without_operators.split() if term.strip()]
        parsed["terms"] = terms

        return parsed

    def _validate_filters(self, filters: Dict[str, Any]) -> List[str]:
        """Validate search filters."""
        errors = []
        
        # Validate type filter
        if "type" in filters:
            valid_types = ["job", "story", "comment", "poll", "pollopt"]
            if filters["type"] not in valid_types:
                errors.append(f"Invalid type filter: {filters['type']}. Must be one of: {valid_types}")

        # Validate author filter
        if "by" in filters:
            if not isinstance(filters["by"], str) or len(filters["by"].strip()) == 0:
                errors.append("Author filter must be a non-empty string")

        # Validate score filter
        if "score" in filters:
            try:
                score = int(filters["score"])
                if score < 0:
                    errors.append("Score filter must be non-negative")
            except (ValueError, TypeError):
                errors.append("Score filter must be a valid integer")

        return errors

    def _validate_date_range(self, date_range: Dict[str, str]) -> List[str]:
        """Validate date range filter."""
        errors = []
        
        if not isinstance(date_range, dict):
            errors.append("Date range must be a dictionary")
            return errors

        # Check for required fields
        if "from" not in date_range and "to" not in date_range:
            errors.append("Date range must have 'from' or 'to' field")

        # Validate date format (simplified - should be ISO format)
        for field in ["from", "to"]:
            if field in date_range:
                date_str = date_range[field]
                if not isinstance(date_str, str):
                    errors.append(f"Date range '{field}' must be a string")
                elif not re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    errors.append(f"Date range '{field}' must be in YYYY-MM-DD format")

        return errors

    def _validate_score_range(self, score_range: Dict[str, int]) -> List[str]:
        """Validate score range filter."""
        errors = []
        
        if not isinstance(score_range, dict):
            errors.append("Score range must be a dictionary")
            return errors

        # Validate min/max values
        for field in ["min", "max"]:
            if field in score_range:
                try:
                    value = int(score_range[field])
                    if value < 0:
                        errors.append(f"Score range '{field}' must be non-negative")
                except (ValueError, TypeError):
                    errors.append(f"Score range '{field}' must be a valid integer")

        # Validate min <= max
        if "min" in score_range and "max" in score_range:
            try:
                if int(score_range["min"]) > int(score_range["max"]):
                    errors.append("Score range 'min' must be less than or equal to 'max'")
            except (ValueError, TypeError):
                pass  # Already handled above

        return errors
