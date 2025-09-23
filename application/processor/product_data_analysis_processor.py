"""
ProductDataAnalysisProcessor for Product Performance Analysis System

Handles analysis of product performance data including KPI calculations,
trend analysis, and performance scoring as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor

from application.entity.product_data.version_1.product_data import ProductData


class ProductDataAnalysisProcessor(CyodaProcessor):
    """
    Processor for analyzing product performance data.
    
    Performs KPI calculations, trend analysis, and sets performance flags
    for ProductData entities based on business rules.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductDataAnalysisProcessor",
            description="Analyzes product performance data and calculates KPIs and trends",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze product performance data and calculate metrics.

        Args:
            entity: The ProductData entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The entity with updated analysis results
        """
        try:
            self.logger.info(
                f"Starting performance analysis for ProductData {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to ProductData for type-safe operations
            product_data = cast_entity(entity, ProductData)

            # Perform comprehensive performance analysis
            await self._analyze_performance_metrics(product_data)
            await self._analyze_inventory_status(product_data)
            await self._analyze_sales_trends(product_data)
            await self._set_performance_flags(product_data)

            self.logger.info(
                f"Completed performance analysis for product {product_data.product_id} - "
                f"Score: {product_data.performance_score:.1f}, "
                f"High Performer: {product_data.is_high_performer}, "
                f"Needs Restock: {product_data.requires_restocking}"
            )

            return product_data

        except Exception as e:
            self.logger.error(
                f"Error analyzing entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _analyze_performance_metrics(self, product_data: ProductData) -> None:
        """
        Analyze and calculate performance metrics for the product.

        Args:
            product_data: The ProductData entity to analyze
        """
        # Recalculate performance metrics with updated business rules
        product_data.calculate_performance_metrics()
        
        # Additional performance analysis based on category
        category_performance_thresholds = {
            "Dogs": {"high_sales": 100, "high_revenue": 5000},
            "Cats": {"high_sales": 80, "high_revenue": 4000},
            "Birds": {"high_sales": 50, "high_revenue": 2500},
            "Fish": {"high_sales": 60, "high_revenue": 3000},
            "Reptiles": {"high_sales": 30, "high_revenue": 2000},
        }
        
        thresholds = category_performance_thresholds.get(
            product_data.category, 
            {"high_sales": 50, "high_revenue": 2500}
        )
        
        # Adjust performance score based on category-specific thresholds
        sales_performance = min((product_data.sales_volume or 0) / thresholds["high_sales"], 1.0)
        revenue_performance = min((product_data.revenue or 0) / thresholds["high_revenue"], 1.0)
        
        # Weighted performance score (60% sales, 40% revenue)
        product_data.performance_score = (sales_performance * 60) + (revenue_performance * 40)
        
        self.logger.info(
            f"Calculated performance metrics for {product_data.product_id}: "
            f"turnover={product_data.inventory_turnover_rate:.2f}, "
            f"score={product_data.performance_score:.1f}"
        )

    async def _analyze_inventory_status(self, product_data: ProductData) -> None:
        """
        Analyze inventory status and set restocking flags.

        Args:
            product_data: The ProductData entity to analyze
        """
        stock_level = product_data.stock_level or 0
        sales_volume = product_data.sales_volume or 0
        
        # Category-specific restocking thresholds
        category_restock_thresholds = {
            "Dogs": 15,
            "Cats": 12,
            "Birds": 8,
            "Fish": 10,
            "Reptiles": 5,
        }
        
        restock_threshold = category_restock_thresholds.get(product_data.category, 10)
        
        # Set restocking flag based on stock level and sales velocity
        if stock_level < restock_threshold:
            product_data.requires_restocking = True
        elif sales_volume > 50 and stock_level < (restock_threshold * 2):
            # High-selling items need higher stock levels
            product_data.requires_restocking = True
        else:
            product_data.requires_restocking = False
            
        self.logger.info(
            f"Inventory analysis for {product_data.product_id}: "
            f"stock={stock_level}, threshold={restock_threshold}, "
            f"requires_restock={product_data.requires_restocking}"
        )

    async def _analyze_sales_trends(self, product_data: ProductData) -> None:
        """
        Analyze sales trends and identify slow-moving inventory.

        Args:
            product_data: The ProductData entity to analyze
        """
        sales_volume = product_data.sales_volume or 0
        stock_level = product_data.stock_level or 0
        
        # Define slow-moving criteria based on category
        category_slow_moving_thresholds = {
            "Dogs": {"max_sales": 20, "min_stock": 30},
            "Cats": {"max_sales": 15, "min_stock": 25},
            "Birds": {"max_sales": 10, "min_stock": 20},
            "Fish": {"max_sales": 12, "min_stock": 25},
            "Reptiles": {"max_sales": 8, "min_stock": 15},
        }
        
        thresholds = category_slow_moving_thresholds.get(
            product_data.category,
            {"max_sales": 15, "min_stock": 25}
        )
        
        # Identify slow-moving inventory
        if (sales_volume <= thresholds["max_sales"] and 
            stock_level >= thresholds["min_stock"]):
            product_data.is_slow_moving = True
        else:
            product_data.is_slow_moving = False
            
        self.logger.info(
            f"Sales trend analysis for {product_data.product_id}: "
            f"sales={sales_volume}, stock={stock_level}, "
            f"slow_moving={product_data.is_slow_moving}"
        )

    async def _set_performance_flags(self, product_data: ProductData) -> None:
        """
        Set performance flags based on analysis results.

        Args:
            product_data: The ProductData entity to update
        """
        # High performer criteria: score >= 70 OR (high sales AND good turnover)
        high_sales_threshold = 100
        good_turnover_threshold = 2.0
        
        if (product_data.performance_score >= 70 or 
            ((product_data.sales_volume or 0) >= high_sales_threshold and 
             (product_data.inventory_turnover_rate or 0) >= good_turnover_threshold)):
            product_data.is_high_performer = True
        else:
            product_data.is_high_performer = False
            
        self.logger.info(
            f"Performance flags set for {product_data.product_id}: "
            f"high_performer={product_data.is_high_performer}, "
            f"slow_moving={product_data.is_slow_moving}, "
            f"requires_restock={product_data.requires_restocking}"
        )
