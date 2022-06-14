import zipfile

import aiofiles
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sentinelsat import SentinelAPI

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app import config
from app.database.database import get_session
from app.database.models.zone import ZoneGet, ZoneUpdate
from app.database.repositories.zones_repository import ZonesRepository
from app.responses import Message
from app.utils import photos, ndvi

router = APIRouter(
    prefix="/zones/ndvi",
    tags=["NDVI"],
    responses={404: {"description": "Not found"}},
)

sentinel_api = SentinelAPI(config.sentinel_user, config.sentinel_password, config.sentinel_url)


@router.get("/{zone_id}", response_model=ZoneGet, responses={'404': {'model': Message}})
async def get_ndvi(zone_id: int, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)
    db_zone = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    product_id = photos.save_space_photo(sentinel_api, db_zone)
    filename = None
    with zipfile.ZipFile(config.photos_uploads_path + product_id + ".zip", 'r') as zip_ref:
        zip_ref.extractall(config.photos_uploads_path)
        filename = zip_ref.namelist()[0]

    async with aiofiles.open(config.geojson_uploads_path + f"{filename}", 'rb') as src:
        band_nir = await ndvi.extract_band_nir(src)
        band_red = await ndvi.extract_band_red(src)
        file_ndvi = ndvi.calculate_ndvi(band_nir, band_red)
        filename = ndvi.save_ndvi(src, file_ndvi, db_zone.id)

        zone_update = ZoneUpdate()
        zone_update.ndviFilename = filename

        zones_repository.update(db_zone, zone_update)

    await zones_repository.commit()
    await zones_repository.refresh(db_zone)

    return FileResponse(config.ndvi_uploads_path + db_zone.ndviFilename)
