import datetime
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class DHT11Model(Base):
    __tablename__ = "DHT11"

    id: Mapped[int] = mapped_column(primary_key=True)
    temperature: Mapped[float]
    air_humidity: Mapped[float]
    register_at: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.now(datetime.UTC))
