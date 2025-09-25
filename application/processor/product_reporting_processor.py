"""
ProductReportingProcessor for Pet Store Performance Analysis System

Handles product reporting tasks including creating Report entities for analyzed products
and triggering report generation workflows as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.product.version_1.product import Product
from application.entity.report.version_1.report import Report
from services.services import get_entity_service


class ProductReportingProcessor(CyodaProcessor):
    """
    Processor for Product entity that handles reporting tasks,
    creates Report entities, and triggers report generation workflows.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductReportingProcessor",
            description="Handles product reporting and creates Report entities for analyzed products",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process product for reporting and create/update Report entities.

        Args:
            entity: The Product entity to process for reporting
            **kwargs: Additional processing parameters

        Returns:
            The processed product entity
        """
        try:
            self.logger.info(
                f"Processing product for reporting: {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Check if we need to create a new weekly report
            await self._ensure_weekly_report_exists(product)

            # Add product data to existing reports
            await self._add_product_to_reports(product)

            self.logger.info(
                f"Product {product.technical_id} processed for reporting successfully"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error processing product for reporting {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _ensure_weekly_report_exists(self, product: Product) -> None:
        """
        Ensure a weekly report exists for the current week.

        Args:
            product: The Product entity being processed
        """
        entity_service = get_entity_service()
        
        # Calculate current week's date range
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday
        
        week_start_str = week_start.isoformat().replace("+00:00", "Z")
        week_end_str = week_end.isoformat().replace("+00:00", "Z")

        try:
            # Check if a report already exists for this week
            # This is a simplified check - in a real system you'd search by date range
            report_title = f"Weekly Performance Report - {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
            
            # Create a new weekly report
            report = Report(
                report_title=report_title,
                report_period_start=week_start_str,
                report_period_end=week_end_str,
                report_type="WEEKLY",
                executive_summary="Weekly performance analysis report generated automatically",
                total_products_analyzed=0,
                total_revenue=0.0,
                recipient_email="victoria.sagdieva@cyoda.com",
                email_status="PENDING"
            )

            # Convert to dict for EntityService
            report_data = report.model_dump(by_alias=True)

            # Save the new Report
            response = await entity_service.save(
                entity=report_data,
                entity_class=Report.ENTITY_NAME,
                entity_version=str(Report.ENTITY_VERSION),
            )

            created_report_id = response.metadata.id
            self.logger.info(f"Created new weekly report {created_report_id}")

        except Exception as e:
            self.logger.error(f"Failed to create weekly report: {str(e)}")
            # Continue processing even if report creation fails

    async def _add_product_to_reports(self, product: Product) -> None:
        """
        Add product data to existing reports based on performance.

        Args:
            product: The Product entity to add to reports
        """
        entity_service = get_entity_service()

        try:
            # Get all pending reports (simplified - in real system would filter by date)
            reports = await entity_service.find_all(
                entity_class=Report.ENTITY_NAME,
                entity_version=str(Report.ENTITY_VERSION),
            )

            for report_response in reports:
                try:
                    # Cast to Report entity
                    report = cast_entity(report_response.data, Report)
                    
                    # Only update reports that are still pending
                    if report.email_status != "PENDING":
                        continue

                    # Prepare product data for report
                    product_data = {
                        "product_id": product.product_id,
                        "name": product.name,
                        "category": product.category,
                        "sales_volume": product.sales_volume or 0,
                        "revenue": product.revenue or 0.0,
                        "performance_score": product.performance_score or 0.0,
                        "trend_indicator": product.trend_indicator,
                        "inventory_level": product.inventory_level or 0,
                        "status": product.status
                    }

                    # Categorize product based on performance
                    updated = False
                    
                    # High performers (score >= 70)
                    if (product.performance_score or 0.0) >= 70.0:
                        if report.top_performing_products is None:
                            report.top_performing_products = []
                        report.top_performing_products.append(product_data)
                        updated = True
                    
                    # Low performers (score < 40)
                    elif (product.performance_score or 0.0) < 40.0:
                        if report.underperforming_products is None:
                            report.underperforming_products = []
                        report.underperforming_products.append(product_data)
                        updated = True
                    
                    # Low stock items
                    if product.is_low_stock():
                        if report.low_stock_items is None:
                            report.low_stock_items = []
                        report.low_stock_items.append(product_data)
                        updated = True

                    # Update report totals
                    if updated:
                        report.total_products_analyzed = (report.total_products_analyzed or 0) + 1
                        report.total_revenue = (report.total_revenue or 0.0) + (product.revenue or 0.0)

                        # Update the report
                        report_data = report.model_dump(by_alias=True)
                        await entity_service.update(
                            entity_id=report.technical_id or report.entity_id,
                            entity=report_data,
                            entity_class=Report.ENTITY_NAME,
                            entity_version=str(Report.ENTITY_VERSION),
                        )

                        self.logger.info(
                            f"Updated report {report.technical_id} with product {product.product_id}"
                        )

                except Exception as e:
                    self.logger.error(f"Failed to update report: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to retrieve reports for updating: {str(e)}")
            # Continue processing even if report updates fail
