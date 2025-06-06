# tests/unit/test_viz.py
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # para asegurar backend no interactivo
from shapely.geometry import Polygon, Point
from pathlib import Path
from pascal_zoning.viz import zoning_overview

def test_zoning_overview_creates_png(tmp_path):
    """
    Creamos dos GeoDataFrames mínimos:
    - zones_gdf: 2 polígonos rectangulares
    - samples_gdf: 3 puntos
    Llamamos a zoning_overview(...) y verificamos que el PNG exista.
    """
    # 1) Construir una GeoDataFrame de zonas con 2 polígonos triviales
    poly1 = Polygon([(0,0), (1,0), (1,1), (0,1)])
    poly2 = Polygon([(1,0), (2,0), (2,1), (1,1)])
    zones_gdf = gpd.GeoDataFrame(
        {"cluster": [0, 1], "zone_name": ["Zona_00", "Zona_01"], "area_ha": [0.0001, 0.0001]},
        geometry=[poly1, poly2],
        crs="EPSG:32719"
    )

    # 2) Construir una GeoDataFrame de muestras (un punto en cada zona)
    pts = [Point(0.5, 0.5), Point(1.5, 0.5)]
    samples_gdf = gpd.GeoDataFrame(
        {"zone_name": ["Zona_00", "Zona_01"]},
        geometry=pts,
        crs="EPSG:32719"
    )

    output_file = tmp_path / "test_overview.png"
    zoning_overview(zones_gdf, samples_gdf, output_file)

    # Verificamos que el archivo PNG se haya creado
    assert output_file.exists()
    # Opcional: podemos comprobar que no está vacío (tamaño > 0 bytes)
    assert output_file.stat().st_size > 0
