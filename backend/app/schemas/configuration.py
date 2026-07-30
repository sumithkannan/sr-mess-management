from pydantic import BaseModel
from typing import Any, Optional

class ConfigUpdate(BaseModel):
    key: str
    value: Any

class ConfigResponse(BaseModel):
    id: int
    key: str
    value: Any
    class Config:
        from_attributes = True
