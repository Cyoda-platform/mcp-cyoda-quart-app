"""
ValidateHnItemProcessor for Cyoda Client Application

Validates HN item data against Firebase HN API schema and business rules.
Performs comprehensive validation including type-specific rules and relationship checks.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ValidateHnItemProcessor(CyodaProcessor):
    """
    Processor for validating HN items against Firebase HN API schema and business rules.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validate_hn_item_processor",
            description="Validates HN item data against Firebase HN API schema and business rules",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Validate the HN item according to functional requirements.

        Args:
            entity: The HnItem to validate
            **kwargs: Additional processing parameters

        Returns:
            The entity with validation results
        """
        try:
            self.logger.info(
                f"Validating HnItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Perform validation
            validation_errors = await self._validate_item(hn_item)

            # Store validation results
            if validation_errors:
                hn_item.set_validation_result("failed", validation_errors)
                self.logger.warning(
                    f"HnItem {hn_item.id} validation failed: {validation_errors}"
                )
            else:
                hn_item.set_validation_result("passed")
                self.logger.info(f"HnItem {hn_item.id} validation passed successfully")

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error validating HnItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_item(self, item: HnItem) -> list[str]:
        """
        Perform comprehensive validation of the HN item.

        Args:
            item: The HnItem to validate

        Returns:
            List of validation errors (empty if valid)
        """
        validation_errors = []

        # Validate required fields
        if not item.id:
            validation_errors.append("ID is required")

        if not item.type or item.type not in HnItem.ALLOWED_TYPES:
            validation_errors.append(
                f"Invalid or missing type. Must be one of: {HnItem.ALLOWED_TYPES}"
            )

        # Validate type-specific rules
        await self._validate_type_specific_rules(item, validation_errors)

        # Validate relationships
        await self._validate_relationships(item, validation_errors)

        # Validate business rules
        self._validate_business_rules(item, validation_errors)

        return validation_errors

    async def _validate_type_specific_rules(
        self, item: HnItem, validation_errors: list[str]
    ) -> None:
        """Validate type-specific business rules"""
        if item.type == "comment":
            # Comments should have a parent (but we'll be lenient for top-level comments)
            if item.parent is None:
                self.logger.info(
                    f"Comment {item.id} has no parent - may be a top-level comment"
                )

        elif item.type == "pollopt":
            # Poll options must reference a poll
            if item.poll is None:
                validation_errors.append("Poll options must reference a poll")

        elif item.type == "poll":
            # Polls should have parts (poll options)
            if not item.parts:
                self.logger.info(f"Poll {item.id} has no parts - may be empty poll")

        elif item.type in ["story", "job"]:
            # Stories and jobs should have titles
            if not item.title:
                validation_errors.append(
                    f"{item.type.capitalize()}s should have a title"
                )

    async def _validate_relationships(
        self, item: HnItem, validation_errors: list[str]
    ) -> None:
        """Validate item relationships"""
        entity_service = get_entity_service()

        try:
            # Validate parent relationship
            if item.parent:
                parent_exists = await self._item_exists(entity_service, item.parent)
                if not parent_exists:
                    validation_errors.append(
                        f"Parent item {item.parent} does not exist"
                    )

            # Validate kids relationships
            if item.kids:
                for kid_id in item.kids:
                    kid_exists = await self._item_exists(entity_service, kid_id)
                    if not kid_exists:
                        validation_errors.append(f"Child item {kid_id} does not exist")

            # Validate poll relationship
            if item.poll:
                poll_exists = await self._item_exists(entity_service, item.poll)
                if not poll_exists:
                    validation_errors.append(f"Poll item {item.poll} does not exist")

            # Validate parts relationships
            if item.parts:
                for part_id in item.parts:
                    part_exists = await self._item_exists(entity_service, part_id)
                    if not part_exists:
                        validation_errors.append(
                            f"Poll option {part_id} does not exist"
                        )

        except Exception as e:
            self.logger.warning(
                f"Error validating relationships for item {item.id}: {str(e)}"
            )
            # Don't fail validation for relationship check errors, just log them

    def _validate_business_rules(
        self, item: HnItem, validation_errors: list[str]
    ) -> None:
        """Validate business rules"""
        # Only certain types can have scores
        if item.score is not None and item.type not in [
            "story",
            "poll",
            "job",
            "pollopt",
        ]:
            validation_errors.append(f"Type {item.type} cannot have a score")

        # Only comments can have parents
        if item.parent is not None and item.type != "comment":
            validation_errors.append(
                f"Only comments can have parents, but {item.type} has parent {item.parent}"
            )

        # Only poll options can reference polls
        if item.poll is not None and item.type != "pollopt":
            validation_errors.append(
                f"Only poll options can reference polls, but {item.type} references poll {item.poll}"
            )

        # Only polls can have parts
        if item.parts is not None and item.type != "poll":
            validation_errors.append(
                f"Only polls can have parts, but {item.type} has parts"
            )

        # Validate source
        if item.source and item.source not in HnItem.ALLOWED_SOURCES:
            validation_errors.append(
                f"Invalid source. Must be one of: {HnItem.ALLOWED_SOURCES}"
            )

    async def _item_exists(self, entity_service: Any, item_id: int) -> bool:
        """Check if an item exists by searching for it"""
        try:
            # Search for item by HN ID
            from common.service.entity_service import SearchConditionRequest

            builder = SearchConditionRequest.builder()
            builder.equals("id", str(item_id))
            condition = builder.build()

            results = await entity_service.search(
                entity_class=HnItem.ENTITY_NAME,
                condition=condition,
                entity_version=str(HnItem.ENTITY_VERSION),
            )

            return len(results) > 0

        except Exception as e:
            self.logger.warning(f"Error checking if item {item_id} exists: {str(e)}")
            return False  # Assume doesn't exist if we can't check
