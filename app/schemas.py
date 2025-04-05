from typing import Any, Optional
from pydantic import BaseModel, PositiveInt


class Intake(BaseModel):
    value: Any
    ttl: Optional[PositiveInt] = None
