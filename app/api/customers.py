from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
)


router = APIRouter()


@router.post(
    "/customers",
    response_model=CustomerResponse,
)
def create_customer(data: CustomerCreate):

    db: Session = SessionLocal()

    try:

        # ---------------------------------------------
        # Check if customer already exists
        # ---------------------------------------------

        customer = (
            db.query(Customer)
            .filter(Customer.phone == data.phone)
            .first()
        )

        if customer:
            return customer

        # ---------------------------------------------
        # Create new customer
        # ---------------------------------------------

        customer = Customer(
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            wilaya=data.wilaya,
            commune=data.commune,
        )

        db.add(customer)

        db.commit()

        db.refresh(customer)

        return customer

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()