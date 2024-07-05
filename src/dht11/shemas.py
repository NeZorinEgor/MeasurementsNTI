from pydantic import BaseModel


class PostDHT11(BaseModel):
    temperature: float
    air_humidity: float
