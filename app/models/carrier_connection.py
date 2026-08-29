from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class CarrierConnection(Base):
    __tablename__ = "carrier_connections"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    carrier_id = Column(
        String,
        ForeignKey("carriers.id"),
        nullable=False,
    )

    # NOTE: No Authentication/Merchant exists yet. This column is a
    # placeholder only and is not used in any logic currently.
    merchant_id = Column(
        Integer,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="connected",
    )

    credentials_encrypted = Column(
        LargeBinary,
        nullable=False,
    )

    last_error_code = Column(
        String(120),
        nullable=True,
    )

    carrier = relationship(
        "Carrier",
        back_populates="connections",
    )
