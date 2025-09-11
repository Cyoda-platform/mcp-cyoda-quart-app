"""
CatFactDistributionProcessor for Cyoda Client Application

Marks cat fact as sent after email distribution.
Updates the entity state and logs distribution completion.
"""

import logging
from typing import Any, cast

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CatFactDistributionProcessor(CyodaProcessor):
    """
    Processor for marking cat facts as distributed after email sending.
    Updates the entity state to indicate distribution completion.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactDistributionProcessor",
            description="Marks cat fact as sent after email distribution",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact distribution marking according to functional requirements.

        Args:
            entity: The CatFact entity to mark as sent (must be in scheduled state)
            **kwargs: Additional processing parameters

        Returns:
            The CatFact entity marked as sent
        """
        try:
            self.logger.info(
                f"Processing cat fact distribution {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate cat fact exists and is in scheduled state
            if cat_fact.state != "scheduled":
                raise ValueError(
                    f"Cat fact must be in scheduled state, current state: {cat_fact.state}"
                )

            # Update timestamp to mark distribution completion
            cat_fact.update_timestamp()

            # Log distribution completion
            self.logger.info(
                f"Cat fact distribution completed: {cat_fact.fact_text[:50]}... (scheduled for {cat_fact.scheduled_send_date})"
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error processing cat fact distribution {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
