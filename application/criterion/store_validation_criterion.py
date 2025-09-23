"""
StoreValidationCriterion for Product Performance Analysis and Reporting System

Validates that a Store entity meets all required business rules before it can
proceed to the inventory synchronization stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.store.version_1.store import Store


class StoreValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Store entity that checks all business rules
    before the entity can proceed to inventory synchronization stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreValidationCriterion",
            description="Validates Store entity business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Store entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Store)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Store entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Validate required fields
            if not self._validate_required_fields(store):
                return False

            # Validate field formats and constraints
            if not self._validate_field_constraints(store):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(store):
                return False

            self.logger.info(
                f"Store entity {store.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Store entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, store: Store) -> bool:
        """Validate that all required fields are present and valid"""
        
        # Store name is required
        if not store.store_name or len(store.store_name.strip()) == 0:
            self.logger.warning(f"Store {store.technical_id} has empty store name")
            return False

        if len(store.store_name) > 255:
            self.logger.warning(f"Store {store.technical_id} name too long: {len(store.store_name)} characters")
            return False

        return True

    def _validate_field_constraints(self, store: Store) -> bool:
        """Validate field formats and constraints"""
        
        # Validate email format if present
        if store.email:
            if "@" not in store.email or "." not in store.email:
                self.logger.warning(f"Store {store.technical_id} has invalid email format: {store.email}")
                return False

        # Validate phone format if present
        if store.phone:
            # Remove common formatting characters and check length
            cleaned_phone = ''.join(c for c in store.phone if c.isdigit())
            if len(cleaned_phone) < 10:
                self.logger.warning(f"Store {store.technical_id} has invalid phone number: {store.phone}")
                return False

        # Validate inventory data if present
        if store.inventory_data:
            if not isinstance(store.inventory_data, dict):
                self.logger.warning(f"Store {store.technical_id} has invalid inventory data format")
                return False
            
            # Check for negative values
            for status, count in store.inventory_data.items():
                if not isinstance(count, int) or count < 0:
                    self.logger.warning(
                        f"Store {store.technical_id} has invalid inventory count for {status}: {count}"
                    )
                    return False

        # Validate pet counts if present
        for field_name, field_value in [
            ("total_pets", store.total_pets),
            ("available_pets", store.available_pets),
            ("pending_pets", store.pending_pets),
            ("sold_pets", store.sold_pets),
        ]:
            if field_value is not None and (not isinstance(field_value, int) or field_value < 0):
                self.logger.warning(
                    f"Store {store.technical_id} has invalid {field_name}: {field_value}"
                )
                return False

        return True

    def _validate_business_rules(self, store: Store) -> bool:
        """Validate business logic rules"""
        
        # Business rule: If inventory data exists, pet counts should be consistent
        if store.inventory_data and isinstance(store.inventory_data, dict):
            calculated_total = (
                store.inventory_data.get("available", 0) +
                store.inventory_data.get("pending", 0) +
                store.inventory_data.get("sold", 0)
            )
            
            if store.total_pets is not None and store.total_pets != calculated_total:
                self.logger.warning(
                    f"Store {store.technical_id} has inconsistent pet counts. "
                    f"Total pets: {store.total_pets}, Calculated from inventory: {calculated_total}"
                )
                # This is a warning, not a failure - the processor can recalculate

        # Business rule: Available pets should not exceed total pets
        if (store.total_pets is not None and store.available_pets is not None and 
            store.available_pets > store.total_pets):
            self.logger.warning(
                f"Store {store.technical_id} has more available pets ({store.available_pets}) "
                f"than total pets ({store.total_pets})"
            )
            return False

        # Business rule: Store should have some form of contact information
        if not any([store.address, store.phone, store.email]):
            self.logger.warning(
                f"Store {store.technical_id} has no contact information (address, phone, or email)"
            )
            # This is a warning, not a failure - store can still be processed

        return True
