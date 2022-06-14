from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.zone import Zone, ZoneGet, ZoneCreate, ZoneUpdate
from app.database.repositories.zones_repository import ZonesRepository
from app.responses import Message

router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ZoneGet], responses={'404': {'model': Message}})
async def get_zones(
        search: Optional[str] = None,
        session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zones = await zones_repository.get_all(search)
    return db_zones


@router.get("/{zone_id}", response_model=ZoneGet, responses={'404': {'model': Message}})
async def get_zone(zone_id: int, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)
    db_zone = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    return db_zone


@router.post("/", response_model=ZoneGet, responses={'404': {'model': Message}})
async def add_zone(zone_create: ZoneCreate, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zone = zones_repository.create(zone_create)

    await zones_repository.commit()
    await zones_repository.refresh(db_zone)

    return db_zone


@router.put("/{zone_id}", response_model=ZoneGet, responses={'404': {'model': Message}})
async def update_zone(zone_id: int, zone_update: ZoneUpdate, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zone: Optional[Zone] = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    db_zone = zones_repository.update(db_zone, zone_update)

    await zones_repository.commit()
    await zones_repository.refresh(db_zone)

    return db_zone


@router.delete("/{zone_id}", responses={'404': {'model': Message}, '200': {'model': Message}})
async def delete_zone(zone_id: int, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zone: Optional[Zone] = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{db_zone}] Zone not found"})

    await zones_repository.delete(db_zone)
    await zones_repository.commit()

    return JSONResponse(status_code=200, content={'message': f'[ID:{zone_id}] Zone deleted successfully'})
