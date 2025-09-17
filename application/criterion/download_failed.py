"""
DownloadFailedCriterion for Cyoda Client Application

Checks if a DataSource download has failed
by verifying the status field according to workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.datasource.version_1.datasource import DataSource


class DownloadFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if DataSource download failed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="download_failed",
            description="Checks if DataSource download failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the DataSource download failed.

        Args:
            entity: The CyodaEntity to check (expected to be DataSource)
            **kwargs: Additional criteria parameters

        Returns:
            True if download failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking download failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataSource for type-safe operations
            datasource = cast_entity(entity, DataSource)

            # Check if status is "failed"
            is_failed = datasource.is_download_failed()

            self.logger.info(
                f"Entity {datasource.technical_id} download failure check: {is_failed} (status: {datasource.status})"
            )

            return is_failed

        except Exception as e:
            self.logger.error(
                f"Error checking download failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
