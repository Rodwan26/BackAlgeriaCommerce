from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str | None = None
    category_id: int | None = None


class CategoryInfo(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image: str | None = None
    category_id: int | None = None
    category: CategoryInfo | None = None

    model_config = {
        "from_attributes": True
    }