import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sentinelsat import SentinelAPI
from app.utils import photos

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app import config
from app.database.database import get_session
from app.database.models.zone import ZoneGet
from app.database.repositories.zones_repository import ZonesRepository
from app.responses import Message

router = APIRouter(
    prefix="/zones/photos",
    tags=["Photos"],
    responses={404: {"description": "Not found"}},
)

sentinel_api = SentinelAPI(config.sentinel_user, config.sentinel_password, config.sentinel_url)


@router.get("/{zone_id}", response_class=FileResponse, responses={'404': {'model': Message}})
async def get_zone_photo(zone_id: int, session: AsyncSession = Depends(get_session)):
    zones_repository = ZonesRepository(session)
    db_zone = await zones_repository.get_by_id(zone_id)
    if db_zone is None:
        return JSONResponse(status_code=404, content={'message': f"[ID:{zone_id}] Zone not found"})

    product_id = photos.save_space_photo(sentinel_api, db_zone)
    filename = None
    with zipfile.ZipFile(config.photos_uploads_path + product_id + ".zip", 'r') as zip_ref:
        zip_ref.extractall(config.photos_uploads_path)
        filename = zip_ref.namelist()[0]

    return FileResponse(config.geojson_uploads_path + filename)
