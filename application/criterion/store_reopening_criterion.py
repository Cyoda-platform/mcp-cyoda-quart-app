"""
StoreReopeningCriterion for Purrfect Pets API

Checks if a temporarily closed store can be reopened.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.store.version_1.store import Store


class StoreReopeningCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a temporarily closed store can be reopened.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreReopeningCriterion",
            description="Checks if a temporarily closed store can be reopened",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the store can be reopened.

        Args:
            entity: The Store entity to check
            **kwargs: Additional criteria parameters (reopening data)

        Returns:
            True if the store can be reopened, False otherwise
        """
        try:
            self.logger.info(
                f"Checking store reopening eligibility for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Check if store's current state is TEMPORARILY_CLOSED
            if not store.is_temporarily_closed():
                self.logger.info(
                    f"Store {store.technical_id} is not temporarily closed (current state: {store.state})"
                )
                return False

            # Get reopening data from kwargs
            issues_resolved = kwargs.get("issuesResolved") or kwargs.get("issues_resolved")
            staff_available = kwargs.get("staffAvailable") or kwargs.get("staff_available")
            facilities_ready = kwargs.get("facilitiesReady") or kwargs.get("facilities_ready")

            # Check if closure issues have been resolved
            if not issues_resolved:
                self.logger.info(
                    f"Store {store.technical_id} closure issues not resolved"
                )
                return False

            # Check if adequate staff is available
            if not staff_available:
                self.logger.info(
                    f"Store {store.technical_id} does not have adequate staff available"
                )
                return False

            # Check if store facilities are ready
            if not facilities_ready:
                self.logger.info(
                    f"Store {store.technical_id} facilities are not ready"
                )
                return False

            self.logger.info(
                f"Store {store.technical_id} is ready for reopening"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking store reopening eligibility for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
