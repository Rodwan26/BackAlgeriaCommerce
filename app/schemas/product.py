from pydantic import BaseModel


class OptionCreate(BaseModel):
    name: str
    values: list[str] = []


class VariantCreate(BaseModel):
    id: int | None = None
    sku: str | None = None
    price: float | None = None
    stock: int = 0
    image: str | None = None
    options: dict[str, str] = {}


class TagCreate(BaseModel):
    name: str


class OptionOut(BaseModel):
    id: int
    name: str
    values: list[str] | None = None

    model_config = {
        "from_attributes": True
    }


class VariantOut(BaseModel):
    id: int
    sku: str | None = None
    price: float | None = None
    stock: int = 0
    image: str | None = None
    options: dict[str, str] | None = None

    model_config = {
        "from_attributes": True
    }


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class CollectionInfo(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 0
    image: str | None = None
    category_id: int | None = None
    status: str = "draft"
    options: list[OptionCreate] = []
    variants: list[VariantCreate] = []
    tags: list[str] = []
    collections: list[int] = []


class ProductStatusUpdate(BaseModel):
    status: str


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
    stock: int
    image: str | None = None
    status: str = "draft"
    category_id: int | None = None
    category: CategoryInfo | None = None
    options: list[OptionOut] = []
    variants: list[VariantOut] = []
    tags: list[TagOut] = []

    collections: list[CollectionInfo] = []

    model_config = {
        "from_attributes": True
    }
