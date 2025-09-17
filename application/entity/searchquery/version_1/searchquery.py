# entity/searchquery/version_1/searchquery.py

"""
SearchQuery for Cyoda Client Application

Manages search operations for Hacker News items, including complex queries
with parent hierarchy joins and filtering capabilities as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class SearchQuery(CyodaEntity):
    """
    SearchQuery manages search operations for Hacker News items.

    Supports complex queries with parent hierarchy joins and filtering capabilities.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> preparing -> executing -> completed -> cached -> expired
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "SearchQuery"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core search fields
    query_id: Optional[str] = Field(
        default=None,
        alias="queryId",
        description="Unique identifier for the search query",
    )
    query_text: str = Field(
        ..., alias="queryText", description="Search terms and keywords"
    )

    # Search filters
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Search filters (type, author, date range, score)",
    )

    # Search options
    include_children: bool = Field(
        default=False,
        alias="includeChildren",
        description="Boolean to include child comments in results",
    )
    parent_hierarchy: bool = Field(
        default=False,
        alias="parentHierarchy",
        description="Boolean to traverse parent relationships",
    )
    sort_by: str = Field(
        default="relevance",
        alias="sortBy",
        description="Sort criteria: score, time, relevance",
    )

    # Pagination
    limit: int = Field(default=50, description="Maximum number of results")
    offset: int = Field(default=0, description="Pagination offset")

    # Execution metadata
    executed_at: Optional[str] = Field(
        default=None, alias="executedAt", description="Query execution timestamp"
    )
    results_count: Optional[int] = Field(
        default=None, alias="resultsCount", description="Number of results returned"
    )
    execution_time: Optional[str] = Field(
        default=None, alias="executionTime", description="Query execution duration"
    )

    # Search results
    results: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Search results with relevance scores"
    )

    # Caching metadata
    cached_at: Optional[str] = Field(
        default=None, alias="cachedAt", description="When results were cached"
    )
    cache_ttl: int = Field(
        default=86400,  # 24 hours
        alias="cacheTtl",
        description="Cache time-to-live in seconds",
    )
    cache_key: Optional[str] = Field(
        default=None, alias="cacheKey", description="Generated cache key for the query"
    )

    # Validation constants
    ALLOWED_SORT_OPTIONS: ClassVar[List[str]] = ["score", "time", "relevance"]
    MAX_LIMIT: ClassVar[int] = 1000
    MAX_QUERY_LENGTH: ClassVar[int] = 500

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        """Validate search query text"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Query text must be non-empty")
        if len(v) > cls.MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query text must be at most {cls.MAX_QUERY_LENGTH} characters"
            )
        return v.strip()

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort criteria"""
        if v not in cls.ALLOWED_SORT_OPTIONS:
            raise ValueError(f"Sort option must be one of: {cls.ALLOWED_SORT_OPTIONS}")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate result limit"""
        if v <= 0:
            raise ValueError("Limit must be positive")
        if v > cls.MAX_LIMIT:
            raise ValueError(f"Limit must be at most {cls.MAX_LIMIT}")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Validate pagination offset"""
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v

    @field_validator("cache_ttl")
    @classmethod
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL"""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v

    def set_executed(self, execution_time_ms: int) -> None:
        """Mark query as executed with timing"""
        self.executed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.execution_time = f"{execution_time_ms}ms"
        self.update_timestamp()

    def set_results(self, results: List[Dict[str, Any]]) -> None:
        """Set search results"""
        self.results = results
        self.results_count = len(results)
        self.update_timestamp()

    def set_cached(self, cache_key: str) -> None:
        """Mark results as cached"""
        self.cached_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.cache_key = cache_key
        self.update_timestamp()

    def is_cache_expired(self) -> bool:
        """Check if cached results have expired"""
        if not self.cached_at:
            return True

        cached_time = datetime.fromisoformat(self.cached_at.replace("Z", "+00:00"))
        current_time = datetime.now(timezone.utc)
        elapsed_seconds = (current_time - cached_time).total_seconds()

        return elapsed_seconds > self.cache_ttl

    def generate_cache_key(self) -> str:
        """Generate cache key based on query parameters"""
        import hashlib

        # Create a string representation of the query
        query_parts = [
            self.query_text,
            str(self.filters),
            str(self.include_children),
            str(self.parent_hierarchy),
            self.sort_by,
            str(self.limit),
            str(self.offset),
        ]

        query_string = "|".join(query_parts)
        return hashlib.md5(query_string.encode()).hexdigest()

    def get_filter_value(self, filter_name: str, default: Any = None) -> Any:
        """Get value from filters dict"""
        if not self.filters:
            return default
        return self.filters.get(filter_name, default)

    def set_filter(self, filter_name: str, value: Any) -> None:
        """Set filter value"""
        if self.filters is None:
            self.filters = {}
        self.filters[filter_name] = value
        self.update_timestamp()

    def has_date_range_filter(self) -> bool:
        """Check if query has date range filter"""
        return self.get_filter_value("date_range") is not None

    def has_author_filter(self) -> bool:
        """Check if query has author filter"""
        return self.get_filter_value("author") is not None

    def has_type_filter(self) -> bool:
        """Check if query has type filter"""
        return self.get_filter_value("type") is not None

    def has_score_filter(self) -> bool:
        """Check if query has score filter"""
        return self.get_filter_value("min_score") is not None

    def get_search_summary(self) -> Dict[str, Any]:
        """Get search execution summary"""
        return {
            "query_text": self.query_text,
            "results_count": self.results_count or 0,
            "execution_time": self.execution_time,
            "executed_at": self.executed_at,
            "cached": self.cached_at is not None,
            "cache_expired": self.is_cache_expired() if self.cached_at else None,
            "filters_applied": len(self.filters) if self.filters else 0,
            "include_children": self.include_children,
            "parent_hierarchy": self.parent_hierarchy,
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Add state and search summary for API compatibility
        data["state"] = self.state
        data["search_summary"] = self.get_search_summary()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
