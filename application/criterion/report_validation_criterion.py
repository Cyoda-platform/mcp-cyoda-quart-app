"""
ReportValidationCriterion for Pet Store Performance Analysis System

Validates that Report entities are complete, accurate, and ready for email dispatch
as specified in functional requirements for automated reporting.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.report.version_1.report import Report


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks completeness,
    data quality, and readiness for email dispatch.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report entity completeness and quality before email dispatch",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate required fields
            if not self._validate_required_fields(report):
                return False

            # Validate report content completeness
            if not self._validate_content_completeness(report):
                return False

            # Validate data quality
            if not self._validate_data_quality(report):
                return False

            # Validate email configuration
            if not self._validate_email_configuration(report):
                return False

            # Validate business logic
            if not self._validate_business_logic(report):
                return False

            self.logger.info(
                f"Report {report.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, report: Report) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            report: The Report entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate report title
        if not report.report_title or len(report.report_title.strip()) == 0:
            self.logger.warning(f"Report {report.technical_id} has invalid title")
            return False

        # Validate report period
        if not report.report_period_start or not report.report_period_end:
            self.logger.warning(f"Report {report.technical_id} has invalid reporting period")
            return False

        # Validate report type
        if report.report_type not in report.ALLOWED_REPORT_TYPES:
            self.logger.warning(f"Report {report.technical_id} has invalid report type: {report.report_type}")
            return False

        # Validate recipient email
        if not report.recipient_email or "@" not in report.recipient_email:
            self.logger.warning(f"Report {report.technical_id} has invalid recipient email")
            return False

        return True

    def _validate_content_completeness(self, report: Report) -> bool:
        """
        Validate that report content is complete and meaningful.

        Args:
            report: The Report entity to validate

        Returns:
            True if content is complete, False otherwise
        """
        # Validate executive summary
        if not report.executive_summary or len(report.executive_summary.strip()) < 50:
            self.logger.warning(f"Report {report.technical_id} has insufficient executive summary")
            return False

        # Validate that report has analyzed some products
        if (report.total_products_analyzed or 0) == 0:
            self.logger.warning(f"Report {report.technical_id} has no products analyzed")
            return False

        # Validate that report data exists
        if not report.report_data:
            self.logger.warning(f"Report {report.technical_id} has no report data")
            return False

        # Check for at least some product data
        has_product_data = (
            (report.top_performing_products and len(report.top_performing_products) > 0) or
            (report.underperforming_products and len(report.underperforming_products) > 0) or
            (report.low_stock_items and len(report.low_stock_items) > 0)
        )

        if not has_product_data:
            self.logger.warning(f"Report {report.technical_id} has no product data")
            return False

        return True

    def _validate_data_quality(self, report: Report) -> bool:
        """
        Validate data quality and consistency.

        Args:
            report: The Report entity to validate

        Returns:
            True if data quality is acceptable, False otherwise
        """
        # Validate numeric fields
        if report.total_revenue is not None and report.total_revenue < 0:
            self.logger.warning(f"Report {report.technical_id} has negative total revenue")
            return False

        if report.total_products_analyzed is not None and report.total_products_analyzed < 0:
            self.logger.warning(f"Report {report.technical_id} has negative products analyzed count")
            return False

        # Validate product data consistency
        if report.top_performing_products:
            for i, product in enumerate(report.top_performing_products):
                if not self._validate_product_data(product, f"top_performing[{i}]", report.technical_id):
                    return False

        if report.underperforming_products:
            for i, product in enumerate(report.underperforming_products):
                if not self._validate_product_data(product, f"underperforming[{i}]", report.technical_id):
                    return False

        if report.low_stock_items:
            for i, product in enumerate(report.low_stock_items):
                if not self._validate_product_data(product, f"low_stock[{i}]", report.technical_id):
                    return False

        return True

    def _validate_product_data(self, product_data: dict, context: str, report_id: str) -> bool:
        """
        Validate individual product data within the report.

        Args:
            product_data: Product data dictionary
            context: Context for logging (e.g., "top_performing[0]")
            report_id: Report technical ID for logging

        Returns:
            True if product data is valid, False otherwise
        """
        # Check required fields
        required_fields = ["product_id", "name", "category"]
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                self.logger.warning(f"Report {report_id} {context} missing required field: {field}")
                return False

        # Validate numeric fields
        numeric_fields = ["sales_volume", "revenue", "performance_score", "inventory_level"]
        for field in numeric_fields:
            if field in product_data and product_data[field] is not None:
                try:
                    value = float(product_data[field])
                    if value < 0 and field != "performance_score":  # Performance score can be 0
                        self.logger.warning(f"Report {report_id} {context} has negative {field}: {value}")
                        return False
                except (ValueError, TypeError):
                    self.logger.warning(f"Report {report_id} {context} has invalid {field}: {product_data[field]}")
                    return False

        return True

    def _validate_email_configuration(self, report: Report) -> bool:
        """
        Validate email configuration and status.

        Args:
            report: The Report entity to validate

        Returns:
            True if email configuration is valid, False otherwise
        """
        # Validate email status
        if report.email_status not in report.ALLOWED_EMAIL_STATUSES:
            self.logger.warning(f"Report {report.technical_id} has invalid email status: {report.email_status}")
            return False

        # Validate recipient email format (basic check)
        email = report.recipient_email
        if not email or "@" not in email or "." not in email.split("@")[1]:
            self.logger.warning(f"Report {report.technical_id} has invalid email format: {email}")
            return False

        # Check that email is pending (ready for dispatch)
        if report.email_status != "PENDING":
            self.logger.warning(f"Report {report.technical_id} email status is not PENDING: {report.email_status}")
            return False

        return True

    def _validate_business_logic(self, report: Report) -> bool:
        """
        Validate business logic rules.

        Args:
            report: The Report entity to validate

        Returns:
            True if business rules are satisfied, False otherwise
        """
        # Rule: Weekly reports should have reasonable product counts
        if report.report_type == "WEEKLY":
            total_products = report.total_products_analyzed or 0
            if total_products > 1000:  # Unreasonably high for weekly
                self.logger.warning(f"Report {report.technical_id} has suspiciously high product count: {total_products}")
                return False

        # Rule: Total revenue should be consistent with product data
        if report.total_revenue is not None and report.total_revenue > 0:
            # Calculate revenue from product lists
            calculated_revenue = 0.0
            
            for product_list in [report.top_performing_products, report.underperforming_products]:
                if product_list:
                    for product in product_list:
                        calculated_revenue += product.get("revenue", 0.0)
            
            # Allow for some difference due to rounding and partial data
            if calculated_revenue > 0 and abs(report.total_revenue - calculated_revenue) > report.total_revenue * 0.5:
                self.logger.warning(
                    f"Report {report.technical_id} has inconsistent revenue calculation: "
                    f"Reported: {report.total_revenue}, Calculated: {calculated_revenue}"
                )
                return False

        # Rule: Report should have generation timestamp
        if not report.generated_at:
            self.logger.warning(f"Report {report.technical_id} has no generation timestamp")
            return False

        return True
