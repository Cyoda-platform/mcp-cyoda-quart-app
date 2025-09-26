"""
TriggerAnalysisProcessor for Cyoda Client Application

Handles the creation of analysis entities and triggering of analysis workflow.
Creates analysis entities for validated comments as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.analysis.version_1.analysis import Analysis
from application.entity.comment.version_1.comment import Comment
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class TriggerAnalysisProcessor(CyodaProcessor):
    """
    Processor for Comment that creates analysis entities and triggers analysis workflow.
    Creates new Analysis entity for the validated comment.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TriggerAnalysisProcessor",
            description="Creates analysis entity and triggers analysis workflow for validated comments",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Comment entity to trigger analysis.

        Args:
            entity: The Comment entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with analysis triggered
        """
        try:
            self.logger.info(
                f"Triggering analysis for Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Create analysis entity for this comment
            await self._create_analysis_entity(comment)

            # Set analysis triggered flag
            comment.set_analysis_triggered(True)

            self.logger.info(f"Analysis triggered for Comment {comment.technical_id}")

            return comment

        except Exception as e:
            self.logger.error(
                f"Error triggering analysis for comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _create_analysis_entity(self, comment: Comment) -> None:
        """
        Create Analysis entity for the given comment.

        Args:
            comment: The Comment entity to create analysis for
        """
        entity_service = get_entity_service()

        try:
            # Create Analysis entity using direct Pydantic model construction
            analysis = Analysis(
                comment_id=comment.technical_id or comment.entity_id or "unknown",
                status="processing",
            )

            # Convert Pydantic model to dict for EntityService.save()
            analysis_data = analysis.model_dump(by_alias=True)

            # Save the new Analysis entity using entity constants
            response = await entity_service.save(
                entity=analysis_data,
                entity_class=Analysis.ENTITY_NAME,
                entity_version=str(Analysis.ENTITY_VERSION),
            )

            # Get the technical ID of the created entity
            created_entity_id = response.metadata.id

            self.logger.info(
                f"Created Analysis entity {created_entity_id} for Comment {comment.technical_id} - workflow will handle state transitions automatically"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create Analysis entity for Comment {comment.technical_id}: {str(e)}"
            )
            raise
