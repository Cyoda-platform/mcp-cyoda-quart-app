import asyncio
import threading
from concurrent import futures
from typing import Any, Coroutine


class BackgroundEventLoop:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _start_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coroutine(self, coro: Coroutine[Any, Any, Any]) -> futures.Future[Any]:
        # Submit coroutine to background loop
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
