from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProductOption(Base):
    __tablename__ = "product_options"

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

    values = Column(
        JSONB,
        nullable=True,
    )

    product = relationship(
        "Product",
        back_populates="options",
    )
