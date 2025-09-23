"""
PerformanceReportGenerationProcessor for Product Performance Analysis System

Handles generation of weekly performance reports with analysis and insights
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service

from application.entity.performance_report.version_1.performance_report import PerformanceReport
from application.entity.product_data.version_1.product_data import ProductData


class PerformanceReportGenerationProcessor(CyodaProcessor):
    """
    Processor for generating performance reports.
    
    Aggregates product data, analyzes trends, and generates comprehensive
    weekly performance reports with insights and recommendations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PerformanceReportGenerationProcessor",
            description="Generates weekly performance reports with analysis and insights",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate a comprehensive performance report.

        Args:
            entity: The PerformanceReport entity to populate
            **kwargs: Additional processing parameters

        Returns:
            The entity with generated report data
        """
        try:
            self.logger.info(
                f"Starting report generation for PerformanceReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to PerformanceReport for type-safe operations
            report = cast_entity(entity, PerformanceReport)

            # Fetch all product data for analysis
            product_data_list = await self._fetch_product_data()
            
            # Generate report content
            await self._generate_executive_summary(report, product_data_list)
            await self._analyze_sales_trends(report, product_data_list)
            await self._analyze_inventory_status(report, product_data_list)
            await self._generate_insights_and_recommendations(report, product_data_list)
            
            # Calculate summary metrics
            report.calculate_summary_metrics([p.model_dump(by_alias=True) for p in product_data_list])

            self.logger.info(
                f"Generated performance report with {len(product_data_list)} products analyzed"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_product_data(self) -> List[ProductData]:
        """
        Fetch all available product data for analysis.

        Returns:
            List of ProductData entities
        """
        try:
            entity_service = get_entity_service()
            
            # Search for all ProductData entities
            search_response = await entity_service.search(
                entity_class=ProductData.ENTITY_NAME,
                entity_version=str(ProductData.ENTITY_VERSION),
                query={},
                page_size=1000
            )
            
            product_data_list = []
            if hasattr(search_response, 'entities') and search_response.entities:
                for entity_data in search_response.entities:
                    try:
                        # Convert entity data to ProductData instance
                        product_data = ProductData(**entity_data.entity)
                        product_data_list.append(product_data)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse product data: {str(e)}")
                        continue
            
            self.logger.info(f"Fetched {len(product_data_list)} product data entities for analysis")
            return product_data_list
            
        except Exception as e:
            self.logger.error(f"Error fetching product data: {str(e)}")
            # Return empty list if fetch fails
            return []

    async def _generate_executive_summary(self, report: PerformanceReport, product_data_list: List[ProductData]) -> None:
        """
        Generate executive summary for the report.

        Args:
            report: The PerformanceReport entity to update
            product_data_list: List of ProductData entities to analyze
        """
        total_products = len(product_data_list)
        total_revenue = sum(p.revenue or 0 for p in product_data_list)
        total_sales = sum(p.sales_volume or 0 for p in product_data_list)
        high_performers = len([p for p in product_data_list if p.is_high_performer])
        items_needing_restock = len([p for p in product_data_list if p.requires_restocking])
        slow_moving_items = len([p for p in product_data_list if p.is_slow_moving])
        
        # Calculate period dates
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        report.report_period_start = start_date.isoformat().replace("+00:00", "Z")
        report.report_period_end = end_date.isoformat().replace("+00:00", "Z")
        
        summary = f"""
        Weekly Product Performance Analysis Summary
        
        Reporting Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
        
        Key Metrics:
        • Total Products Analyzed: {total_products}
        • Total Revenue: ${total_revenue:,.2f}
        • Total Sales Volume: {total_sales:,} units
        • High-Performing Products: {high_performers} ({(high_performers/max(total_products,1)*100):.1f}%)
        • Items Requiring Restock: {items_needing_restock}
        • Slow-Moving Inventory Items: {slow_moving_items}
        
        This week's analysis shows {'strong' if high_performers > total_products * 0.3 else 'moderate' if high_performers > total_products * 0.15 else 'weak'} 
        overall performance with {'significant' if items_needing_restock > total_products * 0.2 else 'moderate' if items_needing_restock > total_products * 0.1 else 'minimal'} 
        inventory management attention required.
        """.strip()
        
        report.executive_summary = summary
        
        self.logger.info(f"Generated executive summary with {total_products} products analyzed")

    async def _analyze_sales_trends(self, report: PerformanceReport, product_data_list: List[ProductData]) -> None:
        """
        Analyze sales trends and identify top/bottom performers.

        Args:
            report: The PerformanceReport entity to update
            product_data_list: List of ProductData entities to analyze
        """
        # Sort products by sales volume (descending)
        sorted_by_sales = sorted(product_data_list, key=lambda p: p.sales_volume or 0, reverse=True)
        
        # Top 5 highest selling products
        top_performers = sorted_by_sales[:5]
        for product in top_performers:
            product_info = {
                "productId": product.product_id,
                "name": product.name,
                "category": product.category,
                "salesVolume": product.sales_volume or 0,
                "revenue": product.revenue or 0.0,
                "performanceScore": product.performance_score or 0.0
            }
            report.add_high_performing_product(product_info)
        
        # Identify slow-moving inventory
        slow_moving = [p for p in product_data_list if p.is_slow_moving]
        for product in slow_moving:
            product_info = {
                "productId": product.product_id,
                "name": product.name,
                "category": product.category,
                "salesVolume": product.sales_volume or 0,
                "stockLevel": product.stock_level or 0,
                "inventoryTurnover": product.inventory_turnover_rate or 0.0
            }
            report.add_slow_moving_product(product_info)
        
        self.logger.info(
            f"Analyzed sales trends: {len(top_performers)} top performers, "
            f"{len(slow_moving)} slow-moving items"
        )

    async def _analyze_inventory_status(self, report: PerformanceReport, product_data_list: List[ProductData]) -> None:
        """
        Analyze inventory status and identify restocking needs.

        Args:
            report: The PerformanceReport entity to update
            product_data_list: List of ProductData entities to analyze
        """
        # Identify items requiring restock
        restock_items = [p for p in product_data_list if p.requires_restocking]
        
        for product in restock_items:
            restock_info = {
                "productId": product.product_id,
                "name": product.name,
                "category": product.category,
                "currentStock": product.stock_level or 0,
                "salesVolume": product.sales_volume or 0,
                "urgency": "HIGH" if (product.stock_level or 0) < 5 else "MEDIUM" if (product.stock_level or 0) < 10 else "LOW"
            }
            report.add_restock_item(restock_info)
        
        self.logger.info(f"Identified {len(restock_items)} items requiring restock")

    async def _generate_insights_and_recommendations(self, report: PerformanceReport, product_data_list: List[ProductData]) -> None:
        """
        Generate business insights and recommendations.

        Args:
            report: The PerformanceReport entity to update
            product_data_list: List of ProductData entities to analyze
        """
        # Analyze category performance
        category_stats = {}
        for product in product_data_list:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "total_sales": 0,
                    "total_revenue": 0.0,
                    "high_performers": 0
                }
            
            category_stats[category]["count"] += 1
            category_stats[category]["total_sales"] += product.sales_volume or 0
            category_stats[category]["total_revenue"] += product.revenue or 0.0
            if product.is_high_performer:
                category_stats[category]["high_performers"] += 1
        
        # Generate performance trends
        for category, stats in category_stats.items():
            avg_sales = stats["total_sales"] / stats["count"]
            performance_rate = stats["high_performers"] / stats["count"] * 100
            
            if performance_rate > 40:
                trend = f"{category} category showing strong performance with {performance_rate:.1f}% high performers"
            elif performance_rate > 20:
                trend = f"{category} category showing moderate performance with {performance_rate:.1f}% high performers"
            else:
                trend = f"{category} category underperforming with only {performance_rate:.1f}% high performers"
            
            report.add_performance_trend(trend)
        
        # Generate recommendations
        total_products = len(product_data_list)
        high_performers = len([p for p in product_data_list if p.is_high_performer])
        restock_needed = len([p for p in product_data_list if p.requires_restocking])
        slow_moving = len([p for p in product_data_list if p.is_slow_moving])
        
        if high_performers / total_products < 0.2:
            report.add_recommendation("Consider reviewing pricing strategy and marketing efforts to improve overall product performance")
        
        if restock_needed > total_products * 0.15:
            report.add_recommendation("Implement automated inventory monitoring to prevent stockouts of popular items")
        
        if slow_moving > total_products * 0.25:
            report.add_recommendation("Review slow-moving inventory for potential promotions or discontinuation")
        
        # Best performing category recommendation
        if category_stats:
            best_category = max(category_stats.items(), key=lambda x: x[1]["high_performers"] / x[1]["count"])
            report.add_recommendation(f"Focus marketing efforts on {best_category[0]} category which shows highest performance rate")
        
        self.logger.info(f"Generated {len(report.performance_trends)} trends and {len(report.recommendations)} recommendations")
