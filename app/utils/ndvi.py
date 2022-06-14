import rasterio
import numpy

from app import config


async def extract_band_red(src):
    return await src.read(3)


async def extract_band_nir(src):
    return await src.read(4)


def calculate_ndvi(band_nir, band_red):
    numpy.seterr(divide='ignore', invalid='ignore')
    return (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)


def save_ndvi(src, ndvi, filename):
    kwargs = src.meta
    kwargs.update(
        dtype=rasterio.float32,
        count=1
    )

    with rasterio.open(config.ndvi_uploads_path + f'{filename}.tif', 'w', **kwargs) as dst:
        dst.write_band(1, ndvi.astype(rasterio.float32))

    return f"{filename}.tif"