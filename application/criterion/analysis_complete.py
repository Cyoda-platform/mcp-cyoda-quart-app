"""
AnalysisCompleteCriterion for Cyoda Client Application

Checks if a DataAnalysis has completed successfully
by verifying that results and metrics are populated according to workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.dataanalysis.version_1.dataanalysis import DataAnalysis


class AnalysisCompleteCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if DataAnalysis completed successfully.
    """

    def __init__(self) -> None:
        super().__init__(
            name="analysis_complete",
            description="Checks if DataAnalysis completed successfully with results and metrics",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the DataAnalysis completed successfully.

        Args:
            entity: The CyodaEntity to check (expected to be DataAnalysis)
            **kwargs: Additional criteria parameters

        Returns:
            True if analysis completed with results and metrics, False otherwise
        """
        try:
            self.logger.info(
                f"Checking analysis completion for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataAnalysis for type-safe operations
            analysis = cast_entity(entity, DataAnalysis)

            # Check if analysis is complete (has both results and metrics)
            is_complete = analysis.is_analysis_complete()

            self.logger.info(
                f"Entity {analysis.technical_id} analysis completion check: {is_complete} "
                f"(has_results: {analysis.results is not None}, has_metrics: {analysis.metrics is not None})"
            )
            
            return is_complete

        except Exception as e:
            self.logger.error(
                f"Error checking analysis completion for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
