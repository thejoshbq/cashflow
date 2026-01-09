# schemas.py

from pydantic import BaseModel
from typing import Optional


class StartRequest(BaseModel):
    income: float

class NodeRequest(BaseModel):
    parent_label: str
    label: str
    amount: float
    group: str
    apr: float = 0.0
    current_balance: float = 0.0

class EditNodeRequest(BaseModel):
    new_label: Optional[str] = None
    new_amount: Optional[float] = None
    new_group: Optional[str] = None
    apr: Optional[float] = None
    current_balance: Optional[float] = None

class AssetRequest(BaseModel):
    name: str
    value: float