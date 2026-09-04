from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # --------------------------------------------------
    # Customer relationship
    # --------------------------------------------------

    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )

    customer = relationship(
        "Customer",
        back_populates="orders",
    )

    # --------------------------------------------------
    # Legacy customer information
    # Kept temporarily for existing orders
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Delivery
    # --------------------------------------------------

    delivery_type = Column(
        String(30),
        nullable=True,
    )

    # --------------------------------------------------
    # Landing page source
    # Orders created from a landing page keep a link
    # to the page that produced them (NULL otherwise).
    # --------------------------------------------------

    landing_page_id = Column(
        Integer,
        ForeignKey("landing_pages.id", ondelete="SET NULL"),
        nullable=True,
    )

    # --------------------------------------------------
    # Order information
    # --------------------------------------------------

    total = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
    )

    # --------------------------------------------------
    # Order items
    # --------------------------------------------------

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )