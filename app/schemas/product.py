from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image: str | None = None

    model_config = {
        "from_attributes": True
    }