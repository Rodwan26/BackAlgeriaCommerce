from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class LandingPageCreate(BaseModel):
    product_id: Optional[int] = None
    slug: str
    title: str = ""
    brand: str = ""
    header_colors: dict[str, Any] = {}
    sections: list[Any] = []


class LandingPageUpdate(BaseModel):
    product_id: Optional[int] = None
    slug: str
    title: str = ""
    brand: str = ""
    header_colors: dict[str, Any] = {}
    sections: list[Any] = []


class LandingPageProduct(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LandingPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int] = None
    product: Optional[LandingPageProduct] = None
    slug: str
    title: str
    brand: str
    header_colors: dict[str, Any]
    sections: list[Any]
