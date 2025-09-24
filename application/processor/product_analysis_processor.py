"""
ProductAnalysisProcessor for Product Performance Analysis and Reporting System

Analyzes product performance metrics including sales volume, revenue calculations,
inventory turnover rates, and performance scoring for business insights.
"""

import logging
from typing import Any

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entity that performs performance analysis.

    Calculates key performance indicators including:
    - Performance scoring based on sales and inventory metrics
    - Inventory turnover rate calculations
    - Revenue calculations from price and sales volume
    - Product categorization for reporting insights
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes product performance metrics and calculates KPIs for reporting",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze the Product entity and calculate performance metrics.

        Args:
            entity: The Product entity to analyze (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The analyzed product with calculated performance metrics
        """
        try:
            self.logger.info(
                f"Analyzing Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Calculate revenue if not already set
            if product.revenue is None:
                product.calculate_revenue()

            # Calculate performance score
            performance_score = self._calculate_performance_score(product)

            # Calculate inventory turnover rate
            turnover_rate = self._calculate_inventory_turnover_rate(product)

            # Set performance metrics
            product.set_performance_metrics(performance_score, turnover_rate)

            # Log analysis completion
            self.logger.info(
                f"Product {product.technical_id} analyzed successfully - "
                f"Performance Score: {performance_score:.2f}, "
                f"Turnover Rate: {turnover_rate:.2f}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_score(self, product: Product) -> float:
        """
        Calculate performance score based on sales and inventory metrics.

        Performance score is calculated using:
        - Sales volume (40% weight)
        - Revenue (30% weight)
        - Stock availability (20% weight)
        - Category performance (10% weight)

        Args:
            product: The Product entity to score

        Returns:
            Performance score between 0-100
        """
        score = 0.0

        # Sales volume component (0-40 points)
        if product.sales_volume is not None:
            # Normalize sales volume (assuming max of 1000 units for scoring)
            sales_score = min(product.sales_volume / 1000.0, 1.0) * 40
            score += sales_score

        # Revenue component (0-30 points)
        if product.revenue is not None:
            # Normalize revenue (assuming max of $10,000 for scoring)
            revenue_score = min(product.revenue / 10000.0, 1.0) * 30
            score += revenue_score

        # Stock availability component (0-20 points)
        if product.stock_level is not None:
            if product.stock_level > 0:
                # Available products get full points
                stock_score = 20
                # Bonus for healthy stock levels
                if (
                    product.reorder_point
                    and product.stock_level > product.reorder_point * 2
                ):
                    stock_score = 20
                elif product.is_low_stock():
                    stock_score = 10  # Reduced score for low stock
            else:
                stock_score = 0  # Out of stock
            score += stock_score

        # Category performance component (0-10 points)
        category_scores = {
            "Dogs": 10,  # High demand category
            "Cats": 8,  # High demand category
            "Fish": 6,  # Medium demand category
            "Birds": 5,  # Medium demand category
            "Reptiles": 4,  # Lower demand category
            "Small Pets": 3,  # Lower demand category
        }
        category_score = category_scores.get(product.category, 5)  # Default 5 points
        score += category_score

        return min(score, 100.0)  # Cap at 100

    def _calculate_inventory_turnover_rate(self, product: Product) -> float:
        """
        Calculate inventory turnover rate.

        Simplified calculation based on sales volume and current stock level.
        In a real system, this would use historical data over time periods.

        Args:
            product: The Product entity

        Returns:
            Inventory turnover rate (times per period)
        """
        if product.sales_volume is None or product.stock_level is None:
            return 0.0

        if product.stock_level == 0:
            # High turnover if sold out
            return 10.0 if product.sales_volume > 0 else 0.0

        # Simple turnover calculation: sales_volume / average_inventory
        # Assuming current stock is representative of average inventory
        turnover_rate = product.sales_volume / product.stock_level

        return round(turnover_rate, 2)

    def _determine_product_insights(self, product: Product) -> Dict[str, Any]:
        """
        Generate insights about the product for reporting.

        Args:
            product: The analyzed Product entity

        Returns:
            Dictionary containing product insights
        """
        insights = {
            "is_high_performer": product.is_high_performer(),
            "is_low_stock": product.is_low_stock(),
            "needs_attention": False,
            "recommendations": [],
        }

        # Determine if product needs attention
        if product.performance_score and product.performance_score < 30:
            insights["needs_attention"] = True
            insights["recommendations"].append("Review pricing and marketing strategy")

        if product.is_low_stock():
            insights["needs_attention"] = True
            insights["recommendations"].append("Restock inventory immediately")

        if product.inventory_turnover_rate and product.inventory_turnover_rate < 1.0:
            insights["recommendations"].append(
                "Consider promotional activities to increase sales"
            )

        if product.status == "pending":
            insights["recommendations"].append("Update product status to available")

        return insights
