from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(
        String,
        primary_key=True,
    )

    name = Column(
        String(120),
        nullable=False,
    )

    name_ar = Column(
        String(120),
        nullable=False,
    )

    logo_url = Column(
        String,
        nullable=True,
    )

    dashboard_url = Column(
        String,
        nullable=True,
    )

    credential_schema = Column(
        JSONB,
        nullable=False,
    )

    sorted_order = Column(
        Integer,
        nullable=False,
        default=0,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    connections = relationship(
        "CarrierConnection",
        back_populates="carrier",
    )
