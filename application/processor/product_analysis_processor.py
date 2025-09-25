"""
ProductAnalysisProcessor for Pet Store Performance Analysis System

Handles performance analysis calculations for Product entities including
trend analysis, performance scoring, and insights generation.
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entity that performs performance analysis
    and calculates performance metrics and trends.
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
        Analyze performance metrics for the Product entity.

        Args:
            entity: The Product entity to process (must be in 'data_extracted' state)
            **kwargs: Additional processing parameters

        Returns:
            The product entity with analysis results
        """
        try:
            self.logger.info(
                f"Analyzing performance for Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Calculate performance score
            performance_score = self._calculate_performance_score(product)

            # Generate trend analysis
            trend_analysis = self._generate_trend_analysis(product)

            # Set analysis results
            product.set_analyzed(performance_score, trend_analysis)

            self.logger.info(
                f"Product {product.technical_id} analysis completed successfully. "
                f"Performance Score: {performance_score:.2f}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_score(self, product: Product) -> float:
        """
        Calculate performance score based on sales, revenue, and inventory metrics.

        Args:
            product: The Product entity to analyze

        Returns:
            Performance score between 0 and 100
        """
        # Base score components
        sales_score = 0.0
        revenue_score = 0.0
        inventory_score = 0.0

        # Sales volume scoring (0-40 points)
        if product.sales_volume is not None:
            if product.sales_volume >= 200:
                sales_score = 40.0
            elif product.sales_volume >= 100:
                sales_score = 30.0 + (product.sales_volume - 100) * 0.1
            elif product.sales_volume >= 50:
                sales_score = 20.0 + (product.sales_volume - 50) * 0.2
            else:
                sales_score = product.sales_volume * 0.4

        # Revenue scoring (0-35 points)
        if product.revenue is not None:
            if product.revenue >= 5000:
                revenue_score = 35.0
            elif product.revenue >= 2000:
                revenue_score = 25.0 + (product.revenue - 2000) * 0.0033
            elif product.revenue >= 500:
                revenue_score = 15.0 + (product.revenue - 500) * 0.0067
            else:
                revenue_score = product.revenue * 0.03

        # Inventory efficiency scoring (0-25 points)
        if product.inventory_level is not None:
            if product.stock_status == "IN_STOCK":
                inventory_score = 25.0
            elif product.stock_status == "LOW_STOCK":
                inventory_score = 20.0
            elif product.stock_status == "RESTOCK_NEEDED":
                inventory_score = 15.0
            elif product.stock_status == "OUT_OF_STOCK":
                inventory_score = 5.0
            else:
                inventory_score = 10.0

        # Calculate total score
        total_score = sales_score + revenue_score + inventory_score

        # Apply category-specific adjustments
        category_bonus = self._get_category_performance_bonus(product.category)
        total_score += category_bonus

        # Ensure score is within 0-100 range
        final_score = max(0.0, min(100.0, total_score))

        self.logger.debug(
            f"Performance calculation for {product.name}: "
            f"Sales={sales_score:.1f}, Revenue={revenue_score:.1f}, "
            f"Inventory={inventory_score:.1f}, Category Bonus={category_bonus:.1f}, "
            f"Final={final_score:.1f}"
        )

        return round(final_score, 2)

    def _get_category_performance_bonus(self, category: str) -> float:
        """
        Get category-specific performance bonus/penalty.

        Args:
            category: Product category

        Returns:
            Bonus points (can be negative)
        """
        category_bonuses = {
            "FOOD": 5.0,  # High demand category
            "TOYS": 3.0,  # Popular category
            "HEALTH": 4.0,  # High-value category
            "DOGS": 2.0,  # Popular pet category
            "CATS": 2.0,  # Popular pet category
            "ACCESSORIES": 1.0,
            "FISH": 0.0,
            "BIRDS": -1.0,  # Lower demand
            "REPTILES": -2.0,  # Niche category
            "SMALL_PETS": -1.0,
        }

        return category_bonuses.get(category, 0.0)

    def _generate_trend_analysis(self, product: Product) -> Dict[str, Any]:
        """
        Generate trend analysis data for the product.

        Note: This is a simulated implementation. In a real system, this would
        analyze historical data to identify actual trends.

        Args:
            product: The Product entity to analyze

        Returns:
            Dictionary containing trend analysis data
        """
        # Simulate trend analysis based on current metrics
        trend_direction = "stable"
        trend_strength = "moderate"

        # Determine trend based on performance score
        if product.performance_score is not None:
            if product.performance_score >= 70:
                trend_direction = "upward"
                trend_strength = "strong"
            elif product.performance_score >= 50:
                trend_direction = "upward"
                trend_strength = "moderate"
            elif product.performance_score >= 30:
                trend_direction = "stable"
                trend_strength = "moderate"
            else:
                trend_direction = "downward"
                trend_strength = "weak"

        # Generate insights based on metrics
        insights = []

        if product.sales_volume and product.sales_volume >= 200:
            insights.append("High sales volume indicates strong market demand")
        elif product.sales_volume and product.sales_volume <= 20:
            insights.append("Low sales volume suggests need for marketing boost")

        if product.revenue and product.revenue >= 3000:
            insights.append("Strong revenue performance")
        elif product.revenue and product.revenue <= 500:
            insights.append("Revenue below expectations - consider pricing strategy")

        if product.stock_status == "OUT_OF_STOCK":
            insights.append("Out of stock - immediate restocking required")
        elif product.stock_status == "LOW_STOCK":
            insights.append("Low inventory - plan restocking soon")

        # Generate recommendations
        recommendations = []

        if product.is_high_performer():
            recommendations.append(
                "Maintain current strategy and consider expanding inventory"
            )
        elif product.is_low_performer():
            recommendations.append("Review pricing and marketing strategy")
            recommendations.append("Consider product positioning or discontinuation")

        if product.needs_restocking():
            recommendations.append("Schedule inventory replenishment")

        # Simulate seasonal factors
        seasonal_factor = random.choice(
            ["spring_boost", "summer_stable", "fall_decline", "winter_peak"]
        )

        trend_analysis = {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "insights": insights,
            "recommendations": recommendations,
            "seasonal_factor": seasonal_factor,
            "analysis_timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "confidence_score": round(random.uniform(0.7, 0.95), 2),
            "market_position": self._determine_market_position(product),
            "risk_factors": self._identify_risk_factors(product),
        }

        return trend_analysis

    def _determine_market_position(self, product: Product) -> str:
        """
        Determine the product's market position based on performance.

        Args:
            product: The Product entity

        Returns:
            Market position string
        """
        if product.performance_score is None:
            return "unknown"

        if product.performance_score >= 80:
            return "market_leader"
        elif product.performance_score >= 60:
            return "strong_performer"
        elif product.performance_score >= 40:
            return "average_performer"
        elif product.performance_score >= 20:
            return "underperformer"
        else:
            return "poor_performer"

    def _identify_risk_factors(self, product: Product) -> List[str]:
        """
        Identify potential risk factors for the product.

        Args:
            product: The Product entity

        Returns:
            List of risk factors
        """
        risk_factors = []

        if product.stock_status == "OUT_OF_STOCK":
            risk_factors.append("inventory_shortage")

        if product.sales_volume and product.sales_volume <= 10:
            risk_factors.append("low_demand")

        if product.revenue and product.revenue <= 200:
            risk_factors.append("low_profitability")

        if product.category in ["REPTILES", "BIRDS"]:
            risk_factors.append("niche_market")

        if product.performance_score and product.performance_score <= 25:
            risk_factors.append("poor_performance")

        return risk_factors
