"""Integration tests for verifying complete system workflow.

Tests end-to-end functionality following ISO 42001 validation requirements."""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from src.main import process_image
from src.config import DEFAULT_SAVI_L
from src.logging_config import setup_logging


def test_full_workflow(tmp_path: Path) -> None:
    """Tests the complete system workflow with simulated satellite data.

    Verifies image processing, index calculation, and logging functionality
    in an integrated test environment.

    Args:
        tmp_path: Temporary directory provided by pytest
    """
    # Configurar directorios de prueba
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Crear imagen de prueba
    test_image_path = input_dir / "test.tif"
    red_band = np.ones((10, 10), dtype=np.float32) * 0.3  # Simulando reflectancia roja
    nir_band = np.ones((10, 10), dtype=np.float32) * 0.8  # Simulando reflectancia NIR

    # Crear archivo multiespectral
    profile = {
        "driver": "GTiff",
        "width": 10,
        "height": 10,
        "count": 2,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": from_bounds(0, 0, 1, 1, 10, 10),
    }

    with rasterio.open(test_image_path, "w", **profile) as dst:
        dst.write(red_band, 1)  # Banda roja
        dst.write(nir_band, 2)  # Banda NIR
        dst.update_tags(1, wavelength_nm=665)  # Rojo
        dst.update_tags(2, wavelength_nm=842)  # NIR

    # Configurar logging
    setup_logging(output_dir)

    # Procesar imagen con índices por defecto
    indices_to_calculate = ["ndvi", f"savi_{DEFAULT_SAVI_L}"]
    result_paths = process_image(
        test_image_path, output_dir, indices=indices_to_calculate
    )

    # Verificar resultado
    assert isinstance(result_paths, dict)
    assert len(result_paths) == len(indices_to_calculate)
    assert all(isinstance(path, Path) for path in result_paths.values())
    assert all(path.parent == output_dir for path in result_paths.values())

    # Verificar valores de NDVI
    with rasterio.open(result_paths["ndvi"]) as src:
        ndvi = src.read(1)
        expected_ndvi = (0.8 - 0.3) / (0.8 + 0.3)  # (NIR - RED) / (NIR + RED)
        np.testing.assert_allclose(ndvi, expected_ndvi, rtol=1e-3)
