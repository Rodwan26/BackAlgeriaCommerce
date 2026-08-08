from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    description = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    image = Column(String, nullable=True)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )