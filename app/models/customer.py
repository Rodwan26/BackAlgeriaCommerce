from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    phone = Column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    date_of_birth = Column(
        Date,
        nullable=False,
    )

    wilaya = Column(
        String(100),
        nullable=False,
    )

    commune = Column(
        String(100),
        nullable=False,
    )

    orders = relationship(
        "Order",
        back_populates="customer",
    )