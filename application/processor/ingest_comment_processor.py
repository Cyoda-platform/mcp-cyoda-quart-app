"""
IngestCommentProcessor for Cyoda Client Application

Handles the ingestion of comment data from external APIs.
Fetches and stores comment data as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.comment.version_1.comment import Comment
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class IngestCommentProcessor(CyodaProcessor):
    """
    Processor for Comment that handles ingestion from external APIs.
    Fetches comment data and populates the entity with ingested information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="IngestCommentProcessor",
            description="Ingests comment data from external APIs and populates entity fields",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Comment entity for ingestion.

        Args:
            entity: The Comment entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with ingested data
        """
        try:
            self.logger.info(
                f"Ingesting Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Simulate fetching data from external API
            # In a real implementation, this would call the actual external API
            api_data = self._fetch_from_external_api(
                comment.source_api, comment.external_id
            )

            # Update comment with fetched data
            if api_data:
                comment.content = api_data.get("content", comment.content)
                comment.author = api_data.get("author", comment.author)
                comment.timestamp = api_data.get("timestamp", comment.timestamp)

                # Merge metadata
                if api_data.get("metadata"):
                    if comment.metadata is None:
                        comment.metadata = {}
                    comment.metadata.update(api_data["metadata"])

            # Set ingestion timestamp
            comment.set_ingested_at()

            self.logger.info(f"Comment {comment.technical_id} ingested successfully")

            return comment

        except Exception as e:
            self.logger.error(
                f"Error ingesting comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _fetch_from_external_api(self, source_api: str, external_id: str) -> Dict[str, Any]:
        """
        Simulate fetching comment data from external API.

        In a real implementation, this would make actual API calls to the specified source.

        Args:
            source_api: The API source to fetch from
            external_id: The external comment ID

        Returns:
            Dictionary containing fetched comment data
        """
        # Simulate API response based on source
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Mock data based on source API
        mock_data = {
            "reddit": {
                "content": f"This is a sample Reddit comment with ID {external_id}",
                "author": f"reddit_user_{external_id[:8]}",
                "timestamp": current_timestamp,
                "metadata": {
                    "upvotes": 15,
                    "downvotes": 2,
                    "replies": 3,
                    "subreddit": "technology",
                },
            },
            "twitter": {
                "content": f"Sample tweet content for ID {external_id}",
                "author": f"@twitter_user_{external_id[:8]}",
                "timestamp": current_timestamp,
                "metadata": {
                    "likes": 25,
                    "retweets": 5,
                    "replies": 8,
                    "hashtags": ["#tech", "#ai"],
                },
            },
            "facebook": {
                "content": f"Facebook post content for ID {external_id}",
                "author": f"fb_user_{external_id[:8]}",
                "timestamp": current_timestamp,
                "metadata": {"likes": 42, "shares": 7, "comments": 12},
            },
        }

        # Return mock data for known sources, or generic data for unknown sources
        if source_api.lower() in mock_data:
            return mock_data[source_api.lower()]
        else:
            return {
                "content": f"Generic comment content for ID {external_id}",
                "author": f"user_{external_id[:8]}",
                "timestamp": current_timestamp,
                "metadata": {"source": source_api, "fetched_at": current_timestamp},
            }
