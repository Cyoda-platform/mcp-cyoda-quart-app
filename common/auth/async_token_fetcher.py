import asyncio
import logging
from authlib.integrations.httpx_client import AsyncOAuth2Client

from common.auth.base_token_fetcher import BaseTokenFetcher
from common.performance.cache import get_cache_manager
# Removed metrics dependency for simplicity

logger = logging.getLogger(__name__)


class AsyncTokenFetcher(BaseTokenFetcher):
    def __init__(self, client_id, client_secret, token_url, scope=None):
        super().__init__()
        self._client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope
        )
        self._token_url = token_url
        self._lock = asyncio.Lock()
        self._cache = get_cache_manager()
        self._cache_key = f"auth_token:{client_id}"

    # Removed timed_operation decorator for simplicity
    async def get_token(self) -> str:
        async with self._lock:
            # Try cache first
            cached_token = await self._cache.get(self._cache_key)
            if cached_token and not self.is_token_stale():
                logger.debug("Retrieved token from cache")
                return cached_token

            # Fetch new token if stale or not cached
            if self.is_token_stale():
                try:
                    logger.debug("Fetching new token from OAuth server")
                    token = await self._client.fetch_token(url=self._token_url)
                    self._update_token(token)

                    # Cache the token with TTL slightly less than expiry
                    cache_ttl = max(300, self._expires_in - 60)  # At least 5 minutes, but 1 minute before expiry
                    await self._cache.set(self._cache_key, self._access_token, ttl=cache_ttl)

                    logger.info(f"Successfully fetched and cached new token (expires in {self._expires_in}s)")

                except Exception as e:
                    logger.error(f"Failed to fetch token: {e}")
                    raise

            return self._access_token

    def invalidate_tokens(self):
        """Invalidate cached tokens."""
        super().invalidate_tokens()
        # Clear from cache - handle both sync and async contexts
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._cache.delete(self._cache_key))
        except RuntimeError:
            # No running event loop, clear cache synchronously
            self._cache.delete(self._cache_key)
        logger.debug("Invalidated cached tokens")
