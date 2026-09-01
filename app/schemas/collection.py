from pydantic import BaseModel


class CollectionCreate(BaseModel):
    name: str


class CollectionUpdate(BaseModel):
    name: str


class CollectionResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }
