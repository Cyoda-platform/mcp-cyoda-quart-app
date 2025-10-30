from typing import Any

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker


class TestEntityCriterionTrue(CyodaCriteriaChecker):

    is_triggered = False

    def __init__(self) -> None:
        super().__init__(
            name="test-criterion-true", description="always True test criterion"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        self.is_triggered = True
        return True

    def clear(self):
        self.is_triggered = False
