"""
RetryAnalysisProcessor for Cyoda Client Application

Handles the retry of failed analysis processing.
Resets analysis for retry as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.analysis.version_1.analysis import Analysis
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class RetryAnalysisProcessor(CyodaProcessor):
    """
    Processor for Analysis that handles retry of failed analysis.
    Resets analysis status and increments retry count.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RetryAnalysisProcessor",
            description="Resets failed analysis for retry",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Analysis entity to prepare it for retry.

        Args:
            entity: The Analysis entity to retry
            **kwargs: Additional processing parameters

        Returns:
            The entity prepared for retry
        """
        try:
            self.logger.info(
                f"Preparing retry for Analysis {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Analysis for type-safe operations
            analysis = cast_entity(entity, Analysis)

            # Set status to retrying
            analysis.status = "retrying"

            # Increment retry count and set retry timestamp
            analysis.increment_retry_count()

            self.logger.info(
                f"Analysis {analysis.technical_id} prepared for retry (attempt #{analysis.retry_count})"
            )

            return analysis

        except Exception as e:
            self.logger.error(
                f"Error preparing retry for analysis {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
