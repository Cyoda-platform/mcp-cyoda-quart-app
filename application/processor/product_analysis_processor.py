"""
ProductAnalysisProcessor for Pet Store Performance Analysis System

Handles performance analysis for Product entities, calculating metrics like
performance scores and inventory turnover rates as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.product.version_1.product import Product


class ProductAnalysisProcessor(CyodaProcessor):
    """
    Processor for Product entity that performs performance analysis,
    calculates metrics, and updates product performance data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductAnalysisProcessor",
            description="Analyzes Product performance metrics and calculates scores",
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
            The processed entity with updated performance metrics
        """
        try:
            self.logger.info(
                f"Analyzing Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Calculate performance score
            performance_score = self._calculate_performance_score(product)
            
            # Calculate inventory turnover rate
            turnover_rate = self._calculate_inventory_turnover_rate(product)
            
            # Update product with calculated metrics
            product.set_performance_metrics(performance_score, turnover_rate)

            self.logger.info(
                f"Product {product.technical_id} analyzed - Score: {performance_score:.2f}, Turnover: {turnover_rate:.2f}"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error analyzing Product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_performance_score(self, product: Product) -> float:
        """
        Calculate performance score based on sales volume, revenue, and stock status.
        
        Args:
            product: The Product entity to analyze
            
        Returns:
            Performance score (0-100)
        """
        score = 0.0
        
        # Sales volume component (40% of score)
        sales_volume = product.sales_volume or 0
        if sales_volume > 100:
            score += 40.0
        elif sales_volume > 50:
            score += 30.0
        elif sales_volume > 20:
            score += 20.0
        elif sales_volume > 0:
            score += 10.0
        
        # Revenue component (40% of score)
        revenue = product.revenue or 0.0
        if revenue > 1000.0:
            score += 40.0
        elif revenue > 500.0:
            score += 30.0
        elif revenue > 200.0:
            score += 20.0
        elif revenue > 0.0:
            score += 10.0
        
        # Stock availability component (20% of score)
        stock_level = product.stock_level or 0
        if stock_level > 50:
            score += 20.0
        elif stock_level > 20:
            score += 15.0
        elif stock_level > 10:
            score += 10.0
        elif stock_level > 0:
            score += 5.0
        
        return min(score, 100.0)

    def _calculate_inventory_turnover_rate(self, product: Product) -> float:
        """
        Calculate inventory turnover rate based on sales and stock levels.
        
        Args:
            product: The Product entity to analyze
            
        Returns:
            Inventory turnover rate
        """
        sales_volume = product.sales_volume or 0
        stock_level = product.stock_level or 1  # Avoid division by zero
        
        if stock_level == 0:
            # If no stock, return high turnover if there were sales
            return 10.0 if sales_volume > 0 else 0.0
        
        # Simple turnover calculation: sales / average stock
        # Assuming current stock is representative of average stock
        turnover_rate = sales_volume / stock_level
        
        return round(turnover_rate, 2)
