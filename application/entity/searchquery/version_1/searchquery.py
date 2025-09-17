# entity/searchquery/version_1/searchquery.py

"""
SearchQuery Entity for Cyoda Client Application

Handles search functionality for HN items with support for complex queries 
and parent hierarchy joins.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class SearchQuery(CyodaEntity):
    """
    SearchQuery handles search functionality for HN items.
    
    Supports complex queries and parent hierarchy joins.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> validated -> executed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "SearchQuery"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core search fields
    query_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the search query"
    )
    query_text: str = Field(
        ...,
        description="Text search terms"
    )
    
    # Search configuration
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Search filters (type, author, date range, etc.)"
    )
    include_hierarchy: bool = Field(
        default=False,
        description="Boolean to include parent hierarchy in results"
    )
    sort_order: str = Field(
        default="relevance",
        description="Sort criteria: score, time, relevance"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        description="Pagination offset"
    )
    
    # Execution metadata
    executed_at: Optional[str] = Field(
        default=None,
        description="Query execution timestamp"
    )
    execution_time_ms: Optional[int] = Field(
        default=None,
        description="Query execution time in milliseconds"
    )
    result_count: int = Field(
        default=0,
        description="Number of results found"
    )
    
    # Results
    results: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Array of matching HNItem references"
    )
    
    # Advanced search options
    search_fields: Optional[List[str]] = Field(
        default_factory=lambda: ["title", "text"],
        description="Fields to search in: title, text, by, url"
    )
    date_range: Optional[Dict[str, str]] = Field(
        default=None,
        description="Date range filter with 'from' and 'to' ISO dates"
    )
    score_range: Optional[Dict[str, int]] = Field(
        default=None,
        description="Score range filter with 'min' and 'max' values"
    )
    
    # Hierarchy search options
    max_depth: Optional[int] = Field(
        default=None,
        description="Maximum depth for hierarchy traversal"
    )
    include_children: bool = Field(
        default=False,
        description="Include child comments in results"
    )
    include_parents: bool = Field(
        default=False,
        description="Include parent items in results"
    )
    
    # Processing fields
    parsed_query: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parsed and validated query structure"
    )
    search_index_used: Optional[str] = Field(
        default=None,
        description="Search index that was used for the query"
    )
    cache_key: Optional[str] = Field(
        default=None,
        description="Cache key for result caching"
    )

    # Validation constants
    ALLOWED_SORT_ORDERS: ClassVar[List[str]] = [
        "relevance", "score", "time", "comments"
    ]
    
    ALLOWED_SEARCH_FIELDS: ClassVar[List[str]] = [
        "title", "text", "by", "url", "type"
    ]

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        """Validate query text is not empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Query text cannot be empty")
        if len(v) > 1000:
            raise ValueError("Query text cannot exceed 1000 characters")
        return v.strip()

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order"""
        if v not in cls.ALLOWED_SORT_ORDERS:
            raise ValueError(f"Sort order must be one of: {cls.ALLOWED_SORT_ORDERS}")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit is within reasonable bounds"""
        if v <= 0:
            raise ValueError("Limit must be positive")
        if v > 1000:
            raise ValueError("Limit cannot exceed 1000")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Validate offset is non-negative"""
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v

    @field_validator("search_fields")
    @classmethod
    def validate_search_fields(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate search fields are allowed"""
        if v is not None:
            for field in v:
                if field not in cls.ALLOWED_SEARCH_FIELDS:
                    raise ValueError(f"Search field '{field}' not allowed. Must be one of: {cls.ALLOWED_SEARCH_FIELDS}")
        return v

    @field_validator("max_depth")
    @classmethod
    def validate_max_depth(cls, v: Optional[int]) -> Optional[int]:
        """Validate max depth is reasonable"""
        if v is not None and (v <= 0 or v > 10):
            raise ValueError("Max depth must be between 1 and 10")
        return v

    def is_text_search(self) -> bool:
        """Check if this is a text-based search"""
        return bool(self.query_text and self.query_text.strip())

    def is_filtered_search(self) -> bool:
        """Check if this search has filters applied"""
        return bool(self.filters and len(self.filters) > 0)

    def is_hierarchy_search(self) -> bool:
        """Check if this search includes hierarchy traversal"""
        return self.include_hierarchy or self.include_children or self.include_parents

    def has_date_filter(self) -> bool:
        """Check if date range filter is applied"""
        return self.date_range is not None

    def has_score_filter(self) -> bool:
        """Check if score range filter is applied"""
        return self.score_range is not None

    def start_execution(self) -> None:
        """Mark query execution as started"""
        self.executed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def complete_execution(self, result_count: int, results: List[Dict[str, Any]]) -> None:
        """Mark query execution as completed"""
        if self.executed_at:
            start_time = datetime.fromisoformat(self.executed_at.replace("Z", "+00:00"))
            end_time = datetime.now(timezone.utc)
            duration = end_time - start_time
            self.execution_time_ms = int(duration.total_seconds() * 1000)
        
        self.result_count = result_count
        self.results = results

    def get_filter_summary(self) -> Dict[str, Any]:
        """Get a summary of applied filters"""
        summary = {
            "has_text_search": self.is_text_search(),
            "has_filters": self.is_filtered_search(),
            "has_hierarchy": self.is_hierarchy_search(),
            "has_date_filter": self.has_date_filter(),
            "has_score_filter": self.has_score_filter(),
            "search_fields": self.search_fields,
            "sort_order": self.sort_order,
            "limit": self.limit,
            "offset": self.offset
        }
        return summary

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of execution results"""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "result_count": self.result_count,
            "execution_time_ms": self.execution_time_ms,
            "executed_at": self.executed_at,
            "filter_summary": self.get_filter_summary()
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Add state for API compatibility
        data["state"] = self.state
        # Add execution summary
        data["execution_summary"] = self.get_execution_summary()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
