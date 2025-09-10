import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTokenFetcher(ABC):
    def __init__(self) -> None:
        self._access_token: Optional[str] = None
        self._access_token_expiry: Optional[float] = None

    def is_token_stale(self) -> bool:
        return (
            not self._access_token
            or not self._access_token_expiry
            or time.time() >= self._access_token_expiry - 60
        )

    def invalidate_tokens(self) -> None:
        self._access_token = None
        self._access_token_expiry = None

    def _update_token(self, token: Dict[str, Any]) -> None:
        self._access_token = token.get("access_token")
        self._access_token_expiry = time.time() + float(token.get("expires_in", 300))

    @abstractmethod
    def get_token(self) -> str:
        pass
