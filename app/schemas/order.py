from typing import Optional

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int
    delivery_type: str
    items: list[OrderItemCreate]


class OrderFromLandingCreate(BaseModel):
    # The landing page is located by its slug; its linked product
    # and stored price/delivery settings drive the order totals.
    slug: str
    name: str
    phone: str
    wilaya: str
    commune: str
    address: Optional[str] = None
    delivery_type: str
    quantity: int = 1


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
    customer_name: str
    customer_phone: str
    customer_address: str
    delivery_type: str | None
    landing_page_id: int | None
    total: float
    status: str
    items: list[OrderItemResponse]

    model_config = {
        "from_attributes": True,
    }