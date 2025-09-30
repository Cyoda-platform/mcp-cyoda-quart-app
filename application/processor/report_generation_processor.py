"""
ReportGenerationProcessor for Pet Store Performance Analysis System

Handles generation of weekly performance reports by aggregating product data
and creating insights as specified in the functional requirements.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from application.entity.report.version_1.report import Report
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that generates weekly performance reports
    by analyzing product data and creating actionable insights.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates weekly performance reports with product analysis and insights",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to generate comprehensive performance analysis.

        Args:
            entity: The Report entity to populate with data
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with generated report content
        """
        try:
            self.logger.info(
                f"Generating report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Get all analyzed products for the report period
            products = await self._get_analyzed_products()
            
            # Generate report content
            await self._populate_report_data(report, products)
            
            # Create executive summary
            self._generate_executive_summary(report)
            
            # Mark report as generated
            report.mark_generated()

            self.logger.info(
                f"Report {report.technical_id} generated successfully with {len(products)} products"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_analyzed_products(self) -> List[Product]:
        """
        Retrieve all products that have been analyzed for inclusion in the report.
        
        Returns:
            List of analyzed Product entities
        """
        entity_service = get_entity_service()
        
        try:
            # Search for products in 'analyzed' or 'completed' state
            builder = SearchConditionRequest.builder()
            builder.equals("state", "analyzed")
            condition = builder.build()
            
            analyzed_results = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )
            
            # Also get completed products
            builder = SearchConditionRequest.builder()
            builder.equals("state", "completed")
            condition = builder.build()
            
            completed_results = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )
            
            # Combine results and convert to Product entities
            all_results = analyzed_results + completed_results
            products = []
            
            for result in all_results:
                try:
                    product = cast_entity(result.data, Product)
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to cast product entity: {str(e)}")
                    continue
            
            self.logger.info(f"Retrieved {len(products)} analyzed products for report")
            return products
            
        except Exception as e:
            self.logger.error(f"Error retrieving analyzed products: {str(e)}")
            return []

    async def _populate_report_data(self, report: Report, products: List[Product]) -> None:
        """
        Populate the report with aggregated product data and insights.
        
        Args:
            report: The Report entity to populate
            products: List of analyzed products
        """
        report.total_products_analyzed = len(products)
        
        if not products:
            self.logger.warning("No products available for report generation")
            return
        
        # Calculate total revenue
        total_revenue = sum(p.revenue or 0.0 for p in products)
        report.total_revenue = total_revenue
        
        # Identify top performers (performance score >= 80)
        top_performers = [p for p in products if p.is_high_performer()]
        for product in sorted(top_performers, key=lambda x: x.performance_score or 0, reverse=True)[:5]:
            report.add_top_performer({
                "name": product.name,
                "category": product.category,
                "performance_score": product.performance_score,
                "sales_volume": product.sales_volume,
                "revenue": product.revenue
            })
        
        # Identify underperformers (performance score < 40)
        underperformers = [p for p in products if p.is_underperforming()]
        for product in sorted(underperformers, key=lambda x: x.performance_score or 0)[:5]:
            report.add_underperformer({
                "name": product.name,
                "category": product.category,
                "performance_score": product.performance_score,
                "sales_volume": product.sales_volume,
                "revenue": product.revenue
            })
        
        # Identify products needing restocking
        restock_needed = [p for p in products if p.requires_restocking]
        for product in restock_needed:
            report.add_restock_recommendation({
                "name": product.name,
                "category": product.category,
                "inventory_level": product.inventory_level,
                "sales_volume": product.sales_volume,
                "urgency": "high" if (product.inventory_level or 0) < 5 else "medium"
            })
        
        # Calculate revenue growth (simplified - comparing against a baseline)
        baseline_revenue = len(products) * 250  # Assume $250 average per product
        if baseline_revenue > 0:
            growth = ((total_revenue - baseline_revenue) / baseline_revenue) * 100
            report.revenue_growth = round(growth, 2)

    def _generate_executive_summary(self, report: Report) -> None:
        """
        Generate an executive summary based on the report data.
        
        Args:
            report: The Report entity to update with summary
        """
        summary_parts = []
        
        # Overall performance
        total_products = report.total_products_analyzed or 0
        total_revenue = report.total_revenue or 0.0
        
        summary_parts.append(
            f"Weekly Performance Report: Analyzed {total_products} products "
            f"generating ${total_revenue:,.2f} in total revenue."
        )
        
        # Top performers
        top_count = len(report.top_performers or [])
        if top_count > 0:
            summary_parts.append(
                f"Identified {top_count} high-performing products driving strong sales."
            )
        
        # Underperformers
        under_count = len(report.underperformers or [])
        if under_count > 0:
            summary_parts.append(
                f"Found {under_count} underperforming products requiring attention."
            )
        
        # Restocking
        restock_count = len(report.restock_recommendations or [])
        if restock_count > 0:
            summary_parts.append(
                f"Urgent: {restock_count} products require immediate restocking."
            )
        
        # Revenue growth
        if report.revenue_growth is not None:
            if report.revenue_growth > 0:
                summary_parts.append(
                    f"Revenue growth of {report.revenue_growth:.1f}% compared to baseline."
                )
            else:
                summary_parts.append(
                    f"Revenue declined by {abs(report.revenue_growth):.1f}% - investigate market factors."
                )
        
        # Recommendations
        if restock_count > 0:
            summary_parts.append("Immediate action required for inventory management.")
        elif top_count > under_count:
            summary_parts.append("Overall positive performance trend - consider expanding successful products.")
        else:
            summary_parts.append("Mixed performance - focus on improving underperforming products.")
        
        report.executive_summary = " ".join(summary_parts)
