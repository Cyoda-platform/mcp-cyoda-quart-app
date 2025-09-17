"""
IsArchivableCriterion for Cyoda Client Application

Checks if an HNItem can be archived based on age or status as specified in workflow requirements.
"""

from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitem.version_1.hnitem import HNItem


class IsArchivableCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if an HNItem should be archived.
    
    Checks if item age > 30 days OR item is marked as deleted/dead.
    """

    def __init__(self) -> None:
        super().__init__(
            name="is_archivable",
            description="Checks if item can be archived based on age or status"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the HNItem meets archival criteria.

        Args:
            entity: The CyodaEntity to check (expected to be HNItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if the item should be archived, False otherwise
        """
        try:
            self.logger.info(
                f"Checking archival criteria for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Check if item is deleted or dead
            if hn_item.is_deleted_or_dead():
                self.logger.info(
                    f"HNItem {hn_item.technical_id} is archivable: item is deleted or dead"
                )
                return True

            # Check item age (if time field is available)
            if hn_item.time:
                item_age_days = self._calculate_age_in_days(hn_item.time)
                if item_age_days > 30:
                    self.logger.info(
                        f"HNItem {hn_item.technical_id} is archivable: item is {item_age_days} days old"
                    )
                    return True

            # Check if item has been inactive for too long (no recent updates)
            if hn_item.updated_at:
                last_update_age_days = self._calculate_update_age_in_days(hn_item.updated_at)
                if last_update_age_days > 30:
                    self.logger.info(
                        f"HNItem {hn_item.technical_id} is archivable: last updated {last_update_age_days} days ago"
                    )
                    return True

            # Item is not archivable
            self.logger.info(
                f"HNItem {hn_item.technical_id} is not archivable"
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Error checking archival criteria for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _calculate_age_in_days(self, unix_timestamp: int) -> int:
        """
        Calculate age in days from Unix timestamp.

        Args:
            unix_timestamp: Unix timestamp from HN API

        Returns:
            Age in days
        """
        try:
            # Convert Unix timestamp to datetime
            item_datetime = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
            current_datetime = datetime.now(timezone.utc)
            
            # Calculate age in days
            age_delta = current_datetime - item_datetime
            return age_delta.days
            
        except Exception as e:
            self.logger.warning(f"Error calculating age from timestamp {unix_timestamp}: {str(e)}")
            return 0

    def _calculate_update_age_in_days(self, updated_at: str) -> int:
        """
        Calculate age in days from updated_at timestamp.

        Args:
            updated_at: ISO timestamp string

        Returns:
            Age in days since last update
        """
        try:
            # Parse ISO timestamp
            update_datetime = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            current_datetime = datetime.now(timezone.utc)
            
            # Calculate age in days
            age_delta = current_datetime - update_datetime
            return age_delta.days
            
        except Exception as e:
            self.logger.warning(f"Error calculating update age from timestamp {updated_at}: {str(e)}")
            return 0
