"""
RetryAllowedCriterion for Cyoda Client Application

Checks if retry is allowed for failed HN items.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitem.version_1.hnitem import HnItem


class RetryAllowedCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if retry is allowed for failed HN items.
    """

    def __init__(self) -> None:
        super().__init__(
            name="retry_allowed_criterion",
            description="Checks if retry is allowed for failed HN items",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if retry is allowed for the failed entity.

        Args:
            entity: The CyodaEntity to check (expected to be HnItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if retry is allowed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking retry eligibility for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Check if retry is allowed
            max_retries = 3
            retry_allowed = hn_item.can_retry(max_retries)

            self.logger.info(
                f"Retry allowed check for HnItem {hn_item.id}: {retry_allowed} "
                f"(retry_count: {hn_item.retry_count}, failure_reason: {hn_item.failure_reason})"
            )

            return retry_allowed

        except Exception as e:
            self.logger.error(
                f"Error checking retry eligibility for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
