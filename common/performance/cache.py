"""
Simple cache manager stub.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SimpleCacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()


# Global cache manager instance
_cache_manager = SimpleCacheManager()


def get_cache_manager() -> SimpleCacheManager:
    """Get the global cache manager instance."""
    return _cache_manager
