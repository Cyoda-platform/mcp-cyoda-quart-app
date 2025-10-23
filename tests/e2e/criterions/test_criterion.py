from common.processor.base import CyodaCriteriaChecker
from common.entity.cyoda_entity import CyodaEntity
from typing import Any


class TestEntityCriterion(CyodaCriteriaChecker):

    is_triggered = False

    def __init__(self) -> None:
        super().__init__(
            name="test-criterion",
            description="test criterion"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        print("!!!!!!!!!!!!!CRITERION!!!!!!!!!")
        self.is_triggered = True
        return True

    def clear(self):
        self.is_triggered = False
