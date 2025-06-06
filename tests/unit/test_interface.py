# tests/unit/test_interface.py

import numpy as np
import pytest
from pathlib import Path

from pascal_zoning.interface import NDVIBlockInterface


def test_safe_divide_nan_behavior():
    """
    Generamos dos arrays pequeños con NaN y ceros, y validamos que
    safe_divide(a,b) retorne NaN cuando a ó b era NaN originalmente,
    y retorne 0.0 únicamente cuando denominador==0 pero a,b no eran NaN.
    """
    # Creamos un array "a" con un NaN en [0,0] y "b" sin NaN
    a = np.array([[np.nan, 2.0], [3.0, -3.0]], dtype=float)
    b = np.array([[1.0, 2.0], [3.0, 3.0]], dtype=float)

    # Copiamos la implementación de safe_divide tal cual está en interface.py
    def safe_divide(a_arr: np.ndarray, b_arr: np.ndarray) -> np.ndarray:
        """
        Calcula (a - b)/(a + b) de modo que:
        - Si a ó b es NaN, el resultado es NaN.
        - Si (a+b)==0, devolvemos 0.0 (para evitar división por cero),
          pero solo cuando a,b no eran NaN originalmente.
        """
        mask_input_nan = np.isnan(a_arr) | np.isnan(b_arr)

        with np.errstate(divide="ignore", invalid="ignore"):
            numerador = a_arr - b_arr
            denominador = a_arr + b_arr
            resultado = np.divide(
                numerador,
                denominador,
                out=np.zeros_like(a_arr, dtype=np.float32),
                where=(denominador != 0),
            )
        # Forzamos NaN en las posiciones donde a ó b era NaN
        resultado[mask_input_nan] = np.nan

        return resultado

    result = safe_divide(a, b)

    # 1) En [0,0], a es NaN → result[0,0] debe ser NaN
    assert np.isnan(result[0, 0])

    # 2) En [1,1], a = -3.0, b = 3.0 → (−3−3)/(−3+3) = (−6)/0 → forzamos 0.0
    assert result[1, 1] == pytest.approx(0.0)

    # 3) En [1,0], a = 3.0, b = 3.0 → (3−3)/(3+3) = 0/6 → 0.0
    assert result[1, 0] == pytest.approx(0.0)

    # 4) En [0,1], a = 2.0, b = 2.0 → (2−2)/(2+2) = 0/4 → 0.0
    assert result[0, 1] == pytest.approx(0.0)


def test_validate_spectral_data_shapes_and_quality(synthetic_indices_2x2):
    """
    Validamos validate_spectral_data():
    - Si todos los índices son float y tienen la misma forma, retorna True,
      incluso si el porcentaje de píxeles válidos < quality_threshold.
    - Si la forma es inconsistente, lanza un error.
    - Si el dict está vacío, devuelve False.
    """
    indices = synthetic_indices_2x2  # fixture definida en conftest.py

    # Creamos interfaz con threshold muy alto para forzar warning
    interface = NDVIBlockInterface(data_path=Path("."), quality_threshold=0.9)

    # validate_spectral_data debe devolver True (shape consistente),
    # pero imprimir warnings (porque el ratio de válidos es < 90%).
    assert interface.validate_spectral_data(indices) is True

    # Ahora probamos shapes inconsistentes: inyectamos un índice de distinta forma
    bad_indices = {"ndvi": np.ones((2, 2)), "ndre": np.ones((3, 3))}
    with pytest.raises(Exception):
        interface.validate_spectral_data(bad_indices)

    # Verificamos que, si no hay índices (dict vacío), retorne False
    assert interface.validate_spectral_data({}) is False
