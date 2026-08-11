from datetime import date

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    date_of_birth: date
    wilaya: str
    commune: str


class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    date_of_birth: date
    wilaya: str
    commune: str

    model_config = {
        "from_attributes": True,
    }