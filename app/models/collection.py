from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        unique=True,
        nullable=False,
    )

    products = relationship(
        "Product",
        secondary="product_collections",
        back_populates="collections",
    )
