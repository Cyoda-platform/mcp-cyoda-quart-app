"""
FollowUpCompletionProcessor for Purrfect Pets API

Completes a scheduled follow-up for an adoption.
"""

import logging
from typing import Any

from application.entity.adoption.version_1.adoption import Adoption
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class FollowUpCompletionProcessor(CyodaProcessor):
    """
    Processor for Adoption follow-up completion that marks a follow-up as completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="FollowUpCompletionProcessor",
            description="Completes a scheduled follow-up for an adoption",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Adoption follow-up completion according to functional requirements.

        Args:
            entity: The Adoption entity to process (must have follow-up pending)
            **kwargs: Additional processing parameters (follow-up notes, outcome)

        Returns:
            The processed adoption entity in follow_up_completed state
        """
        try:
            self.logger.info(
                f"Processing Adoption follow-up completion for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Get follow-up information from kwargs
            follow_up_notes = kwargs.get("followUpNotes") or kwargs.get(
                "follow_up_notes"
            )
            follow_up_outcome = kwargs.get("followUpOutcome") or kwargs.get(
                "follow_up_outcome"
            )
            staff_member = kwargs.get("staffMember") or kwargs.get("staff_member")

            # Validate adoption has follow-up pending
            if not adoption.is_follow_up_pending():
                raise ValueError("Adoption must have follow-up pending to complete")

            # Validate follow-up is scheduled
            if not adoption.has_follow_up_scheduled():
                raise ValueError("Follow-up must be scheduled before completion")

            # Mark follow-up as completed
            adoption.complete_follow_up()

            # Record follow-up outcome and notes
            if follow_up_notes:
                # In a real system, you might have a separate field for follow-up notes
                # For now, we'll append to adoption notes
                if adoption.adoption_notes:
                    adoption.adoption_notes += (
                        f"\n\nFollow-up completed: {follow_up_notes}"
                    )
                else:
                    adoption.adoption_notes = f"Follow-up completed: {follow_up_notes}"

            # Validate follow-up outcome
            self._validate_follow_up_outcome(follow_up_outcome)

            # Create follow-up completion record (in a real system)
            # This would create a detailed follow-up report
            self.logger.info(
                f"Would create follow-up completion record for adoption {adoption.technical_id}"
            )

            # Handle any issues identified during follow-up
            if follow_up_outcome and "issue" in follow_up_outcome.lower():
                self.logger.info(
                    f"Would escalate follow-up issues for adoption {adoption.technical_id}"
                )

            # Log follow-up completion
            completion_info = f"Follow-up completed"
            if staff_member:
                completion_info += f" by {staff_member}"
            if follow_up_outcome:
                completion_info += f" (Outcome: {follow_up_outcome})"

            self.logger.info(f"Adoption {adoption.technical_id} - {completion_info}")

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error processing adoption follow-up completion {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_follow_up_outcome(self, follow_up_outcome: str) -> None:
        """
        Validate follow-up outcome.

        Args:
            follow_up_outcome: The follow-up outcome to validate
        """
        if not follow_up_outcome:
            self.logger.warning("No follow-up outcome provided")
            return

        # Valid outcomes (in a real system, these might be predefined)
        valid_outcomes = [
            "successful",
            "pet_healthy",
            "pet_happy",
            "customer_satisfied",
            "minor_issues",
            "major_issues",
            "requires_intervention",
            "no_response",
            "customer_unavailable",
        ]

        # Basic validation - just check it's not empty and reasonable length
        if len(follow_up_outcome.strip()) > 500:
            raise ValueError("Follow-up outcome description is too long")

        self.logger.debug(f"Follow-up outcome validation passed: {follow_up_outcome}")
