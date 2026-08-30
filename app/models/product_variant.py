from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    sku = Column(
        String,
        nullable=True,
    )

    price = Column(
        Float,
        nullable=True,
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0,
    )

    image = Column(
        String,
        nullable=True,
    )

    options = Column(
        JSONB,
        nullable=True,
    )

    product = relationship(
        "Product",
        back_populates="variants",
    )
