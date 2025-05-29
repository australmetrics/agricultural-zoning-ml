"""Satellite image preprocessing module.

Provides functions for preparing images before index calculation, including
shapefile clipping and data validation according to ISO 42001 standards.
"""

from pathlib import Path
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import mapping
from loguru import logger


def clip_image_with_shapefile(
    image_path: Path, shapefile_path: Path, output_path: Path
) -> Path:
    """Clips a multiband satellite image using a polygon shapefile.

    Takes a raster image and clips it to the extent of the provided shapefile,
    preserving all bands and metadata in the process.

    Args:
        image_path: Path to the .tif file
        shapefile_path: Path to the .shp file
        output_path: Directory to save the result

    Returns:
        Path to the new clipped TIFF file
    """
    logger.info("🧩 Cargando shapefile...")
    gdf = gpd.read_file(shapefile_path)

    logger.info("🌍 Cargando imagen satelital...")
    with rasterio.open(image_path) as src:
        image_crs = src.crs
        if gdf.crs != image_crs:
            logger.warning(f"⚠️ Reproyectando shapefile desde {gdf.crs} a {image_crs}")
            gdf = gdf.to_crs(image_crs)

        geoms = [mapping(geom) for geom in gdf.geometry]
        clipped_image, clipped_transform = mask(src, geoms, crop=True)

        meta = src.meta.copy()
        meta.update(
            {
                "driver": "GTiff",
                "height": clipped_image.shape[1],
                "width": clipped_image.shape[2],
                "transform": clipped_transform,
            }
        )

        output_path.mkdir(parents=True, exist_ok=True)
        out_file = output_path / f"{image_path.stem}_clipped.tif"
        with rasterio.open(out_file, "w", **meta) as dst:
            dst.write(clipped_image)

        logger.success(f"✅ Imagen recortada guardada en {out_file}")

        return out_file
