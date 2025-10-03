"""
ReportGenerationProcessor for Pet Store Performance Analysis System

Generates weekly performance reports by analyzing Product data and creating
comprehensive insights as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from application.entity.report.version_1.report import Report
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that generates comprehensive performance reports
    by analyzing Product data and creating insights for the sales team.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates weekly performance reports from Product analysis data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to generate comprehensive performance analysis.

        Args:
            entity: The Report entity to populate with analysis
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with generated report content
        """
        try:
            self.logger.info(
                f"Generating Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Get all analyzed products
            products = await self._get_analyzed_products()
            
            if not products:
                self.logger.warning("No analyzed products found for report generation")
                report.executive_summary = "No product data available for analysis."
                report.update_generation_timestamp()
                return report

            # Generate report sections
            await self._generate_executive_summary(report, products)
            await self._identify_top_performers(report, products)
            await self._identify_underperformers(report, products)
            await self._generate_restock_recommendations(report, products)
            await self._calculate_analytics_data(report, products)

            # Update generation metadata
            report.products_analyzed = len(products)
            report.update_generation_timestamp()

            self.logger.info(
                f"Report {report.technical_id} generated successfully with {len(products)} products analyzed"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating Report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_analyzed_products(self) -> List[Product]:
        """
        Retrieve all products that have been analyzed (in analyzed or completed state).
        
        Returns:
            List of analyzed Product entities
        """
        entity_service = get_entity_service()
        
        try:
            # Search for products in analyzed or completed state
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
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error retrieving analyzed products: {str(e)}")
            return []

    async def _generate_executive_summary(self, report: Report, products: List[Product]) -> None:
        """Generate executive summary section of the report."""
        total_products = len(products)
        high_performers = [p for p in products if p.is_high_performer()]
        low_stock_products = [p for p in products if p.is_low_stock()]
        
        summary = f"""Weekly Performance Analysis Summary

Total Products Analyzed: {total_products}
High Performing Products: {len(high_performers)} ({len(high_performers)/total_products*100:.1f}%)
Products Requiring Attention: {len(low_stock_products)} ({len(low_stock_products)/total_products*100:.1f}%)

Key Insights:
- {len(high_performers)} products are exceeding performance expectations
- {len(low_stock_products)} products have low stock levels requiring restocking
- Analysis covers the period from {report.report_period_start} to {report.report_period_end}

This automated report provides actionable insights for inventory management and sales optimization."""

        report.executive_summary = summary

    async def _identify_top_performers(self, report: Report, products: List[Product]) -> None:
        """Identify and add top performing products to the report."""
        # Sort products by performance score (descending)
        sorted_products = sorted(
            [p for p in products if p.performance_score is not None],
            key=lambda x: x.performance_score or 0,
            reverse=True
        )
        
        # Take top 5 performers
        top_performers = sorted_products[:5]
        
        for product in top_performers:
            product_data = {
                "name": product.name,
                "category": product.category,
                "performanceScore": product.performance_score,
                "salesVolume": product.sales_volume,
                "revenue": product.revenue,
                "stockLevel": product.stock_level
            }
            report.add_top_performer(product_data)

    async def _identify_underperformers(self, report: Report, products: List[Product]) -> None:
        """Identify and add underperforming products to the report."""
        # Sort products by performance score (ascending)
        sorted_products = sorted(
            [p for p in products if p.performance_score is not None],
            key=lambda x: x.performance_score or 0
        )
        
        # Take bottom 5 performers with score < 50
        underperformers = [p for p in sorted_products if (p.performance_score or 0) < 50.0][:5]
        
        for product in underperformers:
            product_data = {
                "name": product.name,
                "category": product.category,
                "performanceScore": product.performance_score,
                "salesVolume": product.sales_volume,
                "revenue": product.revenue,
                "stockLevel": product.stock_level,
                "reason": "Low performance score"
            }
            report.add_underperformer(product_data)

    async def _generate_restock_recommendations(self, report: Report, products: List[Product]) -> None:
        """Generate restock recommendations based on stock levels and turnover."""
        restock_candidates = [p for p in products if p.needs_restocking()]
        
        for product in restock_candidates:
            product_data = {
                "name": product.name,
                "category": product.category,
                "currentStock": product.stock_level,
                "turnoverRate": product.inventory_turnover_rate,
                "salesVolume": product.sales_volume,
                "priority": "HIGH" if (product.inventory_turnover_rate or 0) > 5.0 else "MEDIUM"
            }
            report.add_restock_recommendation(product_data)

    async def _calculate_analytics_data(self, report: Report, products: List[Product]) -> None:
        """Calculate overall analytics data for the report."""
        total_revenue = sum(p.revenue or 0.0 for p in products)
        total_sales_volume = sum(p.sales_volume or 0 for p in products)
        
        # Calculate average performance score
        scores = [p.performance_score for p in products if p.performance_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        report.set_analytics_data(total_revenue, total_sales_volume, avg_score)
