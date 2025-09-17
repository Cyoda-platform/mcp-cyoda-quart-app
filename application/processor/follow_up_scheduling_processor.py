"""
FollowUpSchedulingProcessor for Purrfect Pets API

Schedules a follow-up for a completed adoption.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from application.entity.adoption.version_1.adoption import Adoption
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class FollowUpSchedulingProcessor(CyodaProcessor):
    """
    Processor for Adoption follow-up scheduling that schedules post-adoption follow-up.
    """

    def __init__(self) -> None:
        super().__init__(
            name="FollowUpSchedulingProcessor",
            description="Schedules a follow-up for a completed adoption",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Adoption follow-up scheduling according to functional requirements.

        Args:
            entity: The Adoption entity to process (must be completed)
            **kwargs: Additional processing parameters (follow-up date, type)

        Returns:
            The processed adoption entity in follow_up_pending state
        """
        try:
            self.logger.info(
                f"Processing Adoption follow-up scheduling for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Get follow-up information from kwargs
            follow_up_date = kwargs.get("followUpDate") or kwargs.get("follow_up_date")
            follow_up_type = kwargs.get("followUpType") or kwargs.get("follow_up_type")
            days_after_adoption = kwargs.get("daysAfterAdoption") or kwargs.get(
                "days_after_adoption"
            )

            # Validate adoption is completed
            if not adoption.is_completed():
                raise ValueError("Adoption must be completed to schedule follow-up")

            # Calculate follow-up date if not provided
            if not follow_up_date:
                follow_up_date = self._calculate_follow_up_date(
                    adoption, days_after_adoption
                )

            # Validate follow-up date format
            self._validate_follow_up_date(follow_up_date)

            # Set follow-up date
            adoption.follow_up_date = follow_up_date
            adoption.follow_up_completed = False

            # Create follow-up reminder (in a real system)
            # This would create calendar entries, notifications, etc.
            self.logger.info(
                f"Would create follow-up reminder for adoption {adoption.technical_id} on {follow_up_date}"
            )

            # Notify relevant staff (in a real system)
            self.logger.info(
                f"Would notify staff to schedule follow-up for adoption {adoption.technical_id}"
            )

            # Log follow-up scheduling
            follow_up_info = f"Follow-up scheduled for {follow_up_date}"
            if follow_up_type:
                follow_up_info += f" (Type: {follow_up_type})"

            self.logger.info(f"Adoption {adoption.technical_id} - {follow_up_info}")

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error processing adoption follow-up scheduling {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_follow_up_date(
        self, adoption: Adoption, days_after_adoption: int = None
    ) -> str:
        """
        Calculate follow-up date based on adoption date.

        Args:
            adoption: The Adoption entity
            days_after_adoption: Number of days after adoption for follow-up (default: 30)

        Returns:
            Follow-up date in YYYY-MM-DD format
        """
        # Default to 30 days after adoption
        if days_after_adoption is None:
            days_after_adoption = 30

        # Parse adoption date
        if adoption.adoption_date:
            try:
                adoption_datetime = datetime.fromisoformat(
                    adoption.adoption_date.replace("Z", "+00:00")
                )
                follow_up_datetime = adoption_datetime + timedelta(
                    days=days_after_adoption
                )
                return follow_up_datetime.strftime("%Y-%m-%d")
            except ValueError:
                self.logger.warning(
                    f"Invalid adoption date format: {adoption.adoption_date}"
                )

        # Fallback to current date + days
        follow_up_datetime = datetime.now() + timedelta(days=days_after_adoption)
        return follow_up_datetime.strftime("%Y-%m-%d")

    def _validate_follow_up_date(self, follow_up_date: str) -> None:
        """
        Validate follow-up date format.

        Args:
            follow_up_date: The follow-up date to validate

        Raises:
            ValueError: If date format is invalid
        """
        try:
            datetime.strptime(follow_up_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Follow-up date must be in YYYY-MM-DD format: {follow_up_date}"
            )

        # Validate date is not in the past
        follow_up_datetime = datetime.strptime(follow_up_date, "%Y-%m-%d")
        if follow_up_datetime.date() < datetime.now().date():
            raise ValueError("Follow-up date cannot be in the past")

        self.logger.debug(f"Follow-up date validation passed: {follow_up_date}")
