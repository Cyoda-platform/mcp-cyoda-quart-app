"""
CacheExpiredCriterion for Cyoda Client Application

Checks if cached search results have expired as specified in workflow requirements.
"""

from typing import Any

from application.entity.searchquery.version_1.searchquery import SearchQuery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class CacheExpiredCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if cached search results have expired.

    Checks if current time > cached_at + cache_ttl (24 hours default).
    """

    def __init__(self) -> None:
        super().__init__(
            name="cache_expired", description="Checks if cached results have expired"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if cached search results have expired.

        Args:
            entity: The CyodaEntity to check (expected to be SearchQuery)
            **kwargs: Additional criteria parameters

        Returns:
            True if cache has expired, False otherwise
        """
        try:
            self.logger.info(
                f"Checking cache expiration for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to SearchQuery for type-safe operations
            search_query = cast_entity(entity, SearchQuery)

            # Check if cache has expired
            cache_expired = search_query.is_cache_expired()

            if cache_expired:
                if search_query.cached_at:
                    self.logger.info(
                        f"SearchQuery {search_query.technical_id} cache has expired. "
                        f"Cached at: {search_query.cached_at}, TTL: {search_query.cache_ttl}s"
                    )
                else:
                    self.logger.info(
                        f"SearchQuery {search_query.technical_id} has no cached results"
                    )
            else:
                self.logger.info(
                    f"SearchQuery {search_query.technical_id} cache is still valid. "
                    f"Cached at: {search_query.cached_at}, TTL: {search_query.cache_ttl}s"
                )

            return cache_expired

        except Exception as e:
            self.logger.error(
                f"Error checking cache expiration for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # If we can't determine expiration, assume expired for safety
            return True
