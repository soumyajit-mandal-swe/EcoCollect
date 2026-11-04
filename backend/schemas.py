from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid', allow_inf_nan=False)
class Register(Input):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
class ItemInput(Input):
    category_id: int = Field(gt=0)
    condition: Literal['Working','Damaged','Non-functional']
    quantity: int = Field(gt=0, le=1000)
    estimated_weight: Decimal = Field(gt=0, le=999999, decimal_places=2)
class RequestInput(Input):
    address: str = Field(min_length=10, max_length=500)
    items: list[ItemInput] = Field(min_length=1, max_length=30)
class Weight(Input):
    item_id: int
    actual_weight: Decimal = Field(gt=0, le=999999, decimal_places=2)
class WorkflowInput(Input):
    status: Literal['Scheduled','Collected','Recycled']
    centre_id: int | None = None
    pickup_date: date | None = None
    weights: list[Weight] = Field(default_factory=list, max_length=30)
    note: str = Field(default='', max_length=500)
class CentreInput(Input):
    name: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=10, max_length=500)
    phone: str = Field(min_length=6, max_length=30)
    active: bool = True
