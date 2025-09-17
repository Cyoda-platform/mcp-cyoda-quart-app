"""
DownloadSuccessfulCriterion for Cyoda Client Application

Checks if a DataSource download has completed successfully
by verifying the status field according to workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.datasource.version_1.datasource import DataSource


class DownloadSuccessfulCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if DataSource download completed successfully.
    """

    def __init__(self) -> None:
        super().__init__(
            name="download_successful",
            description="Checks if DataSource download completed successfully",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the DataSource download completed successfully.

        Args:
            entity: The CyodaEntity to check (expected to be DataSource)
            **kwargs: Additional criteria parameters

        Returns:
            True if download completed successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Checking download success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataSource for type-safe operations
            datasource = cast_entity(entity, DataSource)

            # Check if status is "completed"
            is_successful = datasource.is_download_completed()

            self.logger.info(
                f"Entity {datasource.technical_id} download success check: {is_successful} (status: {datasource.status})"
            )
            
            return is_successful

        except Exception as e:
            self.logger.error(
                f"Error checking download success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
