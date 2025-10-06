"""
ReportValidationCriterion for Booking Report Generation

Validates that a Report entity meets all required business rules before it can
proceed to report generation stage as specified in functional requirements.
"""

from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks all business rules
    before the entity can proceed to report generation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report entity business rules and configuration",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the report entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating report entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report_entity = cast_entity(entity, Report)

            # State is managed by Cyoda workflow engine - no manual state checks needed

            # Validate required fields
            if not report_entity.title or len(report_entity.title.strip()) < 3:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has invalid title: '{report_entity.title}'"
                )
                return False

            if len(report_entity.title) > 200:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has title that is too long: {len(report_entity.title)} characters"
                )
                return False

            # Validate report type
            allowed_report_types = ["summary", "filtered", "date_range", "custom"]
            if report_entity.report_type not in allowed_report_types:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has invalid report type: {report_entity.report_type}"
                )
                return False

            # Validate display format
            allowed_display_formats = ["table", "chart", "json", "csv"]
            if report_entity.display_format not in allowed_display_formats:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has invalid display format: {report_entity.display_format}"
                )
                return False

            # Validate filter criteria if present
            if report_entity.filter_criteria:
                if not isinstance(report_entity.filter_criteria, dict):
                    self.logger.warning(
                        f"Report {report_entity.technical_id} has invalid filter criteria format"
                    )
                    return False

                # Validate specific filter criteria
                valid_filter_keys = [
                    "depositpaid",
                    "min_price",
                    "max_price",
                    "start_date",
                    "end_date",
                    "firstname",
                    "lastname",
                ]

                for key in report_entity.filter_criteria.keys():
                    if key not in valid_filter_keys:
                        self.logger.warning(
                            f"Report {report_entity.technical_id} has invalid filter key: {key}"
                        )
                        return False

                # Validate date filters if present
                if (
                    "start_date" in report_entity.filter_criteria
                    or "end_date" in report_entity.filter_criteria
                ):
                    start_date = report_entity.filter_criteria.get("start_date")
                    end_date = report_entity.filter_criteria.get("end_date")

                    if start_date and end_date:
                        try:
                            from datetime import datetime

                            start = datetime.strptime(start_date, "%Y-%m-%d")
                            end = datetime.strptime(end_date, "%Y-%m-%d")

                            if end <= start:
                                self.logger.warning(
                                    f"Report {report_entity.technical_id} has invalid date range: "
                                    f"end_date ({end_date}) must be after start_date ({start_date})"
                                )
                                return False

                        except ValueError as e:
                            self.logger.warning(
                                f"Report {report_entity.technical_id} has invalid date format in filters: {str(e)}"
                            )
                            return False

                # Validate price filters if present
                min_price = report_entity.filter_criteria.get("min_price")
                max_price = report_entity.filter_criteria.get("max_price")

                if min_price is not None and min_price < 0:
                    self.logger.warning(
                        f"Report {report_entity.technical_id} has negative min_price: {min_price}"
                    )
                    return False

                if max_price is not None and max_price < 0:
                    self.logger.warning(
                        f"Report {report_entity.technical_id} has negative max_price: {max_price}"
                    )
                    return False

                if (
                    min_price is not None
                    and max_price is not None
                    and max_price <= min_price
                ):
                    self.logger.warning(
                        f"Report {report_entity.technical_id} has invalid price range: "
                        f"max_price ({max_price}) must be greater than min_price ({min_price})"
                    )
                    return False

            # Validate description if present
            if report_entity.description and len(report_entity.description) > 1000:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has description that is too long: {len(report_entity.description)} characters"
                )
                return False

            # Validate data source
            if (
                not report_entity.data_source
                or len(report_entity.data_source.strip()) == 0
            ):
                self.logger.warning(
                    f"Report {report_entity.technical_id} has invalid data source"
                )
                return False

            # Business logic validation
            # For date_range reports, we should have date criteria
            if report_entity.report_type == "date_range":
                if not report_entity.filter_criteria or (
                    "start_date" not in report_entity.filter_criteria
                    and "end_date" not in report_entity.filter_criteria
                ):
                    self.logger.warning(
                        f"Report {report_entity.technical_id} is date_range type but lacks date criteria"
                    )
                    # This is a warning, not a hard failure
                    # return False

            # For filtered reports, we should have some filter criteria
            if report_entity.report_type == "filtered":
                if not report_entity.filter_criteria:
                    self.logger.warning(
                        f"Report {report_entity.technical_id} is filtered type but lacks filter criteria"
                    )
                    # This is a warning, not a hard failure
                    # return False

            self.logger.info(
                f"Report {report_entity.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating report entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
