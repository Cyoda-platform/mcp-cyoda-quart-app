from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ResponseSpec:
    response_type: str
    data: Dict[str, Any]
    source_event_id: Optional[str] = None
    success: bool = True
