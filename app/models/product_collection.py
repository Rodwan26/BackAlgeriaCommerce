from sqlalchemy import Table, Column, Integer, ForeignKey

from app.db.database import Base


product_collections = Table(
    "product_collections",
    Base.metadata,
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "collection_id",
        Integer,
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
