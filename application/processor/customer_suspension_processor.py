"""
CustomerSuspensionProcessor for Purrfect Pets API

Handles customer suspension process.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerSuspensionProcessor(CyodaProcessor):
    """
    Processor for Customer suspension.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerSuspensionProcessor",
            description="Processes customer suspension",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer suspension according to functional requirements.
        """
        try:
            customer = cast_entity(entity, Customer)
            suspension_reason = kwargs.get("suspension_reason", "Policy violation")

            # Record suspension details
            customer.add_metadata("suspension_reason", suspension_reason)
            customer.add_metadata(
                "suspension_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # Cancel active reservations (simulated)
            await self._cancel_active_reservations(customer)

            # Suspend adoption privileges
            customer.add_metadata("adoption_privileges", False)

            # Send suspension notification
            await self._send_suspension_notification(customer, suspension_reason)

            self.logger.info(
                f"Customer suspension {customer.technical_id} processed successfully"
            )
            return customer

        except Exception as e:
            self.logger.error(f"Error processing customer suspension: {str(e)}")
            raise

    async def _cancel_active_reservations(self, customer: Customer) -> None:
        """Cancel active reservations (simulated)."""
        self.logger.info(
            f"Active reservations cancelled for customer {customer.technical_id}"
        )

    async def _send_suspension_notification(
        self, customer: Customer, reason: str
    ) -> None:
        """Send suspension notification (simulated)."""
        self.logger.info(f"Suspension notification sent to {customer.email}: {reason}")


class CustomerReinstateProcessor(CyodaProcessor):
    """
    Processor for Customer reinstatement.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerReinstateProcessor",
            description="Processes customer reinstatement",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer reinstatement according to functional requirements.
        """
        try:
            customer = cast_entity(entity, Customer)

            # Review suspension reason
            suspension_reason = customer.get_metadata("suspension_reason")
            self.logger.info(
                f"Reviewing suspension for customer {customer.technical_id}: {suspension_reason}"
            )

            # Restore adoption privileges
            customer.add_metadata("adoption_privileges", True)
            customer.add_metadata(
                "reinstatement_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # Clear suspension flags
            if customer.metadata:
                customer.metadata.pop("suspension_reason", None)
                customer.metadata.pop("suspension_date", None)

            # Send reinstatement notification
            await self._send_reinstatement_notification(customer)

            self.logger.info(
                f"Customer reinstatement {customer.technical_id} processed successfully"
            )
            return customer

        except Exception as e:
            self.logger.error(f"Error processing customer reinstatement: {str(e)}")
            raise

    async def _send_reinstatement_notification(self, customer: Customer) -> None:
        """Send reinstatement notification (simulated)."""
        self.logger.info(f"Reinstatement notification sent to {customer.email}")


class CustomerDeactivationProcessor(CyodaProcessor):
    """
    Processor for Customer deactivation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerDeactivationProcessor",
            description="Processes customer deactivation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer deactivation according to functional requirements.
        """
        try:
            customer = cast_entity(entity, Customer)

            # Archive customer data
            customer.add_metadata(
                "deactivation_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            customer.add_metadata("data_archived", True)

            # Cancel active applications (simulated)
            await self._cancel_active_applications(customer)

            # Clear personal information if required (simulated)
            await self._clear_personal_information(customer)

            # Send deactivation confirmation
            await self._send_deactivation_confirmation(customer)

            self.logger.info(
                f"Customer deactivation {customer.technical_id} processed successfully"
            )
            return customer

        except Exception as e:
            self.logger.error(f"Error processing customer deactivation: {str(e)}")
            raise

    async def _cancel_active_applications(self, customer: Customer) -> None:
        """Cancel active applications (simulated)."""
        self.logger.info(
            f"Active applications cancelled for customer {customer.technical_id}"
        )

    async def _clear_personal_information(self, customer: Customer) -> None:
        """Clear personal information if required (simulated)."""
        self.logger.info(
            f"Personal information cleared for customer {customer.technical_id}"
        )

    async def _send_deactivation_confirmation(self, customer: Customer) -> None:
        """Send deactivation confirmation (simulated)."""
        self.logger.info(f"Deactivation confirmation sent to {customer.email}")
