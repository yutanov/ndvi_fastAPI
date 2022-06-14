from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app import config
import aiofiles
from app.database.database import get_session
from app.database.models.zone import Zone, ZoneGet, ZoneUpdate
from app.database.repositories.zones_repository import ZonesRepository
from app.responses import Message

router = APIRouter(
    prefix="/zones/geoJson",
    tags=["GeoJson"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{zone_id}", response_model=ZoneGet, responses={'404': {'model': Message}})
async def upload_geoJson(zone_id: int, file: UploadFile, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zone: Optional[Zone] = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    async with aiofiles.open(config.geojson_uploads_path + f"{db_zone.id}.geojson", 'wb') as src:
        content = await file.read()
        await src.write(content)

    zone_update = ZoneUpdate()
    zone_update.geoJsonFilename = f"{db_zone.id}.geojson"

    db_zone = zones_repository.update(db_zone, zone_update)

    await zones_repository.commit()
    await zones_repository.refresh(db_zone)

    return db_zone


@router.get("/{zone_id}", response_class=FileResponse, responses={'404': {'model': Message}})
async def get_getJson(zone_id: int, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)

    db_zone: Optional[Zone] = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    if db_zone.geoJsonFilename is None or len(db_zone.geoJsonFilename) == 0:
        return JSONResponse(status_code=404, content={'message': f"GeoJson file not found"})

    return FileResponse(config.geojson_uploads_path + db_zone.geoJsonFilename)
