"""
NDVIBlockInterface: Interfaz para cargar un TIFF multibanda y calcular
distintos índices espectrales (NDVI, NDWI, NDRE, SI). También valida la
calidad de los datos espectrales (formas, tipos y porcentaje de píxeles válidos).
"""

from pathlib import Path
import warnings

import numpy as np
import rasterio
from rasterio.coords import BoundingBox
from loguru import logger


class NDVIBlockInterface:
    """
    Interfaz que sabe:
      1) Leer un TIFF multibanda (6 bandas) recortado al predio.
      2) Calcular índices espectrales: ndvi, ndwi, ndre y si.
      3) Validar la calidad de dichos índices (misma forma, tipo float2D,
         porcentaje de píxeles válidos).
    """

    def __init__(
        self,
        data_path: Path,
        quality_threshold: float = 0.7,
    ) -> None:
        """
        Args:
            data_path: Carpeta donde vive EXACTAMENTE un .tif multibanda (6 bandas).
            quality_threshold: fracción mínima de píxeles válidos (0–1) para cada índice.
        """
        self.data_path = Path(data_path)
        self.quality_threshold = quality_threshold

    @staticmethod
    def safe_divide(a_arr: np.ndarray, b_arr: np.ndarray) -> np.ndarray:
        """
        Calcula (a - b)/(a + b) de modo que:
          - Si a ó b es NaN, el resultado en esa posición es NaN.
          - Si (a + b) == 0 (y ninguno es NaN), devuelve 0.0 (para evitar división por cero).
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
        # garantizar que donde alguno era NaN, el resultado sea NaN
        resultado[mask_input_nan] = np.nan
        return resultado

    def load_spectral_indices(
        self, tif_folder: Path, names: list[str]
    ) -> dict[str, np.ndarray]:
        """
        Lee el TIFF multibanda (6 bandas) y calcula los índices solicitados.
        Asume que el TIFF tiene seis bandas, ordenadas así:
          1) Azul
          2) Verde
          3) Rojo
          4) NIR  (Infrarrojo Cercano)
          5) RedEdge (Rojo-Extremo)
          6) SWIR (Infrarrojo de Onda Corta)
        Retorna un dict: {"ndvi": array2D, "ndwi": array2D, "ndre": array2D, "si": array2D}
        """
        tif_folder = Path(tif_folder)
        # Tomamos el único .tif que exista en esa carpeta
        tif_files = list(tif_folder.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {tif_folder} esperaba EXACTAMENTE un *.tif, pero hallé: {tif_files}"
            )

        raster_path = tif_files[0]
        with rasterio.open(raster_path) as src:
            # Leer las seis bandas:
            #   b1 = Azul, b2 = Verde, b3 = Rojo, b4 = NIR, b5 = RedEdge, b6 = SWIR
            b1 = src.read(1).astype(np.float32)
            b2 = src.read(2).astype(np.float32)
            b3 = src.read(3).astype(np.float32)
            b4 = src.read(4).astype(np.float32)
            b5 = src.read(5).astype(np.float32)
            b6 = src.read(6).astype(np.float32)

        resultados: dict[str, np.ndarray] = {}

        for idx in names:
            idx_lower = idx.lower().strip()
            if idx_lower == "ndvi":
                # (NIR - Rojo)/(NIR + Rojo)
                resultados["ndvi"] = self.safe_divide(b4, b3)
            elif idx_lower == "ndwi":
                # (Verde - NIR)/(Verde + NIR)
                resultados["ndwi"] = self.safe_divide(b2, b4)
            elif idx_lower == "ndre":
                # (NIR - RedEdge)/(NIR + RedEdge)
                resultados["ndre"] = self.safe_divide(b4, b5)
            elif idx_lower == "si":
                # (Rojo - SWIR)/(Rojo + SWIR)
                resultados["si"] = self.safe_divide(b3, b6)
            else:
                raise ValueError(f"Índice desconocido: {idx}")

        return resultados

    def validate_spectral_data(self, indices: dict[str, np.ndarray]) -> bool:
        """
        Verifica:
          1) Si el dict está vacío: retorna False (no hay datos).
          2) Que todas las matrices existan, sean float, y tengan idéntica forma.
             - Si la forma es inconsistente → lanza Exception.
          3) Calcula el % de píxeles válidos (no NaN) para cada índice.
             - Si para algún índice el ratio < quality_threshold → emite warning, 
               pero igual retorna True.
          4) Si todo OK, retorna True.
        """
        if not indices:
            # “no hay índices” → devolvemos False
            return False

        # Verificar que todas las entradas son arrays de tipo float y mismas dimensiones
        shapes = []
        for nombre, arr in indices.items():
            if not isinstance(arr, np.ndarray):
                raise TypeError(f"{nombre} no es un numpy.ndarray")
            if not np.issubdtype(arr.dtype, np.floating):
                raise TypeError(f"{nombre} debe ser de tipo float, no {arr.dtype}")
            shapes.append((nombre, arr.shape))

        # Revisar si las formas son todas iguales
        formas = [forma for _, forma in shapes]
        if len({forma for forma in formas}) != 1:
            lista_formas = [f"{n}:{s}" for n, s in shapes]
            logger.error(f"Las formas de los índices son inconsistentes: {lista_formas}")
            raise Exception("Formas de índices espectrales inconsistentes")

        # Chequear %, emitir warning si debajo del umbral
        referencia_shape = formas[0]
        total_pixeles = referencia_shape[0] * referencia_shape[1]
        for nombre, arr in indices.items():
            n_validos = np.count_nonzero(~np.isnan(arr))
            ratio = n_validos / total_pixeles
            if ratio < self.quality_threshold:
                logger.warning(
                    f"Baja calidad para {nombre}: solo {ratio*100:.1f}% de píxeles válidos "
                    f"(umbral mínimo {self.quality_threshold*100:.1f}%)."
                )
        return True

    def get_data_bounds(self) -> tuple[float, float, float, float]:
        """
        Abre el TIFF y devuelve (xmin, ymin, xmax, ymax).
        """
        tif_files = list(self.data_path.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {self.data_path} esperaba EXACTAMENTE un *.tif, pero hallé: {tif_files}"
            )
        with rasterio.open(tif_files[0]) as src:
            return src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top

    def get_crs(self) -> dict | str:
        """
        Devuelve el CRS del TIFF, en forma de dict o string (p.ej. 'EPSG:4326').
        """
        tif_files = list(self.data_path.glob("*.tif"))
        if len(tif_files) != 1:
            raise FileNotFoundError(
                f"En {self.data_path} esperaba EXACTAMENTE un *.tif, pero hallé: {tif_files}"
            )
        with rasterio.open(tif_files[0]) as src:
            return src.crs










