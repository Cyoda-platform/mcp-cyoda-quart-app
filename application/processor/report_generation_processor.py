"""
ReportGenerationProcessor for Product Performance Analysis and Reporting System

Handles report generation for Report entities, collecting data from Pet and Store
entities to create comprehensive performance analysis reports.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from application.entity.pet.version_1.pet import Pet
from application.entity.report.version_1.report import Report
from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles report generation.

    Collects data from Pet and Store entities to generate:
    - Performance analysis reports
    - Summary statistics
    - Recommendations
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates performance analysis reports from Pet and Store data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to generate performance analysis report.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters

        Returns:
            The Report entity with generated report data
        """
        try:
            self.logger.info(
                f"Processing Report generation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Collect data from Pet and Store entities
            pet_data = await self._collect_pet_data()
            store_data = await self._collect_store_data()

            # Generate report data
            report_data = self._generate_report_data(report, pet_data, store_data)

            # Generate summary and recommendations
            summary = self._generate_summary(report_data)
            recommendations = self._generate_recommendations(report_data)

            # Update report with generated data
            report.generate_report(report_data, "ReportGenerationProcessor")
            report.summary = summary
            report.recommendations = recommendations

            # Set performance metrics
            total_pets = len(pet_data)
            stores_count = len(store_data)
            overall_score = report_data.get("overall_performance_score", 0.0)
            report.set_performance_metrics(total_pets, stores_count, overall_score)

            self.logger.info(
                f"Report {report.technical_id} generated successfully. "
                f"Analyzed {total_pets} pets from {stores_count} stores."
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _collect_pet_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from all Pet entities.

        Returns:
            List of pet data dictionaries
        """
        try:
            entity_service = get_entity_service()

            # Find all Pet entities
            pet_results = await entity_service.find_all(
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

            pet_data: List[Dict[str, Any]] = []
            for result in pet_results:
                if hasattr(result, "data"):
                    if hasattr(result.data, "model_dump"):
                        pet_dict = result.data.model_dump()
                    else:
                        pet_dict = result.data if isinstance(result.data, dict) else {}
                    pet_data.append(pet_dict)

            self.logger.info(f"Collected data from {len(pet_data)} pets")
            return pet_data

        except Exception as e:
            self.logger.error(f"Error collecting pet data: {str(e)}")
            return []

    async def _collect_store_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from all Store entities.

        Returns:
            List of store data dictionaries
        """
        try:
            entity_service = get_entity_service()

            # Find all Store entities
            store_results = await entity_service.find_all(
                entity_class=Store.ENTITY_NAME,
                entity_version=str(Store.ENTITY_VERSION),
            )

            store_data: List[Dict[str, Any]] = []
            for result in store_results:
                if hasattr(result, "data"):
                    if hasattr(result.data, "model_dump"):
                        store_dict = result.data.model_dump()
                    else:
                        store_dict = result.data if isinstance(result.data, dict) else {}
                    store_data.append(store_dict)

            self.logger.info(f"Collected data from {len(store_data)} stores")
            return store_data

        except Exception as e:
            self.logger.error(f"Error collecting store data: {str(e)}")
            return []

    def _generate_report_data(
        self,
        report: Report,
        pet_data: List[Dict[str, Any]],
        store_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report data from collected entity data.

        Args:
            report: The Report entity
            pet_data: List of pet data
            store_data: List of store data

        Returns:
            Dictionary containing complete report data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Pet analysis
        pet_analysis = self._analyze_pets(pet_data)

        # Store analysis
        store_analysis = self._analyze_stores(store_data)

        # Overall performance calculation
        overall_score = self._calculate_overall_performance(
            pet_analysis, store_analysis
        )

        report_data = {
            "report_metadata": {
                "generated_at": current_timestamp,
                "report_type": report.report_type,
                "report_period": report.report_period,
                "data_sources": [
                    "Pet Store API",
                    "Cyoda Pet Entities",
                    "Cyoda Store Entities",
                ],
            },
            "pet_analysis": pet_analysis,
            "store_analysis": store_analysis,
            "overall_performance_score": overall_score,
            "key_metrics": {
                "total_pets_analyzed": len(pet_data),
                "total_stores_analyzed": len(store_data),
                "average_pet_score": pet_analysis.get("average_performance_score", 0.0),
                "average_store_score": store_analysis.get(
                    "average_performance_score", 0.0
                ),
            },
            "trends": self._analyze_trends(pet_data, store_data),
        }

        return report_data

    def _analyze_pets(self, pet_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pet performance data"""
        if not pet_data:
            return {"total_pets": 0, "average_performance_score": 0.0}

        total_pets = len(pet_data)
        performance_scores = []
        status_distribution = {"available": 0, "pending": 0, "sold": 0, "unknown": 0}
        category_distribution = {}

        for pet in pet_data:
            # Performance score
            score = pet.get("performance_score", 0.0)
            if score:
                performance_scores.append(score)

            # Status distribution
            status = pet.get("status", "unknown")
            if status in status_distribution:
                status_distribution[status] += 1
            else:
                status_distribution["unknown"] += 1

            # Category distribution
            category = pet.get("category", {})
            if isinstance(category, dict):
                cat_name = category.get("name", "Unknown")
            else:
                cat_name = "Unknown"
            category_distribution[cat_name] = category_distribution.get(cat_name, 0) + 1

        avg_score = (
            sum(performance_scores) / len(performance_scores)
            if performance_scores
            else 0.0
        )

        return {
            "total_pets": total_pets,
            "average_performance_score": avg_score,
            "performance_scores": performance_scores,
            "status_distribution": status_distribution,
            "category_distribution": category_distribution,
            "top_performing_pets": self._get_top_performers(
                pet_data, "performance_score"
            ),
        }

    def _analyze_stores(self, store_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze store performance data"""
        if not store_data:
            return {"total_stores": 0, "average_performance_score": 0.0}

        total_stores = len(store_data)
        performance_scores = []
        total_inventory = 0

        for store in store_data:
            # Performance metrics
            perf_metrics = store.get("performance_metrics", {})
            if isinstance(perf_metrics, dict):
                scores = perf_metrics.get("scores", {})
                if isinstance(scores, dict):
                    overall_score = scores.get("overall_score", 0.0)
                    if overall_score:
                        performance_scores.append(overall_score)

            # Inventory totals
            total_pets = store.get("total_pets", 0)
            if total_pets:
                total_inventory += total_pets

        avg_score = (
            sum(performance_scores) / len(performance_scores)
            if performance_scores
            else 0.0
        )

        return {
            "total_stores": total_stores,
            "average_performance_score": avg_score,
            "total_inventory": total_inventory,
            "average_inventory_per_store": (
                total_inventory / total_stores if total_stores > 0 else 0
            ),
            "performance_scores": performance_scores,
        }

    def _calculate_overall_performance(
        self, pet_analysis: Dict[str, Any], store_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall performance score"""
        pet_score = pet_analysis.get("average_performance_score", 0.0)
        store_score = store_analysis.get("average_performance_score", 0.0)

        # Weighted average (60% pets, 40% stores)
        overall_score = (pet_score * 0.6) + (store_score * 0.4)
        return round(overall_score, 2)

    def _analyze_trends(
        self, pet_data: List[Dict[str, Any]], store_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trends in the data"""
        return {
            "pet_trends": {
                "most_common_status": self._get_most_common_value(pet_data, "status"),
                "most_popular_category": self._get_most_popular_category(pet_data),
            },
            "store_trends": {
                "average_availability_rate": self._calculate_avg_availability_rate(
                    store_data
                ),
                "average_sales_rate": self._calculate_avg_sales_rate(store_data),
            },
        }

    def _get_top_performers(
        self, data: List[Dict[str, Any]], score_field: str
    ) -> List[Dict[str, Any]]:
        """Get top performing entities"""
        scored_items = [item for item in data if item.get(score_field, 0) > 0]
        sorted_items = sorted(
            scored_items, key=lambda x: x.get(score_field, 0), reverse=True
        )
        return sorted_items[:5]  # Top 5

    def _get_most_common_value(self, data: List[Dict[str, Any]], field: str) -> str:
        """Get most common value for a field"""
        values = [item.get(field) for item in data if item.get(field)]
        if not values:
            return "Unknown"
        return max(set(values), key=values.count)

    def _get_most_popular_category(self, pet_data: List[Dict[str, Any]]) -> str:
        """Get most popular pet category"""
        categories = []
        for pet in pet_data:
            category = pet.get("category", {})
            if isinstance(category, dict):
                cat_name = category.get("name")
                if cat_name:
                    categories.append(cat_name)

        if not categories:
            return "Unknown"
        return max(set(categories), key=categories.count)

    def _calculate_avg_availability_rate(
        self, store_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate average availability rate across stores"""
        rates = []
        for store in store_data:
            perf_metrics = store.get("performance_metrics", {})
            if isinstance(perf_metrics, dict):
                rates_data = perf_metrics.get("rates", {})
                if isinstance(rates_data, dict):
                    rate = rates_data.get("availability_rate")
                    if rate is not None:
                        rates.append(rate)

        return sum(rates) / len(rates) if rates else 0.0

    def _calculate_avg_sales_rate(self, store_data: List[Dict[str, Any]]) -> float:
        """Calculate average sales rate across stores"""
        rates = []
        for store in store_data:
            perf_metrics = store.get("performance_metrics", {})
            if isinstance(perf_metrics, dict):
                rates_data = perf_metrics.get("rates", {})
                if isinstance(rates_data, dict):
                    rate = rates_data.get("sales_rate")
                    if rate is not None:
                        rates.append(rate)

        return sum(rates) / len(rates) if rates else 0.0

    def _generate_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary"""
        key_metrics = report_data.get("key_metrics", {})
        overall_score = report_data.get("overall_performance_score", 0.0)

        total_pets = key_metrics.get("total_pets_analyzed", 0)
        total_stores = key_metrics.get("total_stores_analyzed", 0)

        summary = f"""
Performance Analysis Summary:

This report analyzes {total_pets} pets across {total_stores} stores with an overall performance score of {overall_score:.1f}/100.

Key Findings:
- Average pet performance score: {key_metrics.get('average_pet_score', 0.0):.1f}/100
- Average store performance score: {key_metrics.get('average_store_score', 0.0):.1f}/100

The analysis covers inventory management, pet availability, and sales performance metrics.
        """.strip()

        return summary

    def _generate_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on report data"""
        recommendations = []
        overall_score = report_data.get("overall_performance_score", 0.0)

        if overall_score < 60.0:
            recommendations.append(
                "Overall performance is below average - consider reviewing inventory and sales strategies"
            )

        pet_analysis = report_data.get("pet_analysis", {})
        if pet_analysis.get("average_performance_score", 0.0) < 50.0:
            recommendations.append(
                "Pet performance scores are low - focus on improving data completeness and availability"
            )

        store_analysis = report_data.get("store_analysis", {})
        if store_analysis.get("average_performance_score", 0.0) < 50.0:
            recommendations.append(
                "Store performance needs improvement - review inventory management processes"
            )

        if overall_score >= 80.0:
            recommendations.append(
                "Excellent performance - consider expanding operations or exploring new markets"
            )

        return recommendations
