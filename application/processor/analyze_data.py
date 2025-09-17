"""
AnalyzeDataProcessor for Cyoda Client Application

Performs pandas analysis on downloaded data and generates insights.
Populates results and metrics fields according to workflow requirements.
"""

import io
import logging
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
import pandas as pd

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.dataanalysis.version_1.dataanalysis import DataAnalysis
from application.entity.datasource.version_1.datasource import DataSource
from services.services import get_entity_service


class AnalyzeDataProcessor(CyodaProcessor):
    """
    Processor for DataAnalysis that performs pandas analysis on data.
    Generates insights, statistics, and metrics from downloaded data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="analyze_data",
            description="Performs pandas analysis on downloaded data and generates insights",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze data from the referenced DataSource.

        Args:
            entity: The DataAnalysis entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with analysis results and metrics
        """
        try:
            self.logger.info(
                f"Starting analysis for DataAnalysis {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataAnalysis for type-safe operations
            analysis = cast_entity(entity, DataAnalysis)

            # Get the referenced DataSource
            entity_service = get_entity_service()
            datasource_response = await entity_service.get_by_id(
                entity_id=analysis.data_source_id,
                entity_class=DataSource.ENTITY_NAME,
                entity_version=str(DataSource.ENTITY_VERSION),
            )

            if not datasource_response:
                raise ValueError(f"DataSource {analysis.data_source_id} not found")

            datasource = cast_entity(datasource_response.data, DataSource)

            # Download data for analysis
            data = await self._download_data_for_analysis(datasource.url)
            
            # Perform analysis based on type
            results, metrics = await self._perform_analysis(data, analysis.analysis_type)

            # Update analysis entity with results
            analysis.set_analysis_results(results, metrics)

            self.logger.info(
                f"DataAnalysis {analysis.technical_id} completed successfully"
            )

            return analysis

        except Exception as e:
            self.logger.error(
                f"Error processing DataAnalysis {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _download_data_for_analysis(self, url: str) -> pd.DataFrame:
        """Download and parse data from URL into pandas DataFrame"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse CSV data
                data_io = io.StringIO(response.text)
                df = pd.read_csv(data_io)
                
                self.logger.info(f"Loaded {len(df)} records from {url}")
                return df
                
        except Exception as e:
            self.logger.error(f"Error downloading data from {url}: {str(e)}")
            raise

    async def _perform_analysis(self, df: pd.DataFrame, analysis_type: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform analysis based on type and return results and metrics"""
        try:
            if analysis_type == "summary":
                return self._perform_summary_analysis(df)
            elif analysis_type == "statistical":
                return self._perform_statistical_analysis(df)
            elif analysis_type == "trend":
                return self._perform_trend_analysis(df)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
                
        except Exception as e:
            self.logger.error(f"Error performing {analysis_type} analysis: {str(e)}")
            raise

    def _perform_summary_analysis(self, df: pd.DataFrame) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform summary analysis"""
        results = {
            "total_records": len(df),
            "columns": list(df.columns),
            "summary_stats": df.describe().to_dict() if not df.empty else {}
        }
        
        metrics = {
            "record_count": len(df),
            "column_count": len(df.columns),
            "null_counts": df.isnull().sum().to_dict() if not df.empty else {}
        }
        
        return results, metrics

    def _perform_statistical_analysis(self, df: pd.DataFrame) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform statistical analysis"""
        results = {}
        metrics = {}
        
        if not df.empty:
            # Look for price column (common in London houses data)
            price_cols = [col for col in df.columns if 'price' in col.lower() or '£' in col]
            if price_cols:
                price_col = price_cols[0]
                results["price_stats"] = df[price_col].describe().to_dict()
                metrics["avg_price"] = float(df[price_col].mean())
                metrics["price_range"] = [float(df[price_col].min()), float(df[price_col].max())]
            
            # Look for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
                    results[f"{col.lower()}_counts"] = df[col].value_counts().head(10).to_dict()
            
            # Correlations for numeric columns
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df.columns) > 1:
                results["correlations"] = numeric_df.corr().to_dict()
        
        metrics["analysis_timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        return results, metrics

    def _perform_trend_analysis(self, df: pd.DataFrame) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform trend analysis"""
        results = {
            "trend_type": "basic",
            "data_points": len(df)
        }
        
        metrics = {
            "trend_direction": "stable",  # Simplified for demo
            "data_quality": "good" if len(df) > 100 else "limited"
        }
        
        if not df.empty:
            # Look for date columns for time-based trends
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                results["time_based_analysis"] = True
                metrics["date_range"] = {
                    "start": str(df[date_cols[0]].min()) if not df[date_cols[0]].isna().all() else None,
                    "end": str(df[date_cols[0]].max()) if not df[date_cols[0]].isna().all() else None
                }
        
        return results, metrics
