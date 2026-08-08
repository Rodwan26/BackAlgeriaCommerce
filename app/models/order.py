from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    customer_name = Column(
        String(120),
        nullable=False,
    )

    customer_phone = Column(
        String(30),
        nullable=False,
    )

    customer_address = Column(
        String(255),
        nullable=False,
    )

    total = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

