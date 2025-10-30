from typing import Optional

from common.auth.async_token_fetcher import AsyncTokenFetcher
from common.auth.sync_token_fetcher import SyncTokenFetcher


class CyodaAuthService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        skip_ssl: bool,
        scope: Optional[str] = None,
    ):
        self._sync = SyncTokenFetcher(
            client_id, client_secret, token_url, skip_ssl, scope
        )
        self._async = AsyncTokenFetcher(
            client_id, client_secret, token_url, skip_ssl, scope
        )

    def get_access_token_sync(self) -> str:
        return self._sync.get_token()

    async def get_access_token(self) -> str:
        return await self._async.get_token()

    def invalidate_tokens(self) -> None:
        self._sync.invalidate_tokens()
        self._async.invalidate_tokens()
