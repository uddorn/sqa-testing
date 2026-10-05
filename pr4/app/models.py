from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Статуси зі Step 2 завдання
OrderStatus = Literal["на обробці", "відправлено", "виконано"]


class BookCreate(BaseModel):
    isbn: str = Field(min_length=1)
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description: str = ""


class Book(BookCreate):
    pass


class BookUpdate(BaseModel):
    """Поля, які можна змінювати. Будь-яке інше поле (зокрема isbn) дає 422."""

    model_config = ConfigDict(extra="forbid")

    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    description: str | None = None


class OrderItem(BaseModel):
    isbn: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItem] = Field(min_length=1)


class Order(BaseModel):
    id: int
    customer_id: int
    items: list[OrderItem]
    status: OrderStatus


class OrderStatusUpdate(BaseModel):
    status: OrderStatus