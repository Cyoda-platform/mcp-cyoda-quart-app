from typing import Any

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker


class TestEntityCriterionFalse(CyodaCriteriaChecker):

    is_triggered = False

    def __init__(self) -> None:
        super().__init__(
            name="test-criterion-false", description="always False test criterion"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        print("!!!!!! CHECK !!!!!!!!!!!!")
        self.is_triggered = True
        return False

    def clear(self):
        self.is_triggered = False
