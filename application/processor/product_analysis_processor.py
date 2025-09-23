"""
ProductAnalysisProcessor for Pet Store Performance Analysis System

Handles performance analysis for Product entities, calculating metrics,
trends, and generating insights for sales reporting as specified in
functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entities that performs performance analysis,
    calculates metrics, and determines trends for sales reporting.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes Product performance metrics and calculates trends for sales reporting",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Product entity to perform performance analysis.

        Args:
            entity: The Product entity to analyze (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The analyzed product with performance metrics
        """
        try:
            self.logger.info(
                f"Analyzing Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Perform performance analysis
            self._calculate_performance_metrics(product)
            self._determine_inventory_status(product)
            self._analyze_sales_trends(product)

            # Update analysis timestamp
            product.update_analysis_timestamp()

            self.logger.info(
                f"Product {product.technical_id} analyzed successfully - "
                f"Score: {product.performance_score}, Trend: {product.trend_indicator}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing Product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_metrics(self, product: Product) -> None:
        """
        Calculate performance metrics for the product.

        Args:
            product: The Product entity to analyze
        """
        # Calculate performance score using the entity's method
        performance_score = product.calculate_performance_score()

        self.logger.info(
            f"Product {product.name} performance score calculated: {performance_score}"
        )

        # Additional metrics based on business rules
        if product.sales_volume and product.sales_volume > 0:
            # Calculate revenue per unit if we have both metrics
            if product.revenue and product.revenue > 0:
                revenue_per_unit = product.revenue / product.sales_volume
                self.logger.info(
                    f"Product {product.name} revenue per unit: ${revenue_per_unit:.2f}"
                )

    def _determine_inventory_status(self, product: Product) -> None:
        """
        Determine inventory status and restocking needs.

        Args:
            product: The Product entity to analyze
        """
        # Check if restocking is needed based on inventory levels
        if product.inventory_count is not None:
            if product.inventory_count <= 5:  # Low inventory threshold
                product.restock_needed = True
                self.logger.warning(
                    f"Product {product.name} has low inventory: {product.inventory_count} units"
                )
            elif product.inventory_count == 0:
                product.restock_needed = True
                self.logger.warning(f"Product {product.name} is out of stock")
            else:
                product.restock_needed = False

    def _analyze_sales_trends(self, product: Product) -> None:
        """
        Analyze sales trends and set trend indicators.

        Args:
            product: The Product entity to analyze
        """
        # Determine trend using the entity's method
        trend = product.determine_trend()

        self.logger.info(f"Product {product.name} trend determined: {trend}")

        # Additional trend analysis based on business rules
        if (
            product.status == "sold"
            and product.sales_volume
            and product.sales_volume > 10
        ):
            # High-selling product
            if product.trend_indicator != "RISING":
                product.trend_indicator = "RISING"
                self.logger.info(
                    f"Product {product.name} upgraded to RISING trend due to high sales"
                )
        elif product.status == "available" and (
            not product.sales_volume or product.sales_volume == 0
        ):
            # No sales activity
            if product.trend_indicator != "DECLINING":
                product.trend_indicator = "DECLINING"
                self.logger.info(
                    f"Product {product.name} marked as DECLINING due to no sales activity"
                )

    def _generate_insights(self, product: Product) -> Dict[str, Any]:
        """
        Generate business insights for the product.

        Args:
            product: The Product entity to analyze

        Returns:
            Dictionary containing business insights
        """
        insights = {
            "is_high_performer": product.is_high_performer(),
            "is_underperformer": product.is_underperformer(),
            "needs_attention": product.needs_attention(),
            "analysis_timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

        # Add specific recommendations
        recommendations = []

        if product.restock_needed:
            recommendations.append("Restock inventory immediately")

        if product.is_high_performer():
            recommendations.append(
                "Consider increasing inventory for this high-performing product"
            )

        if product.is_underperformer():
            recommendations.append("Review pricing and marketing strategy")

        if (
            product.status == "pending"
            and product.inventory_count
            and product.inventory_count > 0
        ):
            recommendations.append("Follow up on pending sales")

        insights["recommendations"] = recommendations

        return insights
