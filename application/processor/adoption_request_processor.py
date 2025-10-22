"""
AdoptionRequestProcessor for Cyoda Client Application

Processes approved adoption requests and performs necessary business logic
such as sending notifications and updating related entities.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption_request import AdoptionRequest


class AdoptionRequestProcessor(CyodaProcessor):
    """
    Processor for AdoptionRequest that handles post-approval processing
    such as notifications and status updates.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionRequestProcessor",
            description="Processes approved adoption requests",
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> None:
        """
        Process the adoption request after approval.

        Args:
            entity: The CyodaEntity to process (expected to be AdoptionRequest)
            **kwargs: Additional processing parameters
        """
        try:
            self.logger.info(
                f"Processing adoption request {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionRequest for type-safe operations
            adoption_request = cast_entity(entity, AdoptionRequest)

            # Log the approval
            self.logger.info(
                f"Adoption request {adoption_request.technical_id} for "
                f"{adoption_request.applicant_name} has been approved"
            )

            # In a real application, you would:
            # 1. Send notification email to applicant
            # 2. Update related entities (e.g., create adoption record)
            # 3. Trigger downstream workflows
            # 4. Log the completion

            # For now, we just log the successful processing
            self.logger.info(
                f"Adoption request {adoption_request.technical_id} processing completed"
            )

        except Exception as e:
            self.logger.error(
                f"Error processing adoption request: {str(e)}"
            )
            raise

