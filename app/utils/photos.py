import zipfile

from sentinelsat import geojson_to_wkt, read_geojson

from app import config


def save_space_photo(sentinel_api, db_zone):
    wkt = geojson_to_wkt(read_geojson(config.geojson_uploads_path + db_zone.geoJsonFilename))
    products = sentinel_api.query(
        wkt,
        limit=1,
        platformname='Sentinel-2',
        cloudcoverpercentage=(0, 30)
    )
    product_id = list(products.keys())[0]
    sentinel_api.download(product_id, config.photos_uploads_path)

    return product_id
