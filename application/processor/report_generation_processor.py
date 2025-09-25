"""
ReportGenerationProcessor for Pet Store Performance Analysis System

Handles generation of performance analysis reports from analyzed product data
as specified in functional requirements.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from application.entity.product import Product
from application.entity.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that generates performance analysis reports
    from analyzed product data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates performance analysis reports from product data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate performance analysis report.

        Args:
            entity: The Report entity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The report entity with generated content
        """
        try:
            self.logger.info(
                f"Generating report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Get analyzed product data
            products = await self._get_analyzed_products()

            # Generate report content
            content = await self._generate_report_content(report, products)

            # Generate insights and summary metrics
            insights = self._generate_insights(products)
            summary_metrics = self._calculate_summary_metrics(products)

            # Set generated report data
            report.set_generated(content, insights, summary_metrics)

            # Add product highlights
            highlights = self._get_product_highlights(products)
            for highlight in highlights:
                report.add_product_highlight(highlight)

            self.logger.info(
                f"Report {report.technical_id} generation completed successfully"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_analyzed_products(self) -> List[Product]:
        """
        Retrieve all analyzed products from the entity service.

        Returns:
            List of analyzed Product entities
        """
        entity_service = get_entity_service()

        try:
            # Get all products that have been analyzed
            product_responses = await entity_service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

            products = []
            for response in product_responses:
                product = cast_entity(response.data, Product)
                # Only include products that have been analyzed
                if (
                    product.state in ["analyzed", "completed"]
                    and product.performance_score is not None
                ):
                    products.append(product)

            self.logger.info(
                f"Retrieved {len(products)} analyzed products for report generation"
            )
            return products

        except Exception as e:
            self.logger.error(f"Error retrieving analyzed products: {str(e)}")
            return []

    async def _generate_report_content(
        self, report: Report, products: List[Product]
    ) -> str:
        """
        Generate the main report content in markdown format.

        Args:
            report: The Report entity
            products: List of analyzed products

        Returns:
            Generated report content as markdown string
        """
        # Set data period if not already set
        if not report.data_period_start:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)  # Weekly report
            report.set_data_period(
                start_date.isoformat().replace("+00:00", "Z"),
                end_date.isoformat().replace("+00:00", "Z"),
            )

        content_lines = [
            f"# {report.title}",
            "",
            f"**Report Type:** {report.report_type}",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Data Period:** {report.data_period_start} to {report.data_period_end}",
            f"**Total Products Analyzed:** {len(products)}",
            "",
            "## Executive Summary",
            "",
            self._generate_executive_summary(products),
            "",
            "## Performance Overview",
            "",
            self._generate_performance_overview(products),
            "",
            "## Top Performing Products",
            "",
            self._generate_top_performers_section(products),
            "",
            "## Underperforming Products",
            "",
            self._generate_underperformers_section(products),
            "",
            "## Inventory Status",
            "",
            self._generate_inventory_section(products),
            "",
            "## Category Analysis",
            "",
            self._generate_category_analysis(products),
            "",
            "## Recommendations",
            "",
            self._generate_recommendations(products),
            "",
            "---",
            "",
            "*This report was automatically generated by the Pet Store Performance Analysis System.*",
        ]

        return "\n".join(content_lines)

    def _generate_executive_summary(self, products: List[Product]) -> str:
        """Generate executive summary section."""
        if not products:
            return "No product data available for analysis."

        total_revenue = sum(p.revenue or 0 for p in products)
        total_sales = sum(p.sales_volume or 0 for p in products)
        avg_performance = sum(p.performance_score or 0 for p in products) / len(
            products
        )

        high_performers = [p for p in products if p.is_high_performer()]
        low_performers = [p for p in products if p.is_low_performer()]
        out_of_stock = [p for p in products if p.stock_status == "OUT_OF_STOCK"]

        summary = [
            f"This week's analysis covers {len(products)} products across all categories.",
            f"Total revenue generated: ${total_revenue:,.2f}",
            f"Total units sold: {total_sales:,}",
            f"Average performance score: {avg_performance:.1f}/100",
            "",
            "**Key Highlights:**",
            f"- {len(high_performers)} products are high performers (score ≥ 70)",
            f"- {len(low_performers)} products need attention (score ≤ 30)",
            f"- {len(out_of_stock)} products are currently out of stock",
        ]

        return "\n".join(summary)

    def _generate_performance_overview(self, products: List[Product]) -> str:
        """Generate performance overview section."""
        if not products:
            return "No performance data available."

        performance_ranges = {
            "Excellent (80-100)": len(
                [p for p in products if (p.performance_score or 0) >= 80]
            ),
            "Good (60-79)": len(
                [p for p in products if 60 <= (p.performance_score or 0) < 80]
            ),
            "Average (40-59)": len(
                [p for p in products if 40 <= (p.performance_score or 0) < 60]
            ),
            "Below Average (20-39)": len(
                [p for p in products if 20 <= (p.performance_score or 0) < 40]
            ),
            "Poor (0-19)": len(
                [p for p in products if (p.performance_score or 0) < 20]
            ),
        }

        overview = ["**Performance Distribution:**", ""]
        for range_name, count in performance_ranges.items():
            percentage = (count / len(products)) * 100
            overview.append(f"- {range_name}: {count} products ({percentage:.1f}%)")

        return "\n".join(overview)

    def _generate_top_performers_section(self, products: List[Product]) -> str:
        """Generate top performers section."""
        top_performers = sorted(
            [p for p in products if p.performance_score is not None],
            key=lambda x: x.performance_score or 0,
            reverse=True,
        )[:5]

        if not top_performers:
            return "No top performers identified."

        section = [
            "| Product | Category | Performance Score | Revenue | Sales Volume |",
            "|---------|----------|------------------|---------|--------------|",
        ]

        for product in top_performers:
            section.append(
                f"| {product.name} | {product.category} | {product.performance_score:.1f} | "
                f"${product.revenue or 0:.2f} | {product.sales_volume or 0} |"
            )

        return "\n".join(section)

    def _generate_underperformers_section(self, products: List[Product]) -> str:
        """Generate underperformers section."""
        underperformers = sorted(
            [p for p in products if p.is_low_performer()],
            key=lambda x: x.performance_score or 0,
        )[:5]

        if not underperformers:
            return "No significant underperformers identified."

        section = [
            "| Product | Category | Performance Score | Revenue | Issues |",
            "|---------|----------|------------------|---------|--------|",
        ]

        for product in underperformers:
            issues = []
            if (product.sales_volume or 0) <= 10:
                issues.append("Low sales")
            if product.stock_status == "OUT_OF_STOCK":
                issues.append("Out of stock")
            if (product.revenue or 0) <= 200:
                issues.append("Low revenue")

            section.append(
                f"| {product.name} | {product.category} | {product.performance_score:.1f} | "
                f"${product.revenue or 0:.2f} | {', '.join(issues) or 'N/A'} |"
            )

        return "\n".join(section)

    def _generate_inventory_section(self, products: List[Product]) -> str:
        """Generate inventory status section."""
        inventory_status: Dict[str, int] = {}
        for product in products:
            status = product.stock_status or "UNKNOWN"
            inventory_status[status] = inventory_status.get(status, 0) + 1

        section = ["**Inventory Status Summary:**", ""]
        for status, count in inventory_status.items():
            section.append(f"- {status.replace('_', ' ').title()}: {count} products")

        # List products needing immediate attention
        urgent_restock = [p for p in products if p.stock_status == "OUT_OF_STOCK"]
        if urgent_restock:
            section.extend(["", "**Products Requiring Immediate Restocking:**"])
            for product in urgent_restock[:10]:  # Limit to top 10
                section.append(f"- {product.name} ({product.category})")

        return "\n".join(section)

    def _generate_category_analysis(self, products: List[Product]) -> str:
        """Generate category analysis section."""
        category_stats = {}

        for product in products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "total_revenue": 0.0,
                    "total_sales": 0.0,
                    "avg_performance": 0.0,
                }

            stats = category_stats[category]
            stats["count"] += 1
            stats["total_revenue"] += float(product.revenue or 0)
            stats["total_sales"] += float(product.sales_volume or 0)
            stats["avg_performance"] += float(product.performance_score or 0)

        # Calculate averages
        for stats in category_stats.values():
            if stats["count"] > 0:
                stats["avg_performance"] = float(stats["avg_performance"]) / stats["count"]

        section = [
            "| Category | Products | Total Revenue | Total Sales | Avg Performance |",
            "|----------|----------|---------------|-------------|-----------------|",
        ]

        for category, stats in sorted(category_stats.items()):
            section.append(
                f"| {category} | {stats['count']} | ${stats['total_revenue']:.2f} | "
                f"{stats['total_sales']} | {stats['avg_performance']:.1f} |"
            )

        return "\n".join(section)

    def _generate_recommendations(self, products: List[Product]) -> str:
        """Generate recommendations section."""
        recommendations = []

        # Inventory recommendations
        out_of_stock_count = len(
            [p for p in products if p.stock_status == "OUT_OF_STOCK"]
        )
        if out_of_stock_count > 0:
            recommendations.append(
                f"🚨 **Immediate Action Required:** {out_of_stock_count} products are out of stock and need immediate restocking."
            )

        low_stock_count = len([p for p in products if p.stock_status == "LOW_STOCK"])
        if low_stock_count > 0:
            recommendations.append(
                f"⚠️ **Plan Restocking:** {low_stock_count} products have low inventory levels."
            )

        # Performance recommendations
        high_performers = [p for p in products if p.is_high_performer()]
        if high_performers:
            recommendations.append(
                f"✅ **Expand Successful Products:** Consider increasing inventory for {len(high_performers)} high-performing products."
            )

        low_performers = [p for p in products if p.is_low_performer()]
        if low_performers:
            recommendations.append(
                f"📊 **Review Strategy:** {len(low_performers)} products need marketing or pricing strategy review."
            )

        # Category recommendations
        category_performance: Dict[str, List[float]] = {}
        for product in products:
            category = product.category
            if category not in category_performance:
                category_performance[category] = []
            category_performance[category].append(float(product.performance_score or 0))

        for category, scores in category_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 70:
                recommendations.append(
                    f"🎯 **{category} Category:** Strong performance - consider expanding product line."
                )
            elif avg_score <= 30:
                recommendations.append(
                    f"🔍 **{category} Category:** Underperforming - review product mix and pricing."
                )

        return (
            "\n".join(recommendations)
            if recommendations
            else "No specific recommendations at this time."
        )

    def _generate_insights(self, products: List[Product]) -> Dict[str, Any]:
        """Generate insights dictionary for the report."""
        if not products:
            return {"message": "No products available for analysis"}

        total_revenue = sum(p.revenue or 0 for p in products)
        total_sales = sum(p.sales_volume or 0 for p in products)
        avg_performance = sum(p.performance_score or 0 for p in products) / len(
            products
        )

        return {
            "total_products_analyzed": len(products),
            "total_revenue": total_revenue,
            "total_sales_volume": total_sales,
            "average_performance_score": round(avg_performance, 2),
            "high_performers_count": len(
                [p for p in products if p.is_high_performer()]
            ),
            "low_performers_count": len([p for p in products if p.is_low_performer()]),
            "out_of_stock_count": len(
                [p for p in products if p.stock_status == "OUT_OF_STOCK"]
            ),
            "categories_analyzed": len(set(p.category for p in products)),
            "top_category": self._get_top_category(products),
            "analysis_timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    def _calculate_summary_metrics(self, products: List[Product]) -> Dict[str, Any]:
        """Calculate summary metrics for the report."""
        if not products:
            return {}

        revenues = [p.revenue or 0 for p in products]
        sales = [p.sales_volume or 0 for p in products]
        scores = [p.performance_score or 0 for p in products]

        return {
            "revenue": {
                "total": sum(revenues),
                "average": sum(revenues) / len(revenues),
                "max": max(revenues),
                "min": min(revenues),
            },
            "sales": {
                "total": sum(sales),
                "average": sum(sales) / len(sales),
                "max": max(sales),
                "min": min(sales),
            },
            "performance": {
                "average": sum(scores) / len(scores),
                "max": max(scores),
                "min": min(scores),
            },
        }

    def _get_product_highlights(self, products: List[Product]) -> List[Dict[str, Any]]:
        """Get product highlights for the report."""
        highlights = []

        # Top performer
        if products:
            top_performer = max(products, key=lambda x: x.performance_score or 0)
            highlights.append(
                {
                    "type": "top_performer",
                    "product_name": top_performer.name,
                    "category": top_performer.category,
                    "performance_score": top_performer.performance_score,
                    "revenue": top_performer.revenue,
                    "sales_volume": top_performer.sales_volume,
                }
            )

        # Biggest revenue generator
        if products:
            revenue_leader = max(products, key=lambda x: x.revenue or 0)
            if revenue_leader != top_performer:
                highlights.append(
                    {
                        "type": "revenue_leader",
                        "product_name": revenue_leader.name,
                        "category": revenue_leader.category,
                        "performance_score": revenue_leader.performance_score,
                        "revenue": revenue_leader.revenue,
                        "sales_volume": revenue_leader.sales_volume,
                    }
                )

        return highlights

    def _get_top_category(self, products: List[Product]) -> str:
        """Get the top performing category."""
        category_scores = {}
        category_counts = {}

        for product in products:
            category = product.category
            if category not in category_scores:
                category_scores[category] = 0.0
                category_counts[category] = 0

            category_scores[category] += float(product.performance_score or 0)
            category_counts[category] += 1

        # Calculate average scores
        category_averages = {
            category: category_scores[category] / category_counts[category]
            for category in category_scores
        }

        return (
            max(category_averages.keys(), key=lambda k: category_averages[k])
            if category_averages
            else "N/A"
        )
