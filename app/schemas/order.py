from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: str
    items: list[OrderItemCreate]


class OrderItemProduct(BaseModel):
    id: int
    name: str
    price: float

    model_config = {
        "from_attributes": True
    }


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: OrderItemProduct

    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    customer_address: str
    total: float
    status: str
    items: list[OrderItemResponse]

    model_config = {
        "from_attributes": True
    }

