"""
CompleteAnalysisProcessor for Cyoda Client Application

Handles the finalization of analysis processing.
Marks analysis as complete and sets completion timestamp as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.analysis.version_1.analysis import Analysis


class CompleteAnalysisProcessor(CyodaProcessor):
    """
    Processor for Analysis that finalizes analysis processing.
    Marks analysis as complete and sets completion timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteAnalysisProcessor",
            description="Finalizes analysis processing and marks as complete",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Analysis entity to mark it as complete.

        Args:
            entity: The Analysis entity to complete
            **kwargs: Additional processing parameters

        Returns:
            The completed entity
        """
        try:
            self.logger.info(
                f"Completing analysis for Analysis {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Analysis for type-safe operations
            analysis = cast_entity(entity, Analysis)

            # Set status to completed
            analysis.status = "completed"
            
            # Set completion timestamp
            analysis.set_completed_at()

            self.logger.info(
                f"Analysis {analysis.technical_id} completed successfully"
            )

            return analysis

        except Exception as e:
            self.logger.error(
                f"Error completing analysis for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
