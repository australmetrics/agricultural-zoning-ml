"""Unit tests for core functionality.

Validates individual components according to ISO 42001 test requirements."""

from pathlib import Path
from src.config import (
    get_config,
    DEFAULT_SAVI_L,
    VALID_L_RANGE,
    VALID_INDICES,
    SUPPORTED_SATELLITES,
)


def test_config_values() -> None:
    """Verifies that configuration values are correct and within valid ranges."""
    config = get_config()

    # Verifica directorios
    assert isinstance(config["output_dir"], Path)
    assert isinstance(config["data_dir"], Path)

    # Verifica parámetros de índices
    assert DEFAULT_SAVI_L >= VALID_L_RANGE[0]
    assert DEFAULT_SAVI_L <= VALID_L_RANGE[1]
    assert all(idx in VALID_INDICES for idx in ["ndvi", "savi"])

    # Verifica configuración de satélites
    for sat_config in SUPPORTED_SATELLITES.values():
        assert "red_band" in sat_config
        assert "nir_band" in sat_config
        assert "resolution" in sat_config
        assert isinstance(sat_config["resolution"], int)


def test_satellite_config() -> None:
    """Verifica la configuración para diferentes tipos de satélites."""
    config = get_config()
    assert isinstance(config, dict)
    assert "satellites" in config
    assert "sentinel2" in config["satellites"]
    assert "landsat8" in config["satellites"]


def test_index_validation() -> None:
    """Verifica la validación de índices vegetativos."""
    config = get_config()
    assert isinstance(config, dict)
    assert "indices" in config
    assert "ndvi" in config["indices"]
    assert "savi" in config["indices"]


def test_l_factor_range() -> None:
    """Verifica que el factor L para SAVI esté en el rango correcto."""
    config = get_config()
    assert isinstance(config, dict)
    assert "indices" in config
    assert "savi" in config["indices"]
    assert "l_factor" in config["indices"]["savi"]
    l_factor = config["indices"]["savi"]["l_factor"]
    assert 0 <= l_factor <= 1
