from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProductTag(Base):
    __tablename__ = "product_tags"

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

    name = Column(
        String,
        nullable=False,
    )

    product = relationship(
        "Product",
        back_populates="tags",
    )
