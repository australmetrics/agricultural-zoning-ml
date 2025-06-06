# tests/unit/conftest.py
import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon


@pytest.fixture
def synthetic_indices_2x2():
    """
    Devuelve un dict de índices “mínimos” para probar interfaces y preprocesos:
    - ndvi: array 2×2 con valores [0.1, 0.2; 0.3, 0.4]
    - ndre: array 2×2 con valores [-0.1, -0.2; -0.3, -0.4]
    """
    ndvi = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=float)
    ndre = np.array([[-0.1, -0.2], [-0.3, -0.4]], dtype=float)
    return {"ndvi": ndvi, "ndre": ndre}


@pytest.fixture
def synthetic_bounds_polygon():
    """
    Devuelve un polígono 2×2 (0,0)-(2,0)-(2,2)-(0,2) para usar como bounds.
    """
    return Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
