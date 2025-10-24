from common.processor.base import CyodaCriteriaChecker
from common.entity.cyoda_entity import CyodaEntity
from typing import Any


class TestEntityCriterionFalse(CyodaCriteriaChecker):

    is_triggered = False

    def __init__(self) -> None:
        super().__init__(
            name="test-criterion-false",
            description="always False test criterion"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        print("!!!!!! CHECK !!!!!!!!!!!!")
        self.is_triggered = True
        return False

    def clear(self):
        self.is_triggered = False
