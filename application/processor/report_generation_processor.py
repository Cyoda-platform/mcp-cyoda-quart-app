"""
ReportGenerationProcessor for Product Performance Analysis and Reporting System

Generates comprehensive performance analysis reports by analyzing Product entities,
calculating insights, and creating formatted reports for the sales team.
"""

import logging
from typing import Any, Dict, List

from application.entity.product.version_1.product import Product
from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that generates performance analysis reports.

    Analyzes all Product entities and creates comprehensive reports including:
    - Top performing products and underperforming products
    - Inventory status and low stock alerts
    - Sales trends and revenue analysis
    - Category performance breakdown
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates performance analysis reports from Product data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate performance analysis report.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters

        Returns:
            The updated Report entity with generated content
        """
        try:
            self.logger.info(
                f"Generating report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Fetch all analyzed products
            products = await self._fetch_analyzed_products()

            # Generate report content
            await self._generate_report_content(report, products)

            # Calculate summary metrics
            self._calculate_summary_metrics(report, products)

            # Generate file (mock implementation)
            self._generate_report_file(report)

            self.logger.info(
                f"Report {report.technical_id} generated successfully - "
                f"Analyzed {len(products)} products"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_analyzed_products(self) -> List[Product]:
        """
        Fetch all products that have been analyzed.

        Returns:
            List of analyzed Product entities
        """
        entity_service = get_entity_service()

        try:
            # Search for products in 'analyzed' state
            builder = SearchConditionRequest.builder()
            builder.equals("state", "analyzed")
            condition = builder.build()

            results = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )

            # Convert results to Product entities
            products = []
            for result in results:
                try:
                    if hasattr(result.data, "model_dump"):
                        product_data = result.data.model_dump()
                    else:
                        product_data = dict(result.data)
                    product = Product(**product_data)
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to convert product data: {str(e)}")
                    continue

            self.logger.info(f"Fetched {len(products)} analyzed products for reporting")
            return products

        except Exception as e:
            self.logger.error(f"Error fetching analyzed products: {str(e)}")
            return []

    async def _generate_report_content(
        self, report: Report, products: List[Product]
    ) -> None:
        """
        Generate the main report content and insights.

        Args:
            report: The Report entity to populate
            products: List of analyzed Product entities
        """
        # Identify top performing products
        top_products = self._identify_top_performers(products)

        # Identify underperforming products
        underperforming = self._identify_underperformers(products)

        # Identify low stock products
        low_stock = self._identify_low_stock_products(products)

        # Add performance insights to report
        report.add_performance_insights(top_products, underperforming, low_stock)

        # Generate category performance analysis
        report.category_performance = self._analyze_category_performance(products)

        # Generate executive summary
        report.summary = self._generate_executive_summary(
            products, top_products, underperforming, low_stock
        )

        # Set total products analyzed
        report.total_products_analyzed = len(products)

    def _identify_top_performers(self, products: List[Product]) -> List[Dict[str, Any]]:
        """Identify top performing products based on performance score"""
        top_performers = []

        # Filter and sort by performance score
        scored_products = [p for p in products if p.performance_score is not None]
        scored_products.sort(key=lambda x: x.performance_score or 0, reverse=True)

        # Take top 5 performers
        for product in scored_products[:5]:
            top_performers.append(
                {
                    "name": product.name,
                    "category": product.category,
                    "performance_score": product.performance_score,
                    "revenue": product.revenue,
                    "sales_volume": product.sales_volume,
                    "status": product.status,
                }
            )

        return top_performers

    def _identify_underperformers(
        self, products: List[Product]
    ) -> List[Dict[str, Any]]:
        """Identify underperforming products that need attention"""
        underperformers = []

        for product in products:
            if product.performance_score is not None and product.performance_score < 30:
                underperformers.append(
                    {
                        "name": product.name,
                        "category": product.category,
                        "performance_score": product.performance_score,
                        "revenue": product.revenue,
                        "sales_volume": product.sales_volume,
                        "issues": self._identify_product_issues(product),
                    }
                )

        return underperformers

    def _identify_low_stock_products(
        self, products: List[Product]
    ) -> List[Dict[str, Any]]:
        """Identify products with low stock levels"""
        low_stock_products = []

        for product in products:
            if product.is_low_stock():
                low_stock_products.append(
                    {
                        "name": product.name,
                        "category": product.category,
                        "current_stock": product.stock_level,
                        "reorder_point": product.reorder_point,
                        "status": product.status,
                        "urgency": "high" if product.stock_level == 0 else "medium",
                    }
                )

        return low_stock_products

    def _analyze_category_performance(self, products: List[Product]) -> Dict[str, Any]:
        """Analyze performance by product category"""
        category_stats = {}

        for product in products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {
                    "total_products": 0,
                    "total_revenue": 0.0,
                    "total_sales": 0,
                    "avg_performance_score": 0.0,
                    "performance_scores": [],
                }

            stats = category_stats[category]
            total_products = stats["total_products"]
            if isinstance(total_products, int):
                stats["total_products"] = total_products + 1

            if product.revenue:
                total_revenue = stats["total_revenue"]
                if isinstance(total_revenue, (int, float)):
                    stats["total_revenue"] = total_revenue + product.revenue
            if product.sales_volume:
                total_sales = stats["total_sales"]
                if isinstance(total_sales, int):
                    stats["total_sales"] = total_sales + product.sales_volume
            if product.performance_score:
                performance_scores = stats["performance_scores"]
                if isinstance(performance_scores, list):
                    performance_scores.append(product.performance_score)

        # Calculate averages
        for category, stats in category_stats.items():
            performance_scores = stats["performance_scores"]
            if isinstance(performance_scores, list) and performance_scores:
                stats["avg_performance_score"] = sum(performance_scores) / len(
                    performance_scores
                )
            del stats["performance_scores"]  # Remove raw scores from final output

        return category_stats

    def _generate_executive_summary(
        self,
        products: List[Product],
        top_products: List[Dict[str, Any]],
        underperforming: List[Dict[str, Any]],
        low_stock: List[Dict[str, Any]],
    ) -> str:
        """Generate executive summary for the report"""
        total_products = len(products)
        total_revenue = sum(p.revenue or 0 for p in products)
        avg_performance = sum(p.performance_score or 0 for p in products) / max(
            total_products, 1
        )

        summary = f"""
Weekly Product Performance Analysis Summary

Total Products Analyzed: {total_products}
Total Revenue: ${total_revenue:,.2f}
Average Performance Score: {avg_performance:.1f}/100

Key Highlights:
- {len(top_products)} high-performing products driving sales
- {len(underperforming)} products requiring attention
- {len(low_stock)} products need restocking

Top Performer: {top_products[0]['name'] if top_products else 'N/A'}
Immediate Action Required: {len([p for p in low_stock if p['urgency'] == 'high'])} out-of-stock items

Recommendations:
- Focus marketing efforts on top-performing categories
- Review pricing strategy for underperforming products
- Prioritize restocking for high-urgency items
        """.strip()

        return summary

    def _identify_product_issues(self, product: Product) -> List[str]:
        """Identify specific issues with underperforming products"""
        issues = []

        if product.sales_volume is not None and product.sales_volume < 10:
            issues.append("Low sales volume")
        if product.revenue is not None and product.revenue < 100:
            issues.append("Low revenue generation")
        if product.is_low_stock():
            issues.append("Low inventory levels")
        if product.status != "available":
            issues.append("Product not available for sale")

        return issues

    def _calculate_summary_metrics(
        self, report: Report, products: List[Product]
    ) -> None:
        """Calculate and set summary metrics for the report"""
        if not products:
            return

        # Calculate total revenue
        report.total_revenue = sum(p.revenue or 0 for p in products)

        # Calculate average performance score
        performance_scores = [
            p.performance_score for p in products if p.performance_score is not None
        ]
        if performance_scores:
            report.average_performance_score = sum(performance_scores) / len(
                performance_scores
            )

        # Mock revenue growth calculation (would use historical data in real system)
        report.revenue_growth_percentage = 12.5  # Mock 12.5% growth

    def _generate_report_file(self, report: Report) -> None:
        """Generate report file (mock implementation)"""
        # In a real system, this would generate PDF/HTML files
        file_path = f"/reports/weekly_report_{report.technical_id}.pdf"
        file_size = 1024 * 50  # Mock 50KB file

        report.set_file_info(file_path, file_size)
