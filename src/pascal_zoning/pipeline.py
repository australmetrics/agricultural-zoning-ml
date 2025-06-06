# src/pascal_zoning/pipeline.py

from __future__ import annotations
from .interface import NDVIBlockInterface
from .zoning import AgriculturalZoning, ZoningResult, ProcessingError
from .viz import zoning_overview

"""
Pipeline oficial de zonificación agronómica (CLI / API).
Ahora NO requiere un archivo de polígono: se extrae directamente del TIFF.
"""
from pathlib import Path
from typing import List
from datetime import datetime

import numpy as np
from loguru import logger
import typer
from shapely.geometry import shape as shape_from_geojson, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.base import BaseGeometry

from .config import load_config, ZoningConfig
from .logging_config import setup_logging

import rasterio
from rasterio.features import shapes


app = typer.Typer(help="Script principal para zonificación agronómica.")

# Constantes
VALID_INDICES = ["ndvi", "ndwi", "ndre", "si"]


# --------------------------------------------------------------------------- #
# Helpers internos
# --------------------------------------------------------------------------- #


def _load_indices(block: NDVIBlockInterface, names: List[str]) -> dict[str, np.ndarray]:
    """
    Carga los índices espectrales solicitados desde el bloque.

    Args:
        block: Interfaz del bloque de datos.
        names: Lista de nombres de índices a cargar. Deben pertenecer a VALID_INDICES.

    Returns:
        Dict con arrays numpy de índices.
    """
    invalid_indices = [name for name in names if name.lower() not in VALID_INDICES]
    if invalid_indices:
        raise ValueError(
            f"Índices inválidos: {invalid_indices}. Valores permitidos: {VALID_INDICES}"
        )

    names = [name.lower() for name in names]
    data = block.load_spectral_indices(block.data_path, names)
    if not block.validate_spectral_data(data):
        logger.warning("Datos espectrales con advertencias de calidad")
    return data


# --------------------------------------------------------------------------- #
# Pipeline OO (usable también en tests)
# --------------------------------------------------------------------------- #


class ZoningPipeline:
    def __init__(
        self,
        config: ZoningConfig | None = None,
        config_path: Path | None = None,
    ) -> None:
        self.config: ZoningConfig = config or load_config(config_path)
        self.config.validate_all()

    def run(
        self,
        raster_path: Path,
        index_names: List[str],
        output_dir: Path,
        force_k: int | None = None,
        min_zone_size: float | None = None,
    ) -> ZoningResult:
        """
        Ejecuta la zonificación completa y devuelve un `ZoningResult`.

        Args:
            raster_path: Ruta al TIFF multibanda recortado al predio (6 bandas).
            index_names: Lista de índices a calcular (de VALID_INDICES).
            output_dir: Carpeta base donde se guardan los resultados.
            force_k: Si se especifica, fuerza ese número de clusters.
            min_zone_size: Tamaño mínimo de zona en hectáreas. Si no se especifica, se usa la configuración.
        Returns:
            ZoningResult con zonas, puntos de muestreo y métricas.
        """
        # -------------------------------------------------------------
        # 1) Generar subdirectorio único (timestamp + parámetros) dentro de output_dir
        # -------------------------------------------------------------
        ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
        sufijo_k = f"k{force_k}" if force_k is not None else "k_auto"
        sufijo_mz = f"mz{min_zone_size or self.config.min_zone_size_ha}"
        nombre_ejecucion = f"{ahora}_{sufijo_k}_{sufijo_mz}"
        carpeta_base = output_dir / nombre_ejecucion
        carpeta_base.mkdir(parents=True, exist_ok=True)

        # 2) Configurar logging apuntando al subdirectorio recién creado
        setup_logging(carpeta_base)

        logger.info(f"– Iniciando zonificación: carpeta de salida → {carpeta_base}")

        # -------------------------------------------------------------
        # 3) Verificar que el archivo TIFF exista
        # -------------------------------------------------------------
        if not raster_path.exists() or not raster_path.is_file():
            raise typer.BadParameter(
                f"El archivo {raster_path} no existe o no es un archivo válido"
            )

        # -------------------------------------------------------------
        # 4) Cargar índices espectrales desde el TIFF multibanda
        #    NDVIBlockInterface espera la carpeta contenedora, no el .tif directamente
        # -------------------------------------------------------------
        block_folder = raster_path.parent
        block = NDVIBlockInterface(data_path=block_folder)
        indices_dict = _load_indices(block, index_names)

        # -------------------------------------------------------------
        # 5) Extraer polígono de la parcela leyendo la primera banda
        # -------------------------------------------------------------
        with rasterio.open(raster_path) as src:
            crs = src.crs.to_string() if src.crs is not None else ""
            transform = src.transform

            # Leer la primera banda para distinguir fondo (0) de parcela (>0)
            banda1 = src.read(1)  # shape: (height, width)

            # Construir la máscara: 1 donde banda1 > 0 (parcela), 0 donde banda1 == 0 (fondo)
            mask_valid = (banda1 > 0).astype(np.uint8)

            # Extraer contornos de mask_valid
            geoms: list[BaseGeometry] = []
            for geom_geojson, val in shapes(
                mask_valid, mask=mask_valid, transform=transform
            ):
                if val == 1:
                    geoms.append(shape_from_geojson(geom_geojson))

            if not geoms:
                raise ProcessingError(
                    "No se pudo derivar polígono: todos los píxeles están en 0."
                )
            polygon_union = unary_union(geoms)

        # -------------------------------------------------------------
        # 6) Preparar bounds y parámetros de zonificación
        # -------------------------------------------------------------
        bounds = polygon_union  # Polygon o MultiPolygon
        tamaño_mínimo = (
            min_zone_size if min_zone_size is not None else self.config.min_zone_size_ha
        )

        engine = AgriculturalZoning(
            random_state=self.config.random_state,
            min_zone_size_ha=tamaño_mínimo,
            max_zones=self.config.max_zones,
            output_dir=carpeta_base,
        )

        # -------------------------------------------------------------
        # 7) Ejecutar pipeline de zonificación completo
        # -------------------------------------------------------------
        result = engine.run_pipeline(
            indices=indices_dict,
            bounds=bounds,
            points_per_zone=self.config.min_points_per_zone,
            crs=crs,
            force_k=force_k,
            output_dir=carpeta_base,
        )

        # -------------------------------------------------------------
        # 8) Generar visualización resumen (zoning_overview)
        # -------------------------------------------------------------
        out_png = carpeta_base / "zonificacion_results.png"
        zoning_overview(zones=result.zones, samples=result.samples, out_png=out_png)

        logger.info(
            f"– Ejecución finalizada correctamente. Resultados en: {carpeta_base}"
        )
        return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


@app.command()
def run(
    raster: Path = typer.Option(
        ..., "--raster", help="Ruta al TIFF multibanda recortado al predio (6 bandas)."
    ),
    output_dir: Path = typer.Option(
        Path("outputs"), "--output-dir", help="Directorio base de resultados"
    ),
    indices: str = typer.Option(
        "ndvi,ndwi,ndre,si",
        "--indices",
        "-i",
        help=f"Cadena separada por coma de índices a usar. Valores permitidos: {VALID_INDICES}",
    ),
    force_k: int = typer.Option(
        None, "--force-k", "-k", help="Si se pasa, fuerza ese número de clusters"
    ),
    min_zone_size: float = typer.Option(
        None,
        "--min-zone-size",
        help="Tamaño mínimo de zona en hectáreas. Si no se especifica, se usa el valor del archivo de configuración",
    ),
    config_file: Path = typer.Option(
        None, "--config", help="JSON de configuración; opcional"
    ),
) -> None:
    """
    Ejecuta la zonificación sobre un TIFF multibanda recortado al predio.

    - raster: ruta al archivo TIFF con 6 bandas recortado al predio.
    - indices: cadena separada por coma de índices a usar (ndvi,ndwi,ndre,si).
    - force-k: si se especifica, se fuerza ese número de clusters.

    Ejemplo:
       python -m pascal_zoning.pipeline \\
         --raster inputs/predio_recortado_x.tif \\
         --output-dir outputs \\
         --indices ndvi,ndre,si \\
         --force-k 3
    """
    try:
        # 1) Validar archivo TIFF
        if not raster.exists() or not raster.is_file():
            raise typer.BadParameter(
                f"El archivo {raster} no existe o no es un archivo válido"
            )

        # 2) Normalizar índices: siempre llega como string
        index_list = [s.strip().lower() for s in indices.split(",") if s.strip()]
        if not index_list:
            raise typer.BadParameter("Debe especificar al menos un índice")

        invalid = [idx for idx in index_list if idx not in VALID_INDICES]
        if invalid:
            raise typer.BadParameter(
                f"Índices inválidos: {invalid}. Valores permitidos: {VALID_INDICES}"
            )

        # 3) Ejecutar pipeline
        pipe = ZoningPipeline(config_path=config_file)
        result = pipe.run(
            raster_path=raster,
            index_names=index_list,
            output_dir=output_dir,
            force_k=force_k,
            min_zone_size=min_zone_size,
        )

        # 4) Mostrar estadísticas por consola
        logger.info(f"Se generaron {len(result.zones)} zonas de manejo")
        logger.info(f"Se generaron {len(result.samples)} puntos de muestreo")
        logger.info(f"Índice de silhouette: {result.metrics.silhouette:.3f}")

    except Exception as e:
        logger.error(f"Error durante la zonificación: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def zonificar(
    raster: Path = typer.Argument(
        ..., help="Ruta al TIFF multibanda recortado al predio (6 bandas)."
    ),
    output_dir: Path = typer.Option(
        Path("outputs"),
        "--output-dir",
        "-o",
        help="Carpeta base donde se guardan los resultados.",
    ),
    indices: str = typer.Option(
        ",".join(VALID_INDICES),
        "--indices",
        "-i",
        help=f"Cadena separada por coma de índices a procesar. Valores posibles: {VALID_INDICES}",
    ),
    force_k: int = typer.Option(
        None,
        "--force-k",
        "-k",
        help="Si se especifica, fuerza este número específico de clusters.",
    ),
    min_zone_size: float = typer.Option(
        None,
        "--min-zone-size",
        help="Tamaño mínimo de zona en hectáreas. Si no se especifica, se usa el valor del archivo de configuración",
    ),
) -> None:
    """
    Alternativa de CLI para zonificación, similar a 'run' pero con otro nombre de comando.
    Acepta índices como cadena separada por coma.
    """
    try:
        # 1) Validar TIFF
        if not raster.exists() or not raster.is_file():
            raise typer.BadParameter(
                f"El archivo {raster} no existe o no es un archivo válido"
            )

        # 2) Normalizar índices (siempre string separado por coma)
        index_list = [s.strip().lower() for s in indices.split(",") if s.strip()]

        invalid = [idx for idx in index_list if idx not in VALID_INDICES]
        if invalid:
            raise typer.BadParameter(
                f"Índices inválidos: {invalid}. Valores permitidos: {VALID_INDICES}"
            )

        # 3) Ejecutar pipeline
        pipeline = ZoningPipeline()
        result = pipeline.run(
            raster_path=raster,
            index_names=index_list,
            output_dir=output_dir,
            force_k=force_k,
            min_zone_size=min_zone_size,
        )

        logger.info(f"Se generaron {len(result.zones)} zonas de manejo")
        logger.info(f"Se generaron {len(result.samples)} puntos de muestreo")
        logger.info(f"Índice de silhouette: {result.metrics.silhouette:.3f}")

    except Exception as e:
        logger.error(f"Error durante la zonificación: {str(e)}")
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    app()
