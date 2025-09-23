"""
ReportGenerationProcessor for Product Performance Analysis and Reporting System

Generates comprehensive performance analysis reports with insights,
trends, and recommendations as specified in functional requirements.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from application.entity.product.version_1.product import Product
from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for generating performance analysis reports.

    Creates comprehensive reports with sales trends, inventory status,
    and actionable insights for the sales team.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates comprehensive performance analysis reports with insights and trends",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to generate performance analysis content.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed Report entity with generated content
        """
        try:
            self.logger.info(
                f"Generating report content for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report_entity = cast_entity(entity, Report)

            # Fetch product data for analysis
            products = await self._fetch_products_for_analysis()

            # Generate report content
            await self._generate_report_content(report_entity, products)

            # Generate insights and recommendations
            self._generate_insights(report_entity, products)

            # Set report metadata
            self._set_report_metadata(report_entity, products)

            # Mark report as generated
            report_entity.mark_generated()

            self.logger.info(
                f"Report generation completed for {report_entity.title}. "
                f"Analyzed {len(products)} products."
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_products_for_analysis(self) -> List[Product]:
        """
        Fetch all products for analysis.

        Returns:
            List of Product entities
        """
        try:
            entity_service = get_entity_service()

            # Fetch all products
            product_responses = await entity_service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

            # Convert to Product entities
            products = []
            for response in product_responses:
                try:
                    if hasattr(response.data, "model_dump"):
                        product_data = response.data.model_dump()
                    else:
                        product_data = response.data

                    if isinstance(product_data, dict):
                        product = Product(**product_data)
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to convert product data: {str(e)}")
                    continue

            self.logger.info(f"Fetched {len(products)} products for analysis")
            return products

        except Exception as e:
            self.logger.error(f"Failed to fetch products for analysis: {str(e)}")
            return []

    async def _generate_report_content(
        self, report: Report, products: List[Product]
    ) -> None:
        """
        Generate the main report content.

        Args:
            report: The Report entity to update
            products: List of Product entities to analyze
        """
        try:
            # Calculate summary statistics
            stats = self._calculate_summary_statistics(products)

            # Generate report content in markdown format
            content_parts = []

            # Header
            content_parts.append(f"# {report.title}")
            content_parts.append(
                f"**Report Period:** {report.report_period_start} to {report.report_period_end}"
            )
            content_parts.append(
                f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            content_parts.append("")

            # Executive Summary
            summary = self._generate_executive_summary(stats)
            content_parts.append("## Executive Summary")
            content_parts.append(summary)
            content_parts.append("")

            # Key Metrics
            content_parts.append("## Key Performance Metrics")
            content_parts.append(
                f"- **Total Products Analyzed:** {stats['total_products']}"
            )
            content_parts.append(f"- **Total Revenue:** ${stats['total_revenue']:,.2f}")
            content_parts.append(
                f"- **Average Performance Score:** {stats['avg_performance_score']:.1f}/100"
            )
            content_parts.append(
                f"- **High Performers:** {stats['high_performers_count']} products"
            )
            content_parts.append(
                f"- **Products Needing Restock:** {stats['restock_needed_count']} products"
            )
            content_parts.append("")

            # Top Performing Products
            if stats["top_performers"]:
                content_parts.append("## Top Performing Products")
                for i, product in enumerate(stats["top_performers"][:5], 1):
                    content_parts.append(
                        f"{i}. **{product.name}** (Score: {product.performance_score:.1f})"
                    )
                    content_parts.append(f"   - Category: {product.category}")
                    content_parts.append(f"   - Revenue: ${product.revenue or 0:.2f}")
                    content_parts.append(
                        f"   - Sales Volume: {product.sales_volume or 0}"
                    )
                content_parts.append("")

            # Underperforming Products
            if stats["underperformers"]:
                content_parts.append("## Products Requiring Attention")
                for i, product in enumerate(stats["underperformers"][:5], 1):
                    content_parts.append(
                        f"{i}. **{product.name}** (Score: {product.performance_score:.1f})"
                    )
                    content_parts.append(f"   - Category: {product.category}")
                    content_parts.append(f"   - Status: {product.status}")
                    if product.needs_restocking():
                        content_parts.append(
                            f"   - ⚠️ **Needs Restocking** (Inventory: {product.inventory_level})"
                        )
                content_parts.append("")

            # Category Performance
            category_stats = self._calculate_category_statistics(products)
            content_parts.append("## Performance by Category")
            for category, cat_stats in category_stats.items():
                content_parts.append(f"### {category}")
                content_parts.append(f"- Products: {cat_stats['count']}")
                content_parts.append(f"- Total Revenue: ${cat_stats['revenue']:,.2f}")
                content_parts.append(f"- Average Score: {cat_stats['avg_score']:.1f}")
                content_parts.append("")

            # Join all content
            report.content = "\n".join(content_parts)
            report.summary = summary

        except Exception as e:
            self.logger.error(f"Failed to generate report content: {str(e)}")
            report.content = f"Error generating report content: {str(e)}"
            report.summary = "Report generation failed due to technical issues."

    def _generate_executive_summary(self, stats: Dict[str, Any]) -> str:
        """
        Generate executive summary based on statistics.

        Args:
            stats: Summary statistics

        Returns:
            Executive summary text
        """
        summary_parts = []

        summary_parts.append(
            f"This weekly performance report analyzes {stats['total_products']} products "
            f"with a combined revenue of ${stats['total_revenue']:,.2f}."
        )

        if stats["high_performers_count"] > 0:
            summary_parts.append(
                f"We identified {stats['high_performers_count']} high-performing products "
                f"that are driving strong sales."
            )

        if stats["restock_needed_count"] > 0:
            summary_parts.append(
                f"**Action Required:** {stats['restock_needed_count']} products "
                f"require immediate restocking to avoid stockouts."
            )

        if stats["avg_performance_score"] >= 70:
            summary_parts.append(
                "Overall product performance is strong with good sales momentum."
            )
        elif stats["avg_performance_score"] >= 50:
            summary_parts.append(
                "Product performance is moderate with opportunities for improvement."
            )
        else:
            summary_parts.append(
                "Product performance needs attention with several underperforming items."
            )

        return " ".join(summary_parts)

    def _calculate_summary_statistics(self, products: List[Product]) -> Dict[str, Any]:
        """
        Calculate summary statistics from products.

        Args:
            products: List of Product entities

        Returns:
            Dictionary of summary statistics
        """
        if not products:
            return {
                "total_products": 0,
                "total_revenue": 0.0,
                "avg_performance_score": 0.0,
                "high_performers_count": 0,
                "restock_needed_count": 0,
                "top_performers": [],
                "underperformers": [],
            }

        total_revenue = sum(p.revenue or 0 for p in products)
        performance_scores = [
            p.performance_score for p in products if p.performance_score is not None
        ]
        avg_score = (
            sum(performance_scores) / len(performance_scores)
            if performance_scores
            else 0
        )

        high_performers = [p for p in products if p.is_high_performer()]
        underperformers = [
            p
            for p in products
            if p.performance_score is not None and p.performance_score < 40
        ]
        restock_needed = [p for p in products if p.needs_restocking()]

        # Sort by performance score
        top_performers = sorted(
            products, key=lambda p: p.performance_score or 0, reverse=True
        )

        return {
            "total_products": len(products),
            "total_revenue": total_revenue,
            "avg_performance_score": avg_score,
            "high_performers_count": len(high_performers),
            "restock_needed_count": len(restock_needed),
            "top_performers": top_performers,
            "underperformers": underperformers,
        }

    def _calculate_category_statistics(
        self, products: List[Product]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate statistics by product category.

        Args:
            products: List of Product entities

        Returns:
            Dictionary of category statistics
        """
        category_stats = {}

        for product in products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {"count": 0, "revenue": 0.0, "scores": []}

            category_stats[category]["count"] += 1
            category_stats[category]["revenue"] += product.revenue or 0
            if product.performance_score is not None:
                category_stats[category]["scores"].append(product.performance_score)

        # Calculate averages
        for category, stats in category_stats.items():
            if stats["scores"]:
                stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"])
            else:
                stats["avg_score"] = 0.0

        return category_stats

    def _generate_insights(self, report: Report, products: List[Product]) -> None:
        """
        Generate insights and recommendations.

        Args:
            report: The Report entity to update
            products: List of Product entities
        """
        insights = []

        # Analyze trends and generate insights
        high_performers = [p for p in products if p.is_high_performer()]
        low_stock_items = [p for p in products if p.is_low_stock()]

        if high_performers:
            insights.append(
                {
                    "type": "success",
                    "description": f"Strong performance from {len(high_performers)} products, particularly in {high_performers[0].category} category",
                    "priority": "high",
                }
            )

        if low_stock_items:
            insights.append(
                {
                    "type": "warning",
                    "description": f"{len(low_stock_items)} products have low inventory levels and may require restocking",
                    "priority": "high",
                }
            )

        # Category insights
        category_stats = self._calculate_category_statistics(products)
        best_category = (
            max(category_stats.items(), key=lambda x: x[1]["avg_score"])
            if category_stats
            else None
        )
        if best_category:
            insights.append(
                {
                    "type": "insight",
                    "description": f"{best_category[0]} category shows strongest performance with average score of {best_category[1]['avg_score']:.1f}",
                    "priority": "medium",
                }
            )

        report.insights = insights

    def _set_report_metadata(self, report: Report, products: List[Product]) -> None:
        """
        Set report metadata and summary fields.

        Args:
            report: The Report entity to update
            products: List of Product entities
        """
        # Set report period (last 7 days)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        report.set_report_period(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )

        # Set summary statistics
        stats = self._calculate_summary_statistics(products)
        report.total_products_analyzed = stats["total_products"]
        report.total_revenue = stats["total_revenue"]

        # Set product lists
        report.top_performing_products = [
            p.technical_id or p.entity_id or "" for p in stats["top_performers"][:10]
        ]
        report.underperforming_products = [
            p.technical_id or p.entity_id or "" for p in stats["underperformers"][:10]
        ]
        report.products_needing_restock = [
            p.technical_id or p.entity_id or "" for p in products if p.needs_restocking()
        ]

        # Generate email subject
        report.generate_email_subject()
