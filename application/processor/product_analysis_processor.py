"""
ProductAnalysisProcessor for Pet Store Performance Analysis System

Handles performance analysis calculations for Product entities including
KPI calculations, trend analysis, and inventory recommendations.
"""

import logging
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.product.version_1.product import Product


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entity that performs performance analysis,
    calculates KPIs, and determines inventory recommendations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes product performance metrics and generates insights",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Product entity to calculate performance metrics.

        Args:
            entity: The Product entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with performance analysis results
        """
        try:
            self.logger.info(
                f"Analyzing Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Calculate performance score
            performance_score = self._calculate_performance_score(product)

            # Generate trend analysis
            trend_analysis = self._generate_trend_analysis(product)

            # Determine if restocking is needed
            needs_restock = self._check_restocking_needed(product)

            # Update product with analysis results
            product.set_performance_data(
                performance_score, trend_analysis, needs_restock
            )

            self.logger.info(
                f"Product {product.technical_id} analyzed - Score: {performance_score:.1f}, "
                f"Restock needed: {needs_restock}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_score(self, product: Product) -> float:
        """
        Calculate performance score based on sales volume, revenue, and inventory turnover.

        Args:
            product: The Product entity to analyze

        Returns:
            Performance score between 0-100
        """
        score = 0.0

        # Sales volume component (40% of score)
        sales_volume = product.sales_volume or 0
        if sales_volume > 100:
            score += 40
        elif sales_volume > 50:
            score += 30
        elif sales_volume > 20:
            score += 20
        elif sales_volume > 0:
            score += 10

        # Revenue component (40% of score)
        revenue = product.revenue or 0.0
        if revenue > 1000:
            score += 40
        elif revenue > 500:
            score += 30
        elif revenue > 200:
            score += 20
        elif revenue > 0:
            score += 10

        # Inventory management component (20% of score)
        inventory = product.inventory_level or 0
        if 10 <= inventory <= 100:  # Optimal range
            score += 20
        elif 5 <= inventory < 10 or inventory > 100:  # Suboptimal
            score += 10
        elif inventory > 0:  # Low stock
            score += 5
        # No points for zero inventory

        return min(score, 100.0)

    def _generate_trend_analysis(self, product: Product) -> Dict[str, Any]:
        """
        Generate trend analysis data for the product.

        Args:
            product: The Product entity to analyze

        Returns:
            Dictionary containing trend analysis data
        """
        sales_volume = product.sales_volume or 0
        revenue = product.revenue or 0.0
        inventory = product.inventory_level or 0

        # Determine trend categories
        sales_trend = (
            "high" if sales_volume > 50 else "medium" if sales_volume > 20 else "low"
        )
        revenue_trend = (
            "high" if revenue > 500 else "medium" if revenue > 200 else "low"
        )

        # Calculate inventory turnover estimate
        if inventory > 0 and sales_volume > 0:
            turnover_ratio = sales_volume / inventory
            turnover_category = (
                "high"
                if turnover_ratio > 2
                else "medium" if turnover_ratio > 1 else "low"
            )
        else:
            turnover_ratio = 0.0
            turnover_category = "unknown"

        return {
            "sales_trend": sales_trend,
            "revenue_trend": revenue_trend,
            "inventory_turnover": {
                "ratio": turnover_ratio,
                "category": turnover_category,
            },
            "category_performance": self._analyze_category_performance(
                product.category
            ),
            "recommendations": self._generate_recommendations(product),
        }

    def _check_restocking_needed(self, product: Product) -> bool:
        """
        Determine if product needs restocking based on inventory levels and sales.

        Args:
            product: The Product entity to check

        Returns:
            True if restocking is recommended
        """
        inventory = product.inventory_level or 0
        sales_volume = product.sales_volume or 0

        # Low inventory threshold
        if inventory < 10:
            return True

        # High sales with medium inventory
        if sales_volume > 50 and inventory < 30:
            return True

        # Zero inventory
        if inventory == 0:
            return True

        return False

    def _analyze_category_performance(self, category: str) -> Dict[str, Any]:
        """
        Analyze performance relative to product category.

        Args:
            category: Product category

        Returns:
            Category-specific performance insights
        """
        # Category-specific performance benchmarks
        category_benchmarks = {
            "dog": {"avg_sales": 45, "avg_revenue": 400},
            "cat": {"avg_sales": 35, "avg_revenue": 300},
            "bird": {"avg_sales": 20, "avg_revenue": 150},
            "fish": {"avg_sales": 25, "avg_revenue": 200},
            "reptile": {"avg_sales": 15, "avg_revenue": 250},
            "small-pet": {"avg_sales": 30, "avg_revenue": 180},
        }

        benchmark = category_benchmarks.get(
            category, {"avg_sales": 30, "avg_revenue": 250}
        )

        return {
            "category": category,
            "benchmark_sales": benchmark["avg_sales"],
            "benchmark_revenue": benchmark["avg_revenue"],
            "category_notes": f"Category: {category.title()} products typically perform at moderate levels",
        }

    def _generate_recommendations(self, product: Product) -> list[str]:
        """
        Generate actionable recommendations based on product analysis.

        Args:
            product: The Product entity to analyze

        Returns:
            List of recommendation strings
        """
        recommendations = []

        sales_volume = product.sales_volume or 0
        revenue = product.revenue or 0.0
        inventory = product.inventory_level or 0

        # Sales-based recommendations
        if sales_volume < 10:
            recommendations.append("Consider marketing campaign to boost sales")
        elif sales_volume > 100:
            recommendations.append("High performer - consider expanding inventory")

        # Revenue-based recommendations
        if revenue < 100:
            recommendations.append("Review pricing strategy to improve revenue")

        # Inventory-based recommendations
        if inventory < 5:
            recommendations.append("Urgent restocking required")
        elif inventory > 200:
            recommendations.append("Consider reducing inventory levels")

        # Category-specific recommendations
        if product.category in ["dog", "cat"] and sales_volume < 30:
            recommendations.append(
                "Popular category underperforming - investigate market factors"
            )

        if not recommendations:
            recommendations.append("Product performing within normal parameters")

        return recommendations
