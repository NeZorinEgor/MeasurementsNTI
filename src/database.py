from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, registry
from sqlalchemy import String
from src.config import settings
from typing import Annotated

# Async engin connector
engine = create_async_engine(
    url=settings.mysql_async_url,
    echo=False,
)

# Factory pattern
session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# global database connector dependency
# sample: session: AsyncSession = Depends(get_session)
async def get_session() -> AsyncSession:
    async with session_factory() as session:
        yield session


# MySQL varchar length
str_50 = Annotated[str, 50]
str_128 = Annotated[str, 128]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str_50: String(50),
            str_128: String(128),
        }
    )
