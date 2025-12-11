from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional
from datetime import datetime

class DishBase(BaseModel):
    name: str
    description: str | None # or Optional[str]=None
    price: float

class DishCreate(DishBase):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt = 0)
    description: str | None = Field(default = None, max_length=300)

class DishResponse(DishBase):
    id: int
    category_id: int

    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class DishUpdate(BaseModel):
    name: str | None
    description: str | None
    price: float | None
    is_active: bool | None



class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    dishes: List[DishResponse] = []

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str = Field(min_length=5, max_length=70)

    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    status: str
    created_at: datetime | None
    items: List[OrderItemResponse]
    total_price: float
    model_config = ConfigDict(from_attributes=True)