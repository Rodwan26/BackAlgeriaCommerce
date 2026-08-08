from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

class CategoryUpdate(BaseModel):
    name: str    

    model_config = {
        "from_attributes": True
    }