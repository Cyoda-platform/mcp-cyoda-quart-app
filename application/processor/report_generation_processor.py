"""
ReportGenerationProcessor for Pet Store Performance Analysis System

Handles report generation including executive summary creation, trend analysis,
and comprehensive report data compilation as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that generates comprehensive performance reports
    with executive summaries, trend analysis, and actionable insights.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates comprehensive performance reports with analysis and insights",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate comprehensive performance report with analysis and insights.

        Args:
            entity: The Report entity to generate
            **kwargs: Additional processing parameters

        Returns:
            The generated report with complete analysis
        """
        try:
            self.logger.info(
                f"Generating performance report: {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Generate executive summary
            report.executive_summary = self._generate_executive_summary(report)

            # Generate sales trends analysis
            report.sales_trends = self._generate_sales_trends(report)

            # Generate inventory insights
            report.inventory_insights = self._generate_inventory_insights(report)

            # Compile complete report data
            report_data = self._compile_report_data(report)
            report.set_report_data(report_data)

            self.logger.info(
                f"Report {report.technical_id} generated successfully - "
                f"Products analyzed: {report.total_products_analyzed}, "
                f"Total revenue: ${report.total_revenue:.2f}"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _generate_executive_summary(self, report: Report) -> str:
        """
        Generate executive summary based on report data.

        Args:
            report: The Report entity

        Returns:
            Executive summary text
        """
        total_products = report.total_products_analyzed or 0
        total_revenue = report.total_revenue or 0.0
        top_performers = len(report.top_performing_products or [])
        underperformers = len(report.underperforming_products or [])
        low_stock = len(report.low_stock_items or [])

        summary_parts = [
            f"Weekly Performance Analysis Summary for {report.report_period_start[:10]} to {report.report_period_end[:10]}",
            "",
            f"• Total Products Analyzed: {total_products}",
            f"• Total Revenue Generated: ${total_revenue:,.2f}",
            f"• High-Performing Products: {top_performers}",
            f"• Underperforming Products: {underperformers}",
            f"• Products Requiring Restocking: {low_stock}",
            "",
        ]

        # Add key insights
        if top_performers > 0:
            summary_parts.append(
                f"✓ {top_performers} products are exceeding performance targets"
            )

        if underperformers > 0:
            summary_parts.append(
                f"⚠ {underperformers} products require attention to improve sales"
            )

        if low_stock > 0:
            summary_parts.append(
                f"📦 {low_stock} products are running low on inventory"
            )

        # Add revenue insights
        if total_revenue > 10000:
            summary_parts.append("💰 Strong revenue performance this week")
        elif total_revenue > 5000:
            summary_parts.append(
                "📈 Moderate revenue performance with room for improvement"
            )
        else:
            summary_parts.append(
                "📉 Revenue below expectations - review product strategies"
            )

        summary_parts.extend(
            [
                "",
                "Recommendations:",
                "• Focus marketing efforts on high-performing products",
                "• Review pricing and promotion strategies for underperforming items",
                "• Prioritize restocking for low-inventory products",
                "• Monitor trends for early identification of market changes",
            ]
        )

        return "\n".join(summary_parts)

    def _generate_sales_trends(self, report: Report) -> Dict[str, Any]:
        """
        Generate sales trends analysis.

        Args:
            report: The Report entity

        Returns:
            Sales trends data
        """
        # Analyze product categories
        category_performance = {}
        category_revenue = {}

        all_products = []
        if report.top_performing_products:
            all_products.extend(report.top_performing_products)
        if report.underperforming_products:
            all_products.extend(report.underperforming_products)

        for product in all_products:
            category = product.get("category", "unknown")
            sales = product.get("sales_volume", 0)
            revenue = product.get("revenue", 0.0)

            if category not in category_performance:
                category_performance[category] = {"products": 0, "total_sales": 0}
                category_revenue[category] = 0.0

            category_performance[category]["products"] += 1
            category_performance[category]["total_sales"] += sales
            category_revenue[category] += revenue

        # Identify trending categories
        trending_up = []
        trending_down = []

        for category, data in category_performance.items():
            avg_sales = (
                data["total_sales"] / data["products"] if data["products"] > 0 else 0
            )
            if avg_sales >= 50:
                trending_up.append(category)
            elif avg_sales < 20:
                trending_down.append(category)

        return {
            "category_performance": category_performance,
            "category_revenue": category_revenue,
            "trending_up": trending_up,
            "trending_down": trending_down,
            "analysis_date": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    def _generate_inventory_insights(self, report: Report) -> Dict[str, Any]:
        """
        Generate inventory insights and recommendations.

        Args:
            report: The Report entity

        Returns:
            Inventory insights data
        """
        low_stock_count = len(report.low_stock_items or [])
        total_products = report.total_products_analyzed or 0

        # Calculate inventory health metrics
        inventory_health_score = 100.0
        if total_products > 0:
            low_stock_percentage = (low_stock_count / total_products) * 100
            inventory_health_score = max(0, 100 - (low_stock_percentage * 2))

        # Categorize low stock items by urgency
        critical_items = []
        warning_items = []

        for item in report.low_stock_items or []:
            inventory_level = item.get("inventory_level", 0)
            if inventory_level <= 5:
                critical_items.append(item)
            else:
                warning_items.append(item)

        # Generate restocking recommendations
        restocking_priority = []
        for item in critical_items:
            restocking_priority.append(
                {
                    "product_id": item.get("product_id"),
                    "name": item.get("name"),
                    "current_stock": item.get("inventory_level", 0),
                    "priority": "CRITICAL",
                    "recommended_order": max(50, item.get("sales_volume", 0) * 2),
                }
            )

        for item in warning_items:
            restocking_priority.append(
                {
                    "product_id": item.get("product_id"),
                    "name": item.get("name"),
                    "current_stock": item.get("inventory_level", 0),
                    "priority": "HIGH",
                    "recommended_order": max(30, item.get("sales_volume", 0) * 1.5),
                }
            )

        return {
            "inventory_health_score": inventory_health_score,
            "low_stock_count": low_stock_count,
            "critical_items_count": len(critical_items),
            "warning_items_count": len(warning_items),
            "restocking_priority": restocking_priority,
            "recommendations": [
                "Implement automated reorder points for critical items",
                "Review supplier lead times for better inventory planning",
                "Consider safety stock levels for high-demand products",
                "Monitor seasonal trends for proactive inventory management",
            ],
            "analysis_date": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    def _compile_report_data(self, report: Report) -> Dict[str, Any]:
        """
        Compile complete report data for email and storage.

        Args:
            report: The Report entity

        Returns:
            Complete report data
        """
        return {
            "report_metadata": {
                "title": report.report_title,
                "period_start": report.report_period_start,
                "period_end": report.report_period_end,
                "generated_at": report.generated_at,
                "generated_by": report.generated_by,
            },
            "summary_metrics": {
                "total_products": report.total_products_analyzed,
                "total_revenue": report.total_revenue,
                "top_performers_count": len(report.top_performing_products or []),
                "underperformers_count": len(report.underperforming_products or []),
                "low_stock_count": len(report.low_stock_items or []),
            },
            "executive_summary": report.executive_summary,
            "detailed_analysis": {
                "top_performing_products": report.top_performing_products,
                "underperforming_products": report.underperforming_products,
                "low_stock_items": report.low_stock_items,
                "sales_trends": report.sales_trends,
                "inventory_insights": report.inventory_insights,
            },
            "email_info": {
                "recipient": report.recipient_email,
                "status": report.email_status,
            },
        }
