from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class LandingPage(Base):
    __tablename__ = "landing_pages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    slug = Column(
        String,
        unique=True,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
        default="",
    )

    brand = Column(
        String,
        nullable=False,
        default="",
    )

    header_colors = Column(
        JSONB,
        nullable=False,
        default={},
    )

    sections = Column(
        JSONB,
        nullable=False,
        default=[],
    )

    product = relationship(
        "Product",
    )
