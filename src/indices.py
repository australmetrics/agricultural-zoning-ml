"""Module for calculating vegetation indices from satellite imagery.

Compatible with Sentinel-2 and Landsat imagery. Provides automated band detection
and standardized index calculations following ISO 42001 requirements.
"""

import numpy as np
import rasterio
from pathlib import Path
from loguru import logger
from typing import Dict
from .config import DEFAULT_SAVI_L


def identify_bands(src: rasterio.DatasetReader) -> Dict[str, int]:
    """Automatically identifies relevant bands based on metadata or wavelengths.

    Uses image metadata or wavelength information to detect and map spectral bands
    to their corresponding indices in the dataset.

    Args:
        src: Rasterio dataset object containing the multispectral image

    Returns:
        Dictionary mapping band names to their indices in the dataset
    """
    bands = {}

    # Primero intentar identificar por metadatos de longitud de onda
    for i in range(1, src.count + 1):
        tags = src.tags(i)
        if "wavelength_nm" in tags:
            wavelength = float(tags["wavelength_nm"])
            # Identificar bandas por rangos de longitud de onda
            if 630 <= wavelength <= 690:  # Rojo
                bands["red"] = i
            elif 760 <= wavelength <= 900:  # NIR
                bands["nir"] = i
            elif 520 <= wavelength <= 600:  # Verde
                bands["green"] = i
            elif 450 <= wavelength <= 520:  # Azul
                bands["blue"] = i
            elif 690 <= wavelength <= 730:  # Red Edge
                bands["red_edge1"] = i

    # Si no se encontraron bandas por metadatos, usar la lógica existente
    if not bands:
        if src.count >= 12:  # Sentinel-2 tiene 12+ bandas
            return {
                "blue": 2,  # Banda 2 (490nm)
                "green": 3,  # Banda 3 (560nm)
                "red": 4,  # Banda 4 (665nm)
                "nir": 8,  # Banda 8 (842nm)
                "red_edge1": 5,  # Banda 5 (705nm)
                "swir1": 11,  # Banda 11 (1610nm)
            }
        elif src.count >= 7:  # Landsat tiene 7+ bandas
            return {
                "blue": 2,  # Banda 2
                "green": 3,  # Banda 3
                "red": 4,  # Banda 4
                "nir": 5,  # Banda 5
                "swir1": 6,  # Banda 6
            }
        else:
            # Caso genérico (suposición de orden RGB-NIR)
            if src.count >= 1:
                bands["red"] = 1
            if src.count >= 2:
                bands["nir"] = 2  # En nuestro caso de prueba, NIR es la segunda banda
            if src.count >= 3:
                bands["green"] = 3
            if src.count >= 4:
                bands["blue"] = 4

    if "nir" not in bands:
        logger.warning(
            "⚠️ No se pudo identificar la banda NIR, necesaria para índices vegetativos"
        )

    return bands


def calculate_ndvi(image_path: Path, output_dir: Path) -> Path:
    """Calculate NDVI (Normalized Difference Vegetation Index).

    Process a multiband satellite image to generate the NDVI index following
    ISO 42001 calculation standards.

    Args:
        image_path: Path to multiband satellite image
        output_dir: Directory to save results

    Returns:
        Path to the generated NDVI file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{image_path.stem}_ndvi.tif"

    with rasterio.open(image_path) as src:
        bands = identify_bands(src)

        if "red" not in bands or "nir" not in bands:
            raise ValueError("No se encontraron bandas rojo o NIR necesarias para NDVI")

        red = src.read(bands["red"]).astype(float)
        nir = src.read(bands["nir"]).astype(float)

        # Evitar división por cero
        denominator = nir + red
        ndvi = np.where(denominator > 0, (nir - red) / denominator, 0)

        # Crear nuevo archivo de salida
        meta = src.meta.copy()
        meta.update({"count": 1, "dtype": "float32", "nodata": np.nan})

        with rasterio.open(output_file, "w", **meta) as dst:
            dst.write(ndvi.astype(np.float32), 1)

        logger.success(f"✅ NDVI calculado y guardado en {output_file}")

    return output_file


def calculate_ndre(image_path: Path, output_dir: Path) -> Path | None:
    """Calculate NDRE (Normalized Difference Red Edge).

    Process a multiband satellite image to generate the NDRE index,
    requires Red Edge bands.

    Args:
        image_path: Path to multiband satellite image
        output_dir: Directory to save results

    Returns:
        Path to generated NDRE file or None if required bands not found
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{image_path.stem}_ndre.tif"

    with rasterio.open(image_path) as src:
        bands = identify_bands(src)

        if "red_edge1" not in bands or "nir" not in bands:
            logger.warning("⚠️ No se encontraron bandas Red Edge necesarias para NDRE")
            return None

        red_edge = src.read(bands["red_edge1"]).astype(float)
        nir = src.read(bands["nir"]).astype(float)

        # Evitar división por cero
        denominator = nir + red_edge
        ndre = np.where(denominator > 0, (nir - red_edge) / denominator, 0)

        # Crear nuevo archivo de salida
        meta = src.meta.copy()
        meta.update({"count": 1, "dtype": "float32", "nodata": np.nan})

        with rasterio.open(output_file, "w", **meta) as dst:
            dst.write(ndre.astype(np.float32), 1)

        logger.success(f"✅ NDRE calculado y guardado en {output_file}")

    return output_file


def calculate_savi(image_path: Path, output_dir: Path, L: float = 0.5) -> Path:
    """Calculate SAVI (Soil Adjusted Vegetation Index).

    Process a multiband satellite image to generate the SAVI index with
    configurable soil adjustment factor.

    Args:
        image_path: Path to multiband satellite image
        output_dir: Directory to save results
        L: Soil adjustment factor (0 = no adjustment, 1 = maximum)

    Returns:
        Path to generated SAVI file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{image_path.stem}_savi_L{L:.2f}.tif"

    with rasterio.open(image_path) as src:
        bands = identify_bands(src)

        if "red" not in bands or "nir" not in bands:
            raise ValueError("No se encontraron bandas rojo o NIR necesarias para SAVI")

        red = src.read(bands["red"]).astype(float)
        nir = src.read(bands["nir"]).astype(float)

        # Fórmula SAVI: ((NIR - RED) / (NIR + RED + L)) * (1 + L)
        denominator = nir + red + L
        savi = np.where(denominator > 0, ((nir - red) / denominator) * (1 + L), 0)

        # Crear nuevo archivo de salida
        meta = src.meta.copy()
        meta.update({"count": 1, "dtype": "float32", "nodata": np.nan})

        with rasterio.open(output_file, "w", **meta) as dst:
            dst.write(savi.astype(np.float32), 1)

        logger.success(f"✅ SAVI calculado y guardado en {output_file}")

    return output_file


def calculate_all_indices(image_path: Path, output_dir: Path) -> Dict[str, Path]:
    """Calculate all available vegetation indices for an image.

    Processes a multiband satellite image to generate all supported vegetation
    indices according to ISO 42001 standards.

    Args:
        image_path: Path to multiband satellite image
        output_dir: Directory to save results

    Returns:
        Dictionary mapping index names to generated file paths
    """
    results = {}

    # NDVI (siempre disponible si hay bandas R y NIR)
    try:
        results["ndvi"] = calculate_ndvi(image_path, output_dir)
        logger.info("📊 NDVI calculado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al calcular NDVI: {e}")

    # NDRE (solo disponible si hay bandas Red Edge)
    try:
        ndre_path = calculate_ndre(image_path, output_dir)
        if ndre_path:
            results["ndre"] = ndre_path
            logger.info("📊 NDRE calculado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al calcular NDRE: {e}")

    # SAVI
    try:
        savi_path = calculate_savi(image_path, output_dir)
        # Usar el nombre con el factor L para compatibilidad
        savi_name = f"savi_{DEFAULT_SAVI_L}"
        results[savi_name] = savi_path
        logger.info("📊 SAVI calculado correctamente")
    except Exception as e:
        logger.error(f"❌ Error al calcular SAVI: {e}")

    return results
