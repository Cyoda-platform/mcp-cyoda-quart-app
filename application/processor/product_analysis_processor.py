"""
ProductAnalysisProcessor for Pet Store Performance Analysis System

Handles product performance analysis including KPI calculations, trend analysis,
and inventory turnover rate calculations as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entity that performs performance analysis,
    calculates KPIs, and determines trend indicators.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes product performance metrics, calculates KPIs and trend indicators",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze product performance and calculate key metrics.

        Args:
            entity: The Product entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The analyzed product with performance metrics
        """
        try:
            self.logger.info(
                f"Analyzing product performance for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Calculate revenue if not already calculated
            if product.price and product.sales_volume:
                product.calculate_revenue()

            # Calculate performance metrics
            performance_data = self._calculate_performance_metrics(product)
            product.set_analysis_data(performance_data)

            # Calculate performance score
            product.performance_score = self._calculate_performance_score(product)

            # Determine trend indicator
            product.trend_indicator = self._determine_trend_indicator(product)

            # Calculate inventory turnover rate
            product.inventory_turnover_rate = self._calculate_inventory_turnover(
                product
            )

            self.logger.info(
                f"Product {product.technical_id} analyzed successfully - "
                f"Performance Score: {product.performance_score}, "
                f"Trend: {product.trend_indicator}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_metrics(self, product: Product) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics for the product.

        Args:
            product: The Product entity to analyze

        Returns:
            Dictionary containing performance metrics
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Basic metrics
        sales_volume = product.sales_volume or 0
        revenue = product.revenue or 0.0
        inventory_level = product.inventory_level or 0

        # Calculate additional metrics
        revenue_per_unit = revenue / sales_volume if sales_volume > 0 else 0.0
        stock_to_sales_ratio = (
            inventory_level / sales_volume if sales_volume > 0 else float("inf")
        )

        # Category-based performance benchmarks
        category_benchmarks = {
            "dog": {"min_sales": 50, "target_revenue": 1000.0},
            "cat": {"min_sales": 40, "target_revenue": 800.0},
            "bird": {"min_sales": 20, "target_revenue": 400.0},
            "fish": {"min_sales": 30, "target_revenue": 600.0},
            "reptile": {"min_sales": 15, "target_revenue": 300.0},
            "small-pet": {"min_sales": 25, "target_revenue": 500.0},
        }

        benchmark = category_benchmarks.get(
            product.category, {"min_sales": 30, "target_revenue": 600.0}
        )

        performance_metrics = {
            "analyzed_at": current_timestamp,
            "sales_volume": sales_volume,
            "revenue": revenue,
            "revenue_per_unit": revenue_per_unit,
            "inventory_level": inventory_level,
            "stock_to_sales_ratio": stock_to_sales_ratio,
            "category_benchmark": benchmark,
            "meets_sales_target": sales_volume >= benchmark["min_sales"],
            "meets_revenue_target": revenue >= benchmark["target_revenue"],
            "is_low_stock": inventory_level <= 10,
            "is_overstocked": stock_to_sales_ratio > 5.0 if sales_volume > 0 else False,
            "analysis_version": "1.0",
        }

        return performance_metrics

    def _calculate_performance_score(self, product: Product) -> float:
        """
        Calculate overall performance score (0-100) based on multiple factors.

        Args:
            product: The Product entity

        Returns:
            Performance score between 0 and 100
        """
        score = 0.0
        max_score = 100.0

        # Sales volume score (30% weight)
        sales_volume = product.sales_volume or 0
        if sales_volume >= 100:
            score += 30.0
        elif sales_volume >= 50:
            score += 20.0
        elif sales_volume >= 20:
            score += 15.0
        elif sales_volume > 0:
            score += 10.0

        # Revenue score (30% weight)
        revenue = product.revenue or 0.0
        if revenue >= 2000.0:
            score += 30.0
        elif revenue >= 1000.0:
            score += 20.0
        elif revenue >= 500.0:
            score += 15.0
        elif revenue > 0:
            score += 10.0

        # Inventory management score (20% weight)
        inventory_level = product.inventory_level or 0
        if 20 <= inventory_level <= 100:  # Optimal range
            score += 20.0
        elif 10 <= inventory_level < 20 or 100 < inventory_level <= 200:
            score += 15.0
        elif inventory_level > 0:
            score += 10.0

        # Status and availability score (20% weight)
        if product.status == "available":
            score += 20.0
        elif product.status == "pending":
            score += 10.0

        return min(score, max_score)

    def _determine_trend_indicator(self, product: Product) -> str:
        """
        Determine trend indicator based on performance metrics.

        Args:
            product: The Product entity

        Returns:
            Trend indicator: RISING, FALLING, or STABLE
        """
        # Simplified trend analysis based on current metrics
        performance_score = product.performance_score or 0.0
        sales_volume = product.sales_volume or 0

        # High performance and good sales indicate rising trend
        if performance_score >= 70.0 and sales_volume >= 50:
            return "RISING"

        # Low performance or very low sales indicate falling trend
        elif performance_score < 40.0 or sales_volume < 10:
            return "FALLING"

        # Everything else is stable
        else:
            return "STABLE"

    def _calculate_inventory_turnover(self, product: Product) -> float:
        """
        Calculate inventory turnover rate.

        Args:
            product: The Product entity

        Returns:
            Inventory turnover rate
        """
        sales_volume = product.sales_volume or 0
        inventory_level = product.inventory_level or 0

        if inventory_level > 0:
            # Simplified turnover calculation: sales / average inventory
            # Assuming current inventory is representative of average
            return sales_volume / inventory_level
        else:
            return 0.0
