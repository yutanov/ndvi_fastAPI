from fastapi import APIRouter
from app.endpoints import zones, zones_geoJson, zones_photos, zones_ndvi

router = APIRouter()
router.include_router(zones.router)
router.include_router(zones_geoJson.router)
router.include_router(zones_ndvi.router)
router.include_router(zones_photos.router)