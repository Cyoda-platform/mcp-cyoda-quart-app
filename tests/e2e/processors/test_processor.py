from common.processor.base import CyodaEntity, CyodaProcessor
from typing import Any, Dict


class ExampleEntityProcessor(CyodaProcessor):

    is_triggered = False

    def __init__(self) -> None:
        super().__init__(
            name="test-processor-1",
            description="test processor"
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        self.is_triggered = True
        return entity

    def clear(self):
        self.is_triggered = False
