from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ResponseSpec:
    response_type: str
    data: dict
    source_event_id: Optional[str] = None
    success: bool = True

