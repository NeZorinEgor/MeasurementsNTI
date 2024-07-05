import asyncio
import datetime
from select import select
from typing import List

from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import event, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.fc28.models import FC28Model
from src.fc28.shemas import PostFC28

router = APIRouter(
    prefix="/v1/FC28",
    tags=["FC28 Module"],
)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def save_fc28(
        fc28_schema: PostFC28,
        session: AsyncSession = Depends(get_session)
):
    """ Save FC28 measurements, return id """
    fc28_model = FC28Model(
        soil_moisture=fc28_schema.soil_moisture,
        register_at=datetime.datetime.now(datetime.UTC)
    )
    session.add(fc28_model)
    await session.commit()
    return {
        "ok": True,
        "id": fc28_model.id,
        "message": "successful save soil moisture"
    }


@router.get("/fc28_data")
@cache(expire=15)
async def get_fc28_data(
    from_date: str = Query(..., description="Start date (inclusive), format: YYYY-MM-DD HH:MM:SS"),
    to_date: str = Query(..., description="End date (inclusive), format: YYYY-MM-DD HH:MM:SS"),
    session: AsyncSession = Depends(get_session)
):
    """ Retrieve FC28 data within specified date range """
    from_date_obj = datetime.datetime.fromisoformat(from_date)
    to_date_obj = datetime.datetime.fromisoformat(to_date)

    query_stmt = text(
        """SELECT soil_moisture, register_at
                           FROM FC28
                           WHERE register_at >= :from_date AND register_at <= :to_date
                           ORDER BY register_at"""
    )
    res = await session.execute(query_stmt, {"from_date": from_date_obj, "to_date": to_date_obj})
    return [{"soil_moisture": i.soil_moisture, "register_at": i.register_at} for i in res]


@router.websocket("/ws")
async def stream_fc28_values(
        websocket: WebSocket,
        session: AsyncSession = Depends(get_session),
):
    flag = asyncio.Event()

    @event.listens_for(FC28Model, "after_insert")
    def inner_stream(*args, **kwargs):
        flag.set()

    await websocket.accept()

    async def fetch_data():
        async with session.begin():
            result = await session.execute(text(
                """SELECT soil_moisture, register_at 
                FROM FC28 
                ORDER BY register_at 
                DESC LIMIT 30;"""
            ))
            rows = result.fetchall()
            return [{"soil_moisture": row.soil_moisture, "register_at": row.register_at.isoformat()} for row in rows]

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
