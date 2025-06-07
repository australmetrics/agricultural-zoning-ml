# tests/unit/test_zoning_core.py
#
# Cobertura mínima de la API *pública* de AgriculturalZoning
# sin depender de helpers internos que ya no existen
# ( _preprocess_features, _create_zone_polygons, etc.).

import numpy as np
import pytest
from shapely.geometry import Polygon
import geopandas as gpd

from pascal_zoning.zoning import (
    AgriculturalZoning,
    ClusterMetrics,
    ZoneStats,
    ZoningResult,
    ProcessingError,
)

# ------------------------------------------------------------------ #
# --------------------------- FIXTURES ------------------------------ #
# ------------------------------------------------------------------ #


@pytest.fixture
def synthetic_indices_2x2():
    """
    Diccionario de índices 2×2.  Usa nombres en MAYÚSCULAS
    porque zoning.py espera 'NDVI', 'NDRE', etc.
    """
    ndvi = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=float)
    ndre = np.array([[-0.1, -0.2], [-0.3, -0.4]], dtype=float)
    return {"NDVI": ndvi, "NDRE": ndre}


@pytest.fixture
def bounds_polygon():
    """Polígono cuadrado 2 m × 2 m."""
    return Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])


# ------------------------------------------------------------------ #
# --------------------------- PRUEBAS ------------------------------- #
# ------------------------------------------------------------------ #


def test_run_pipeline_basic(synthetic_indices_2x2, bounds_polygon, tmp_path):
    """
    Ejecuta el pipeline completo y comprueba que genera
    zonas, muestras y métricas coherentes.
    """
    zoning = AgriculturalZoning(
        random_state=0,
        min_zone_size_ha=0.0,
        max_zones=3,
        output_dir=tmp_path,
    )

    result: ZoningResult = zoning.run_pipeline(
        indices=synthetic_indices_2x2,
        bounds=bounds_polygon,
        points_per_zone=2,
        crs="EPSG:32719",
        force_k=2,  # k fijo para reproducibilidad
    )

    # ------------- estructuras de salida ------------- #
    assert isinstance(result.zones, gpd.GeoDataFrame)
    assert isinstance(result.samples, gpd.GeoDataFrame)
    assert not result.zones.empty
    assert not result.samples.empty

    # ------------- métricas de clustering ------------- #
    assert isinstance(result.metrics, ClusterMetrics)
    assert result.metrics.n_clusters == 2
    assert -1.0 <= result.metrics.silhouette <= 1.0
    assert result.metrics.calinski_harabasz >= 0.0

    # ------------- estadísticas de zona -------------- #
    assert isinstance(result.stats, list)
    assert len(result.stats) == 2  # k=2 ⇒ dos zonas
    for st in result.stats:
        assert isinstance(st, ZoneStats)
        assert st.area_ha > 0.0
        assert 0.0 <= st.compactness <= 1.0
        assert "NDVI" in st.mean_values and "NDRE" in st.mean_values


def test_min_zone_size_filtering(bounds_polygon, synthetic_indices_2x2):
    """
    Si min_zone_size_ha es mayor que el área total de cada zona,
    el pipeline debe lanzar ProcessingError.
    """
    # Cada zona mide 0.0002 ha; probamos con 10 ha.
    zoning_big = AgriculturalZoning(min_zone_size_ha=10.0, max_zones=2)
    with pytest.raises(ProcessingError):
        zoning_big.run_pipeline(
            indices=synthetic_indices_2x2,
            bounds=bounds_polygon,
            points_per_zone=2,
            crs="EPSG:32719",
            force_k=2,
        )

    # Con un umbral muy pequeño sí debe pasar.
    zoning_ok = AgriculturalZoning(min_zone_size_ha=0.00005, max_zones=2)
    res = zoning_ok.run_pipeline(
        indices=synthetic_indices_2x2,
        bounds=bounds_polygon,
        points_per_zone=2,
        crs="EPSG:32719",
        force_k=2,
    )
    assert not res.zones.empty


def test_files_are_created(tmp_path, bounds_polygon, synthetic_indices_2x2):
    """
    Comprueba que save_results() crea los archivos esperados
    cuando se pasa output_dir.
    """
    zoning = AgriculturalZoning(min_zone_size_ha=0.00005, output_dir=tmp_path)
    zoning.run_pipeline(
        indices=synthetic_indices_2x2,
        bounds=bounds_polygon,
        points_per_zone=2,
        crs="EPSG:32719",
        force_k=2,
    )

    expected = {
        "zonificacion_agricola.gpkg",
        "puntos_muestreo.gpkg",
        "estadisticas_zonas.csv",
        "metricas_clustering.json",
    }
    produced = {p.name for p in tmp_path.iterdir()}
    assert expected.issubset(produced), f"Faltan archivos: {expected - produced}"
