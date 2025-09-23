"""
PerformanceReportValidationCriterion for Product Performance Analysis System

Validates PerformanceReport entities for completeness and business rules
before report generation as specified in functional requirements.
"""

from datetime import datetime
from typing import Any

from application.entity.performance_report.version_1.performance_report import (
    PerformanceReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PerformanceReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for PerformanceReport entities.

    Checks report metadata, period validity, and required fields before
    allowing PerformanceReport entities to proceed to report generation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PerformanceReportValidationCriterion",
            description="Validates PerformanceReport entities for completeness and business rules",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the PerformanceReport entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be PerformanceReport)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating PerformanceReport entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to PerformanceReport for type-safe operations
            report = cast_entity(entity, PerformanceReport)

            # Validate required fields
            if not self._validate_required_fields(report):
                return False

            # Validate report period
            if not self._validate_report_period(report):
                return False

            # Validate field constraints
            if not self._validate_field_constraints(report):
                return False

            # Validate business rules
            if not self._validate_business_rules(report):
                return False

            self.logger.info(
                f"PerformanceReport entity {report.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, report: PerformanceReport) -> bool:
        """
        Validate that all required fields are present and non-empty.

        Args:
            report: The PerformanceReport entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate report_title
        if not report.report_title or len(report.report_title.strip()) == 0:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid report_title: '{report.report_title}'"
            )
            return False

        # Validate report period dates
        if (
            not report.report_period_start
            or len(report.report_period_start.strip()) == 0
        ):
            self.logger.warning(
                f"Entity {report.technical_id} has invalid report_period_start: '{report.report_period_start}'"
            )
            return False

        if not report.report_period_end or len(report.report_period_end.strip()) == 0:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid report_period_end: '{report.report_period_end}'"
            )
            return False

        # Validate executive_summary
        if not report.executive_summary or len(report.executive_summary.strip()) == 0:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid executive_summary: '{report.executive_summary}'"
            )
            return False

        return True

    def _validate_report_period(self, report: PerformanceReport) -> bool:
        """
        Validate the report period dates are valid and logical.

        Args:
            report: The PerformanceReport entity to validate

        Returns:
            True if report period is valid, False otherwise
        """
        try:
            # Parse the dates
            start_date = datetime.fromisoformat(
                report.report_period_start.replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(
                report.report_period_end.replace("Z", "+00:00")
            )

            # Check that end date is after start date
            if end_date <= start_date:
                self.logger.warning(
                    f"Entity {report.technical_id} has invalid report period: "
                    f"end date ({report.report_period_end}) must be after start date ({report.report_period_start})"
                )
                return False

            # Check that the period is not too long (e.g., more than 1 year)
            period_days = (end_date - start_date).days
            if period_days > 365:
                self.logger.warning(
                    f"Entity {report.technical_id} has excessively long report period: {period_days} days"
                )
                return False

            # Check that the period is not too short (e.g., less than 1 day)
            if period_days < 1:
                self.logger.warning(
                    f"Entity {report.technical_id} has too short report period: {period_days} days"
                )
                return False

            # Check that the report period is not in the future
            current_date = datetime.now(start_date.tzinfo)
            if start_date > current_date:
                self.logger.warning(
                    f"Entity {report.technical_id} has future report period start date: {report.report_period_start}"
                )
                return False

            return True

        except ValueError as e:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid date format in report period: {str(e)}"
            )
            return False

    def _validate_field_constraints(self, report: PerformanceReport) -> bool:
        """
        Validate field constraints and formats.

        Args:
            report: The PerformanceReport entity to validate

        Returns:
            True if all field constraints are met, False otherwise
        """
        # Validate numeric fields are non-negative
        if report.total_products_analyzed < 0:
            self.logger.warning(
                f"Entity {report.technical_id} has negative total_products_analyzed: {report.total_products_analyzed}"
            )
            return False

        if report.total_revenue < 0:
            self.logger.warning(
                f"Entity {report.technical_id} has negative total_revenue: {report.total_revenue}"
            )
            return False

        if report.total_sales_volume < 0:
            self.logger.warning(
                f"Entity {report.technical_id} has negative total_sales_volume: {report.total_sales_volume}"
            )
            return False

        if report.average_inventory_turnover < 0:
            self.logger.warning(
                f"Entity {report.technical_id} has negative average_inventory_turnover: {report.average_inventory_turnover}"
            )
            return False

        # Validate report format
        if report.report_format not in ["pdf", "html", "json"]:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid report_format: '{report.report_format}'"
            )
            return False

        # Validate report status
        if report.report_status not in ["draft", "finalized", "sent", "failed"]:
            self.logger.warning(
                f"Entity {report.technical_id} has invalid report_status: '{report.report_status}'"
            )
            return False

        # Validate email recipients
        for recipient in report.email_recipients:
            if "@" not in recipient:
                self.logger.warning(
                    f"Entity {report.technical_id} has invalid email recipient: '{recipient}'"
                )
                return False

        return True

    def _validate_business_rules(self, report: PerformanceReport) -> bool:
        """
        Validate business rules and logical constraints.

        Args:
            report: The PerformanceReport entity to validate

        Returns:
            True if all business rules are satisfied, False otherwise
        """
        # Business rule: If products were analyzed, there should be some data
        if report.total_products_analyzed > 0:
            # Should have at least some revenue or sales volume
            if report.total_revenue == 0 and report.total_sales_volume == 0:
                self.logger.warning(
                    f"Entity {report.technical_id} analyzed {report.total_products_analyzed} products "
                    f"but has zero revenue and sales volume"
                )
                # This might be valid for new products, so just warn

        # Business rule: List sizes should be reasonable
        if len(report.highest_selling_products) > 50:
            self.logger.warning(
                f"Entity {report.technical_id} has excessive number of highest selling products: "
                f"{len(report.highest_selling_products)}"
            )
            return False

        if len(report.slow_moving_inventory) > 100:
            self.logger.warning(
                f"Entity {report.technical_id} has excessive number of slow moving items: "
                f"{len(report.slow_moving_inventory)}"
            )
            return False

        if len(report.items_requiring_restock) > 100:
            self.logger.warning(
                f"Entity {report.technical_id} has excessive number of restock items: "
                f"{len(report.items_requiring_restock)}"
            )
            return False

        # Business rule: Email should be sent only for finalized reports
        if report.email_sent and report.report_status != "sent":
            self.logger.warning(
                f"Entity {report.technical_id} is marked as email_sent but status is not 'sent': "
                f"'{report.report_status}'"
            )
            return False

        # Business rule: Data sources should be valid
        valid_sources = ["petstore_api", "petstore_mock", "manual_entry"]
        for source in report.data_sources:
            if source not in valid_sources:
                self.logger.warning(
                    f"Entity {report.technical_id} has invalid data source: '{source}'"
                )
                return False

        return True
