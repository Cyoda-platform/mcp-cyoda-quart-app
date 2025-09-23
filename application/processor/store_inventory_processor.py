"""
StoreInventoryProcessor for Product Performance Analysis and Reporting System

Handles inventory synchronization for Store entities, retrieving data from
the Pet Store API and calculating store performance metrics.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

import httpx

from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class StoreInventoryProcessor(CyodaProcessor):
    """
    Processor for Store entity that handles inventory synchronization.

    Retrieves inventory data from Pet Store API and calculates:
    - Inventory counts by status
    - Store performance metrics
    - Availability and sales rates
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreInventoryProcessor",
            description="Synchronizes Store inventory data from Pet Store API",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        self.pet_store_base_url = "https://petstore.swagger.io/v2"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Store entity to synchronize inventory data.

        Args:
            entity: The Store entity to process
            **kwargs: Additional processing parameters

        Returns:
            The Store entity with updated inventory data
        """
        try:
            self.logger.info(
                f"Processing Store inventory sync for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Retrieve inventory data from Pet Store API
            inventory_data = await self._fetch_inventory_data()

            # Update store with inventory data
            store.update_inventory(inventory_data)

            # Calculate performance metrics
            performance_metrics = self._calculate_store_performance(
                store, inventory_data
            )
            store.update_performance_metrics(performance_metrics)

            self.logger.info(
                f"Store {store.technical_id} inventory synchronized successfully. Total pets: {store.total_pets}"
            )

            return store

        except Exception as e:
            self.logger.error(
                f"Error processing store inventory {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_inventory_data(self) -> Dict[str, int]:
        """
        Fetch inventory data from Pet Store API.

        Returns:
            Dictionary with inventory counts by status
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.pet_store_base_url}/store/inventory"
                )
                response.raise_for_status()

                inventory_data = response.json()
                self.logger.info(f"Retrieved inventory data: {inventory_data}")

                # Ensure we have the expected status keys
                normalized_inventory = {
                    "available": inventory_data.get("available", 0),
                    "pending": inventory_data.get("pending", 0),
                    "sold": inventory_data.get("sold", 0),
                }

                # Add any other statuses that might exist
                for status, count in inventory_data.items():
                    if status not in normalized_inventory:
                        normalized_inventory[status] = count

                return normalized_inventory

        except httpx.RequestError as e:
            self.logger.error(f"Network error fetching inventory: {str(e)}")
            # Return default inventory data if API is unavailable
            return {"available": 0, "pending": 0, "sold": 0}
        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"HTTP error fetching inventory: {e.response.status_code}"
            )
            # Return default inventory data if API returns error
            return {"available": 0, "pending": 0, "sold": 0}
        except Exception as e:
            self.logger.error(f"Unexpected error fetching inventory: {str(e)}")
            return {"available": 0, "pending": 0, "sold": 0}

    def _calculate_store_performance(
        self, store: Store, inventory_data: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate store performance metrics.

        Args:
            store: The Store entity
            inventory_data: Current inventory data

        Returns:
            Dictionary containing performance metrics
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Basic inventory metrics
        total_pets = store.total_pets or 0
        available_pets = store.available_pets or 0
        pending_pets = store.pending_pets or 0
        sold_pets = store.sold_pets or 0

        # Calculate rates
        availability_rate = store.get_availability_rate() or 0.0
        sales_rate = store.get_sales_rate() or 0.0

        # Calculate performance scores
        availability_score = self._calculate_availability_score(availability_rate)
        sales_score = self._calculate_sales_score(sales_rate)
        inventory_health_score = self._calculate_inventory_health_score(
            available_pets, pending_pets, sold_pets, total_pets
        )

        # Overall performance score (weighted average)
        overall_score = (
            availability_score * 0.4 + sales_score * 0.3 + inventory_health_score * 0.3
        )

        performance_metrics = {
            "calculated_at": current_timestamp,
            "store_name": store.store_name,
            "inventory_summary": {
                "total_pets": total_pets,
                "available_pets": available_pets,
                "pending_pets": pending_pets,
                "sold_pets": sold_pets,
            },
            "rates": {
                "availability_rate": availability_rate,
                "sales_rate": sales_rate,
                "pending_rate": (
                    (pending_pets / total_pets * 100.0) if total_pets > 0 else 0.0
                ),
            },
            "scores": {
                "availability_score": availability_score,
                "sales_score": sales_score,
                "inventory_health_score": inventory_health_score,
                "overall_score": overall_score,
            },
            "performance_tier": self._determine_performance_tier(overall_score),
            "recommendations": self._generate_recommendations(
                availability_rate, sales_rate, available_pets, pending_pets, sold_pets
            ),
        }

        return performance_metrics

    def _calculate_availability_score(self, availability_rate: float) -> float:
        """Calculate availability score based on availability rate"""
        if availability_rate >= 80.0:
            return 100.0
        elif availability_rate >= 60.0:
            return 80.0
        elif availability_rate >= 40.0:
            return 60.0
        elif availability_rate >= 20.0:
            return 40.0
        else:
            return 20.0

    def _calculate_sales_score(self, sales_rate: float) -> float:
        """Calculate sales score based on sales rate"""
        if sales_rate >= 50.0:
            return 100.0
        elif sales_rate >= 30.0:
            return 80.0
        elif sales_rate >= 15.0:
            return 60.0
        elif sales_rate >= 5.0:
            return 40.0
        else:
            return 20.0

    def _calculate_inventory_health_score(
        self, available: int, pending: int, sold: int, total: int
    ) -> float:
        """Calculate inventory health score based on distribution"""
        if total == 0:
            return 0.0

        # Ideal distribution: 60% available, 20% pending, 20% sold
        available_ratio = available / total
        pending_ratio = pending / total
        sold_ratio = sold / total

        # Calculate deviation from ideal
        available_deviation = abs(available_ratio - 0.6)
        pending_deviation = abs(pending_ratio - 0.2)
        sold_deviation = abs(sold_ratio - 0.2)

        # Average deviation (lower is better)
        avg_deviation = (available_deviation + pending_deviation + sold_deviation) / 3

        # Convert to score (0-100, where 0 deviation = 100 score)
        health_score = max(0.0, 100.0 - (avg_deviation * 200))

        return health_score

    def _determine_performance_tier(self, overall_score: float) -> str:
        """Determine performance tier based on overall score"""
        if overall_score >= 90.0:
            return "excellent"
        elif overall_score >= 75.0:
            return "good"
        elif overall_score >= 60.0:
            return "average"
        elif overall_score >= 40.0:
            return "below_average"
        else:
            return "poor"

    def _generate_recommendations(
        self,
        availability_rate: float,
        sales_rate: float,
        available: int,
        pending: int,
        sold: int,
    ) -> list[str]:
        """Generate recommendations based on store performance"""
        recommendations = []

        if availability_rate < 50.0:
            recommendations.append(
                "Consider increasing available inventory to improve customer satisfaction"
            )

        if sales_rate < 20.0:
            recommendations.append(
                "Review pricing and marketing strategies to improve sales performance"
            )

        if pending > available:
            recommendations.append(
                "High pending inventory may indicate processing bottlenecks"
            )

        if available == 0:
            recommendations.append("No available inventory - urgent restocking needed")

        if sales_rate > 80.0:
            recommendations.append(
                "Excellent sales performance - consider expanding inventory"
            )

        total = available + pending + sold
        if total < 10:
            recommendations.append(
                "Low total inventory - consider expanding product range"
            )

        return recommendations
