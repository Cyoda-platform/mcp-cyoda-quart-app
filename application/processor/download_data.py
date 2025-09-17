"""
DownloadDataProcessor for Cyoda Client Application

Downloads data from external URLs and updates DataSource entity with
file information and status according to workflow requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.datasource.version_1.datasource import DataSource


class DownloadDataProcessor(CyodaProcessor):
    """
    Processor for DataSource that downloads data from URLs.
    Updates file size, last downloaded timestamp, and status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="download_data",
            description="Downloads data from URL and updates DataSource with file information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Download data from the DataSource URL.

        Args:
            entity: The DataSource entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated download information
        """
        try:
            self.logger.info(
                f"Starting download for DataSource {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataSource for type-safe operations
            datasource = cast_entity(entity, DataSource)

            # Set status to downloading
            datasource.set_downloading()

            # Download data from URL
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(datasource.url)
                    response.raise_for_status()

                    # Get file size and update entity
                    file_size = len(response.content)
                    datasource.set_download_completed(file_size)

                    self.logger.info(
                        f"Successfully downloaded {file_size} bytes from {datasource.url}"
                    )

            except httpx.HTTPError as e:
                self.logger.error(f"HTTP error downloading from {datasource.url}: {str(e)}")
                datasource.set_download_failed()
                raise
            except Exception as e:
                self.logger.error(f"Error downloading from {datasource.url}: {str(e)}")
                datasource.set_download_failed()
                raise

            self.logger.info(
                f"DataSource {datasource.technical_id} download completed successfully"
            )

            return datasource

        except Exception as e:
            self.logger.error(
                f"Error processing DataSource {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
