from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CarrierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    nameAr: str = Field(validation_alias="name_ar")
    logoUrl: Optional[str] = Field(
        validation_alias="logo_url",
        default=None,
    )
    dashboardUrl: Optional[str] = Field(
        validation_alias="dashboard_url",
        default=None,
    )
    credentialSchema: list = Field(
        validation_alias="credential_schema",
    )
    sortedOrder: int = Field(
        validation_alias="sorted_order",
    )


class ConnectionResponse(BaseModel):
    id: str
    carrierId: str
    status: str
    lastErrorCode: Optional[str] = None
    credentialKeys: list[str]


class ConnectionCreate(BaseModel):
    carrierId: str
    credentials: dict[str, str]


class ConnectionPatch(BaseModel):
    credentials: dict[str, str]
