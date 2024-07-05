import datetime

from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class FC28Model(Base):
    __tablename__ = "FC28"

    id: Mapped[int] = mapped_column(primary_key=True)
    soil_moisture: Mapped[float]
    register_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.now(datetime.UTC))
