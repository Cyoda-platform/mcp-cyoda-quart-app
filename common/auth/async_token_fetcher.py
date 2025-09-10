import asyncio
import logging
import time
from typing import Any, Mapping, Optional

from authlib.integrations.httpx_client import (
    AsyncOAuth2Client,  # type: ignore[import-untyped]
)

from common.auth.base_token_fetcher import BaseTokenFetcher
from common.performance.cache import get_cache_manager

# Removed metrics dependency for simplicity

logger = logging.getLogger(__name__)


class AsyncTokenFetcher(BaseTokenFetcher):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._client: AsyncOAuth2Client = AsyncOAuth2Client(  # type: ignore[call-arg]
            client_id=client_id, client_secret=client_secret, scope=scope
        )
        self._token_url: str = token_url
        self._lock: asyncio.Lock = asyncio.Lock()
        self._cache = get_cache_manager()
        self._cache_key: str = f"auth_token:{client_id}"

        # Ensure cache is not None
        if self._cache is None:
            logger.error(
                "Cache manager is None! This will cause authentication failures."
            )
            raise RuntimeError("Cache manager not available")

    # Removed timed_operation decorator for simplicity
    async def get_token(self) -> str:  # type: ignore[override]
        async with self._lock:
            # Try cache first (with error handling)
            cached_token: Optional[str] = None
            try:
                if self._cache is not None:
                    cached_token = await self._cache.async_get(self._cache_key)  # type: ignore[attr-defined]
                    if cached_token and not self.is_token_stale():
                        logger.debug("Retrieved token from cache")
                        return cached_token
            except Exception as e:
                logger.warning(f"Failed to retrieve token from cache: {e}")

            # Fetch new token if stale or not cached
            if self.is_token_stale():
                try:
                    logger.debug("Fetching new token from OAuth server")
                    token: Mapping[str, Any] = await self._client.fetch_token(url=self._token_url)  # type: ignore[no-untyped-call]
                    self._update_token(dict(token))  # provided by BaseTokenFetcher

                    # Cache the token with TTL slightly less than expiry (with error handling)
                    try:
                        if self._cache is not None:
                            # Calculate remaining time until expiry
                            remaining_time = (
                                int(self._access_token_expiry - time.time())  # type: ignore[attr-defined]
                                if self._access_token_expiry  # type: ignore[attr-defined]
                                else 300
                            )
                            cache_ttl = max(
                                300, remaining_time - 60
                            )  # At least 5 minutes, but 1 minute before expiry
                            await self._cache.async_set(  # type: ignore[attr-defined]
                                self._cache_key, self._access_token, ttl=cache_ttl  # type: ignore[attr-defined]
                            )
                            logger.info(
                                f"Successfully fetched and cached new token (expires in {remaining_time}s)"
                            )
                        else:
                            # Calculate remaining time for logging
                            remaining_time = (
                                int(self._access_token_expiry - time.time())  # type: ignore[attr-defined]
                                if self._access_token_expiry  # type: ignore[attr-defined]
                                else 300
                            )
                            logger.info(
                                f"Successfully fetched new token (expires in {remaining_time}s) - cache not available"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to cache token: {e}")

                except Exception as e:
                    logger.error(f"Failed to fetch token: {e}")
                    raise

            return self._access_token or ""  # type: ignore[attr-defined]

    def invalidate_tokens(self) -> None:
        """Invalidate cached tokens."""
        super().invalidate_tokens()
        # Clear from cache - handle both sync and async contexts
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._cache.async_delete(self._cache_key))  # type: ignore[attr-defined]
        except RuntimeError:
            # No running event loop, clear cache synchronously
            self._cache.delete(self._cache_key)  # type: ignore[attr-defined]
        logger.debug("Invalidated cached tokens")
