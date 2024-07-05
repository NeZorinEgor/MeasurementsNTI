import asyncio
import datetime

from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect, Query
from fastapi_cache.decorator import cache
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.dht11.models import DHT11Model
from src.dht11.shemas import PostDHT11

router = APIRouter(
    prefix="/v1/DHT11",
    tags=["DHT11 Module"],
)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def save_dht11(
        dht11_schema: PostDHT11,
        session: AsyncSession = Depends(get_session)
):
    """ Save DHT11 measurements, return id """
    dht11_model = DHT11Model(
        temperature=dht11_schema.temperature,
        air_humidity=dht11_schema.air_humidity,
        register_at=datetime.datetime.now(datetime.UTC)
    )
    session.add(dht11_model)
    await session.commit()
    return {
        "ok": True,
        "id": dht11_model.id,
        "message": "successful save temperature and air humidity"
    }


@router.get("/dht11_data")
@cache(expire=15)
async def get_dht11_data(
    from_date: str = Query(..., description="Start date (inclusive), format: YYYY-MM-DD HH:MM:SS"),
    to_date: str = Query(..., description="End date (inclusive), format: YYYY-MM-DD HH:MM:SS"),
    session: AsyncSession = Depends(get_session)
):
    """ Retrieve DHT11 data within specified date range """
    from_date_obj = datetime.datetime.fromisoformat(from_date)
    to_date_obj = datetime.datetime.fromisoformat(to_date)

    query_stmt = text(
        """SELECT temperature, air_humidity, register_at
                           FROM DHT11
                           WHERE register_at >= :from_date AND register_at <= :to_date
                           ORDER BY register_at"""
    )
    res = await session.execute(query_stmt, {"from_date": from_date_obj, "to_date": to_date_obj})
    return [{"temperature": i.temperature, "air_humidity": i.air_humidity, "register_at": i.register_at} for i in res]


@router.websocket("/ws")
async def stream_fc28_values(
        websocket: WebSocket,
        session: AsyncSession = Depends(get_session),
):
    flag = asyncio.Event()

    @event.listens_for(DHT11Model, "after_insert")
    def inner_stream(*args, **kwargs):
        flag.set()

    await websocket.accept()

    async def fetch_data():
        async with session.begin():
            result = await session.execute(text(
                """SELECT temperature, air_humidity, register_at 
                FROM DHT11
                ORDER BY register_at 
                DESC LIMIT 30; """
            ))
            rows = result.fetchall()
            return [{"temperature": row.temperature, "air_humidity": row.air_humidity, "register_at": row.register_at.isoformat()} for row in rows]

    # Initial data send
    data = await fetch_data()
    await websocket.send_json(data)

    while True:
        try:
            await flag.wait()
            data = await fetch_data()
            await websocket.send_json(data)
            flag.clear()
        except WebSocketDisconnect as e:
            print(f"WebSocket disconnected: {e}")
            break
