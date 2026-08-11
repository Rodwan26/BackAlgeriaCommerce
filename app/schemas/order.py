from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int
    delivery_type: str
    items: list[OrderItemCreate]


class OrderItemProduct(BaseModel):
    id: int
    name: str
    price: float

    model_config = {
        "from_attributes": True,
    }


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: OrderItemProduct

    model_config = {
        "from_attributes": True,
    }


class OrderResponse(BaseModel):
    id: int
    customer_id: int | None
    delivery_type: str | None
    total: float
    status: str
    items: list[OrderItemResponse]

    model_config = {
        "from_attributes": True,
    }