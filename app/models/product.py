from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=False,
    )

    price = Column(
        Float,
        nullable=False,
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

    status = Column(
        String,
        nullable=False,
        default="draft",
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )

    options = relationship(
        "ProductOption",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    tags = relationship(
        "ProductTag",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    collections = relationship(
        "Collection",
        secondary="product_collections",
    )

