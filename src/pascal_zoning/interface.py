"""Interfaz para cargar un TIFF multibanda y calcular índices espectrales.

Incluye validación de calidad según porcentaje mínimo de píxeles válidos.
"""

from pathlib import Path

import numpy as np
import rasterio
from loguru import logger


class NDVIBlockInterface:
    """Interfaz para manejar datos espectrales de un bloque satelital."""

    def __init__(
        self,
        data_path: Path,
        quality_threshold: float = 0.7,
    ) -> None:
        """Inicializa la interfaz con ruta y umbral de calidad.

        Args:
            data_path: Carpeta que contiene exactamente un .tif multibanda (6 bandas).
            quality_threshold: Fracción mínima de píxeles válidos (0–1) requerida.
        """
        self.data_path = Path(data_path)
        self.quality_threshold = quality_threshold

    @staticmethod
    def safe_divide(a_arr: np.ndarray, b_arr: np.ndarray) -> np.ndarray:
        """Calcula (a - b)/(a + b) evitando división por cero.

        - Si a o b es NaN, el resultado será NaN.
        - Si (a + b) == 0 (sin NaN), devuelve 0.0 para evitar excepción.
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
        resultado[mask_input_nan] = np.nan
        return resultado

    def load_spectral_indices(
        self, tif_folder: Path, names: list[str]
    ) -> dict[str, np.ndarray]:
        """Lee un TIFF multibanda y calcula índices espectrales.

        Asume que el TIFF en `tif_folder` tiene 6 bandas con orden:
        Azul, Verde, Rojo, NIR, RedEdge, SWIR.

        Args:
            tif_folder: Carpeta que contiene exactamente un archivo .tif.
            names: Lista de nombres de índices (ndvi, ndwi, ndre, si).

        Returns:
            Diccionario con arrays numpy para cada índice calculado.
        """
        tif_folder = Path(tif_folder)
        tif_files = list(tif_folder.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {tif_folder} esperaba un .tif, hallé: {tif_files}"  # noqa: E501
            )

        raster_path = tif_files[0]
        with rasterio.open(raster_path) as src:
            b2 = src.read(2).astype(np.float32)
            b3 = src.read(3).astype(np.float32)
            b4 = src.read(4).astype(np.float32)
            b5 = src.read(5).astype(np.float32)
            b6 = src.read(6).astype(np.float32)

        resultados: dict[str, np.ndarray] = {}
        for idx in names:
            idx_lower = idx.lower().strip()
            if idx_lower == "ndvi":
                resultados["ndvi"] = self.safe_divide(b4, b3)
            elif idx_lower == "ndwi":
                resultados["ndwi"] = self.safe_divide(b2, b4)
            elif idx_lower == "ndre":
                resultados["ndre"] = self.safe_divide(b4, b5)
            elif idx_lower == "si":
                resultados["si"] = self.safe_divide(b3, b6)
            else:
                raise ValueError(f"Índice desconocido: {idx}")

        return resultados

    def validate_spectral_data(self, indices: dict[str, np.ndarray]) -> bool:
        """Valida calidad y consistencia de datos espectrales.

        Verifica que:
        1) El diccionario no esté vacío.
        2) Cada arreglo sea numpy.float con la misma forma.
        3) El porcentaje válido supere `quality_threshold`; sino warning.

        Args:
            indices: Diccionario con arrays para cada índice.

        Returns:
            True si la validación básica pasa; False si `indices` está vacío.
        """
        if not indices:
            return False

        shapes = []
        for nombre, arr in indices.items():
            if not isinstance(arr, np.ndarray):
                raise TypeError(f"{nombre} no es numpy.ndarray.")
            if not np.issubdtype(arr.dtype, np.floating):
                raise TypeError(f"{nombre} debe ser tipo float, no {arr.dtype}.")
            shapes.append((nombre, arr.shape))

        formas = [f for _, f in shapes]
        if len({f for f in formas}) != 1:
            lista_formas = [f"{n}:{s}" for n, s in shapes]
            logger.error(f"Formas inconsistentes: {lista_formas}.")
            raise Exception("Formas inconsistentes de índices.")

        total_pixeles = formas[0][0] * formas[0][1]
        for nombre, arr in indices.items():
            n_validos = np.count_nonzero(~np.isnan(arr))
            ratio = n_validos / total_pixeles
            if ratio < self.quality_threshold:
                logger.warning(
                    f"Baja calidad {nombre}: {ratio*100:.1f}% < umbral {self.quality_threshold*100:.1f}%."  # noqa: E501
                )
        return True

    def get_data_bounds(self) -> tuple[float, float, float, float]:
        """Obtiene límites (xmin, ymin, xmax, ymax) del TIFF."""
        tif_files = list(self.data_path.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {self.data_path} esperaba un .tif, hallé: {tif_files}"  # noqa: E501
            )
        with rasterio.open(tif_files[0]) as src:
            return (
                src.bounds.left,
                src.bounds.bottom,
                src.bounds.right,
                src.bounds.top,
            )

    def get_crs(self) -> dict | str:
        """Devuelve CRS del TIFF (dict o string, p.ej. 'EPSG:4326')."""
        tif_files = list(self.data_path.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {self.data_path} esperaba un .tif, hallé: {tif_files}"  # noqa: E501
            )
        with rasterio.open(tif_files[0]) as src:
            return src.crs
