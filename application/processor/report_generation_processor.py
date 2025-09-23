"""
ReportGenerationProcessor for Pet Store Performance Analysis System

Handles generation of weekly performance reports by analyzing Product entities
and compiling insights, trends, and recommendations as specified in 
functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.report.version_1.report import Report
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entities that generates weekly performance reports
    by analyzing Product data and compiling insights for the sales team.
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
        Process the Report entity to generate performance analysis content.

        Args:
            entity: The Report entity to generate (must be in 'created' state)
            **kwargs: Additional processing parameters

        Returns:
            The generated report with analysis content
        """
        try:
            self.logger.info(
                f"Generating Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Fetch and analyze product data
            products = await self._fetch_product_data()
            
            # Generate report content
            await self._analyze_products_for_report(report, products)
            self._generate_report_content(report)
            
            # Update generation timestamp
            report.update_generation_timestamp()

            self.logger.info(
                f"Report {report.technical_id} generated successfully - "
                f"Analyzed {report.total_products_analyzed} products"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating Report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_product_data(self) -> List[Product]:
        """
        Fetch all Product entities for analysis.

        Returns:
            List of Product entities
        """
        entity_service = get_entity_service()
        
        try:
            # Fetch all products that have been analyzed (in completed state)
            product_responses = await entity_service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )
            
            products = []
            for response in product_responses:
                if hasattr(response, 'data'):
                    # Convert response data to Product entity
                    product_data = response.data
                    if hasattr(product_data, 'model_dump'):
                        product_dict = product_data.model_dump(by_alias=True)
                    else:
                        product_dict = product_data
                    
                    # Create Product instance from dict
                    product = Product(**product_dict)
                    products.append(product)
            
            self.logger.info(f"Fetched {len(products)} products for report analysis")
            return products
            
        except Exception as e:
            self.logger.error(f"Error fetching product data: {str(e)}")
            return []

    async def _analyze_products_for_report(self, report: Report, products: List[Product]) -> None:
        """
        Analyze products and populate report with insights.

        Args:
            report: The Report entity to populate
            products: List of Product entities to analyze
        """
        high_performers = []
        underperformers = []
        restock_needed = []
        
        total_revenue = 0.0
        total_sales_volume = 0
        performance_scores = []
        
        trending_categories = set()
        declining_categories = set()

        for product in products:
            # Collect summary metrics
            if product.revenue:
                total_revenue += product.revenue
            if product.sales_volume:
                total_sales_volume += product.sales_volume
            if product.performance_score is not None:
                performance_scores.append(product.performance_score)

            # Categorize products
            product_summary = {
                "name": product.name,
                "category": product.category_name or "Unknown",
                "status": product.status,
                "performance_score": product.performance_score,
                "sales_volume": product.sales_volume,
                "revenue": product.revenue,
                "trend": product.trend_indicator
            }

            # High performers
            if product.is_high_performer():
                high_performers.append(product_summary)
                if product.category_name:
                    trending_categories.add(product.category_name)

            # Underperformers
            if product.is_underperformer():
                underperformers.append(product_summary)
                if product.category_name:
                    declining_categories.add(product.category_name)

            # Restock recommendations
            if product.restock_needed:
                restock_item = {
                    "name": product.name,
                    "category": product.category_name or "Unknown",
                    "current_inventory": product.inventory_count,
                    "status": product.status,
                    "priority": "HIGH" if product.inventory_count == 0 else "MEDIUM"
                }
                restock_needed.append(restock_item)

        # Update report with analysis results
        report.high_performers = high_performers
        report.underperformers = underperformers
        report.restock_recommendations = restock_needed
        
        report.total_revenue = total_revenue
        report.total_sales_volume = total_sales_volume
        report.total_products_analyzed = len(products)
        
        if performance_scores:
            report.average_performance_score = sum(performance_scores) / len(performance_scores)
        
        report.trending_categories = list(trending_categories)
        report.declining_categories = list(declining_categories)

        self.logger.info(
            f"Report analysis complete - High performers: {len(high_performers)}, "
            f"Underperformers: {len(underperformers)}, Restock needed: {len(restock_needed)}"
        )

    def _generate_report_content(self, report: Report) -> None:
        """
        Generate the actual report content in the specified format.

        Args:
            report: The Report entity to generate content for
        """
        # Generate executive summary
        report.generate_executive_summary()
        
        # Generate detailed report content based on format
        if report.report_format == "HTML":
            report.report_content = self._generate_html_content(report)
        elif report.report_format == "JSON":
            report.report_content = self._generate_json_content(report)
        else:  # Default to HTML for PDF generation
            report.report_content = self._generate_html_content(report)

    def _generate_html_content(self, report: Report) -> str:
        """
        Generate HTML content for the report.

        Args:
            report: The Report entity

        Returns:
            HTML content string
        """
        html_parts = [
            f"<html><head><title>{report.report_title}</title></head><body>",
            f"<h1>{report.report_title}</h1>",
            f"<p><strong>Report Period:</strong> {report.report_period_start} to {report.report_period_end}</p>",
            f"<p><strong>Generated:</strong> {report.generated_at}</p>",
            "<hr>",
            f"<h2>Executive Summary</h2>",
            f"<pre>{report.executive_summary}</pre>",
            "<hr>"
        ]

        # High performers section
        if report.high_performers:
            html_parts.append("<h2>High Performing Products</h2>")
            html_parts.append("<ul>")
            for product in report.high_performers[:10]:  # Top 10
                html_parts.append(
                    f"<li><strong>{product['name']}</strong> - "
                    f"Score: {product['performance_score']:.1f}, "
                    f"Revenue: ${product['revenue']:.2f}</li>"
                )
            html_parts.append("</ul>")

        # Underperformers section
        if report.underperformers:
            html_parts.append("<h2>Products Needing Attention</h2>")
            html_parts.append("<ul>")
            for product in report.underperformers[:10]:  # Top 10
                html_parts.append(
                    f"<li><strong>{product['name']}</strong> - "
                    f"Score: {product['performance_score']:.1f}, "
                    f"Trend: {product['trend']}</li>"
                )
            html_parts.append("</ul>")

        # Restock recommendations
        if report.restock_recommendations:
            html_parts.append("<h2>Restocking Recommendations</h2>")
            html_parts.append("<ul>")
            for item in report.restock_recommendations:
                html_parts.append(
                    f"<li><strong>{item['name']}</strong> - "
                    f"Current Stock: {item['current_inventory']}, "
                    f"Priority: {item['priority']}</li>"
                )
            html_parts.append("</ul>")

        html_parts.append("</body></html>")
        return "\n".join(html_parts)

    def _generate_json_content(self, report: Report) -> str:
        """
        Generate JSON content for the report.

        Args:
            report: The Report entity

        Returns:
            JSON content string
        """
        import json
        
        content = {
            "title": report.report_title,
            "period": {
                "start": report.report_period_start,
                "end": report.report_period_end
            },
            "summary": {
                "total_products": report.total_products_analyzed,
                "total_revenue": report.total_revenue,
                "total_sales_volume": report.total_sales_volume,
                "average_performance_score": report.average_performance_score
            },
            "high_performers": report.high_performers,
            "underperformers": report.underperformers,
            "restock_recommendations": report.restock_recommendations,
            "trending_categories": report.trending_categories,
            "declining_categories": report.declining_categories,
            "executive_summary": report.executive_summary
        }
        
        return json.dumps(content, indent=2)
