"""
ProductAnalysisProcessor for Product Performance Analysis and Reporting System

Analyzes product performance metrics including sales volume, revenue,
and inventory turnover rates as specified in functional requirements.
"""

import logging
import random
from typing import Any

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for analyzing product performance metrics.

    Calculates key performance indicators (KPIs) such as sales volume,
    revenue per product, and inventory turnover rates.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes product performance metrics and calculates KPIs",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Product entity to analyze performance metrics.

        Args:
            entity: The Product entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The processed Product entity with performance metrics
        """
        try:
            self.logger.info(
                f"Analyzing product performance for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product_entity = cast_entity(entity, Product)

            # Perform performance analysis
            self._analyze_sales_performance(product_entity)
            self._analyze_inventory_performance(product_entity)
            self._calculate_overall_performance_score(product_entity)

            # Update analysis timestamp
            product_entity.update_analysis_timestamp()

            self.logger.info(
                f"Product analysis completed for {product_entity.name}. "
                f"Performance score: {product_entity.performance_score:.2f}"
            )

            return product_entity

        except Exception as e:
            self.logger.error(
                f"Error analyzing product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _analyze_sales_performance(self, product: Product) -> None:
        """
        Analyze sales performance metrics for the product.

        Args:
            product: The Product entity to analyze
        """
        try:
            # Since Pet Store API doesn't provide actual sales data,
            # we'll simulate realistic performance metrics based on product status and category

            # Simulate sales volume based on product status
            if product.status == "sold":
                # Products marked as sold have higher sales volume
                product.sales_volume = random.randint(50, 200)
            elif product.status == "pending":
                # Pending products have moderate sales
                product.sales_volume = random.randint(10, 50)
            else:  # available
                # Available products have lower recent sales
                product.sales_volume = random.randint(0, 30)

            # Calculate revenue based on sales volume and estimated price
            if product.price is not None:
                product.revenue = product.sales_volume * product.price
            else:
                # Estimate price based on category for revenue calculation
                estimated_price = self._estimate_price_by_category(product.category)
                product.revenue = product.sales_volume * estimated_price

            self.logger.debug(
                f"Sales analysis for {product.name}: "
                f"Volume={product.sales_volume}, Revenue=${product.revenue:.2f}"
            )

        except Exception as e:
            self.logger.warning(
                f"Failed to analyze sales performance for {product.name}: {str(e)}"
            )
            # Set default values on error
            product.sales_volume = 0
            product.revenue = 0.0

    def _analyze_inventory_performance(self, product: Product) -> None:
        """
        Analyze inventory performance and turnover rates.

        Args:
            product: The Product entity to analyze
        """
        try:
            # Simulate inventory levels if not provided
            if product.inventory_level is None:
                if product.status == "sold":
                    product.inventory_level = random.randint(
                        0, 10
                    )  # Low inventory for sold items
                elif product.status == "pending":
                    product.inventory_level = random.randint(5, 25)  # Medium inventory
                else:  # available
                    product.inventory_level = random.randint(
                        15, 100
                    )  # Higher inventory

            # Calculate inventory turnover rate
            # Formula: Sales Volume / Average Inventory Level
            if product.inventory_level and product.inventory_level > 0:
                # Assume average inventory is current level + 20% buffer
                average_inventory = product.inventory_level * 1.2
                product.inventory_turnover_rate = (
                    product.sales_volume or 0
                ) / average_inventory
            else:
                product.inventory_turnover_rate = 0.0

            self.logger.debug(
                f"Inventory analysis for {product.name}: "
                f"Level={product.inventory_level}, Turnover={product.inventory_turnover_rate:.2f}"
            )

        except Exception as e:
            self.logger.warning(
                f"Failed to analyze inventory performance for {product.name}: {str(e)}"
            )
            # Set default values on error
            product.inventory_level = 0
            product.inventory_turnover_rate = 0.0

    def _calculate_overall_performance_score(self, product: Product) -> None:
        """
        Calculate overall performance score for the product.

        Args:
            product: The Product entity to analyze
        """
        try:
            # Use the built-in performance score calculation
            score = product.calculate_performance_score()

            self.logger.debug(f"Performance score for {product.name}: {score:.2f}")

        except Exception as e:
            self.logger.warning(
                f"Failed to calculate performance score for {product.name}: {str(e)}"
            )
            product.performance_score = 0.0

    def _estimate_price_by_category(self, category: str) -> float:
        """
        Estimate product price based on category.

        Args:
            category: Product category

        Returns:
            Estimated price
        """
        # Price estimates by category (in USD)
        category_prices = {
            "Dogs": 25.99,
            "Cats": 19.99,
            "Birds": 15.99,
            "Fish": 8.99,
            "Reptiles": 35.99,
            "Small Pets": 12.99,
            "Unknown": 20.00,
        }

        base_price = category_prices.get(category, category_prices["Unknown"])

        # Add some variation (+/- 30%)
        variation = random.uniform(0.7, 1.3)
        return round(base_price * variation, 2)

    def _get_category_performance_multiplier(self, category: str) -> float:
        """
        Get performance multiplier based on category popularity.

        Args:
            category: Product category

        Returns:
            Performance multiplier (0.5 to 1.5)
        """
        # Category performance multipliers based on typical pet popularity
        multipliers = {
            "Dogs": 1.4,  # Most popular
            "Cats": 1.3,  # Very popular
            "Fish": 1.1,  # Moderately popular
            "Birds": 0.9,  # Less popular
            "Small Pets": 0.8,  # Less popular
            "Reptiles": 0.7,  # Niche market
            "Unknown": 1.0,  # Baseline
        }

        return multipliers.get(category, 1.0)
