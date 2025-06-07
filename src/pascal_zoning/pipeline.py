"""Pipeline oficial de zonificación agronómica (CLI / API).

Este módulo implementa la aplicación Typer que:
  1. Carga índices NDVI, NDWI, NDRE, SI desde un TIFF.
  2. Extrae el polígono del predio directamente del raster.
  3. Ejecuta el pipeline de zonificación y guarda resultados.
"""

from __future__ import annotations

# Importaciones de la librería estándar
from datetime import datetime
from pathlib import Path
from typing import List

# Importaciones de terceros
import numpy as np
import rasterio
from loguru import logger
import typer
from shapely.geometry import shape as shape_from_geojson
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from rasterio.features import shapes

# Importaciones de aplicación local
from .config import load_config, ZoningConfig
from .interface import NDVIBlockInterface
from .logging_config import setup_logging
from .viz import zoning_overview
from .zoning import AgriculturalZoning, ProcessingError, ZoningResult

app = typer.Typer(help="Script principal para zonificación agronómica.")

# Constantes
VALID_INDICES = ["ndvi", "ndwi", "ndre", "si"]


def _load_indices(block: NDVIBlockInterface, names: List[str]) -> dict[str, np.ndarray]:
    """Carga índices espectrales solicitados desde el bloque."""
    invalid_indices = [name for name in names if name.lower() not in VALID_INDICES]
    if invalid_indices:
        raise ValueError(
            f"Índices inválidos: {invalid_indices}. Valores permitidos: {VALID_INDICES}"
        )

    names_lower = [name.lower() for name in names]
    data = block.load_spectral_indices(block.data_path, names_lower)
    if not block.validate_spectral_data(data):
        logger.warning("Datos espectrales con advertencias de calidad.")
    return data


class ZoningPipeline:
    """Pipeline orientado a objetos para zonificación agronómica."""

    def __init__(
        self,
        config: ZoningConfig | None = None,
        config_path: Path | None = None,
    ) -> None:
        """Inicializa con configuración o ruta a JSON."""
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
        """Ejecuta zonificación completa y retorna un ZoningResult."""
        ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
        sufijo_k = f"k{force_k}" if force_k is not None else "k_auto"
        tamaño = (
            min_zone_size if min_zone_size is not None else self.config.min_zone_size_ha
        )
        sufijo_mz = f"mz{tamaño}"
        nombre_ejecucion = f"{ahora}_{sufijo_k}_{sufijo_mz}"
        carpeta_base = output_dir / nombre_ejecucion
        carpeta_base.mkdir(parents=True, exist_ok=True)

        setup_logging(carpeta_base)
        logger.info(f"– Iniciando zonificación: carpeta de salida → {carpeta_base}")

        if not raster_path.exists() or not raster_path.is_file():
            raise typer.BadParameter(
                f"El archivo {raster_path} no existe o no es un archivo válido"
            )

        block_folder = raster_path.parent
        block = NDVIBlockInterface(data_path=block_folder)
        indices_dict = _load_indices(block, index_names)

        with rasterio.open(raster_path) as src:
            crs = src.crs.to_string() if src.crs is not None else ""
            transform = src.transform
            banda1 = src.read(1)
            mask_valid = (banda1 > 0).astype(np.uint8)

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

        bounds = polygon_union
        tamaño_zona = tamaño

        engine = AgriculturalZoning(
            random_state=self.config.random_state,
            min_zone_size_ha=tamaño_zona,
            max_zones=self.config.max_zones,
            output_dir=carpeta_base,
        )

        result = engine.run_pipeline(
            indices=indices_dict,
            bounds=bounds,
            points_per_zone=self.config.min_points_per_zone,
            crs=crs,
            force_k=force_k,
            output_dir=carpeta_base,
        )

        out_png = carpeta_base / "zonificacion_results.png"
        zoning_overview(
            zones=result.zones,
            samples=result.samples,
            out_png=out_png,
        )

        logger.info(
            f"– Ejecución finalizada correctamente. Resultados en: {carpeta_base}"
        )
        return result


@app.command()
def run(
    raster: Path = typer.Option(
        ...,
        "--raster",
        help="Ruta al TIFF multibanda recortado al predio (6 bandas).",
    ),
    output_dir: Path = typer.Option(
        Path("outputs"),
        "--output-dir",
        help="Directorio base de resultados",
    ),
    indices: str = typer.Option(
        ",".join(VALID_INDICES),
        "--indices",
        "-i",
        help=(
            "Cadena por coma de índices a usar. " f"Valores permitidos: {VALID_INDICES}"
        ),
    ),
    force_k: int | None = typer.Option(
        None,
        "--force-k",
        "-k",
        help="Si se pasa, fuerza ese número de clusters",
    ),
    min_zone_size: float | None = typer.Option(
        None,
        "--min-zone-size",
        help=(
            "Tamaño mínimo de zona en hectáreas. "
            "Si no se especifica, se usa el valor del archivo de configuración"
        ),
    ),
    config_file: Path = typer.Option(
        None,
        "--config",
        help="JSON de configuración; opcional",
    ),
) -> None:
    """Ejecuta zonificación sobre un TIFF con opciones de línea de comandos."""
    try:
        if not raster.exists() or not raster.is_file():
            raise typer.BadParameter(
                f"El archivo {raster} no existe o no es un archivo válido"
            )

        index_list = [s.strip().lower() for s in indices.split(",") if s.strip()]
        if not index_list:
            raise typer.BadParameter("Debe especificar al menos un índice")

        invalid = [idx for idx in index_list if idx not in VALID_INDICES]
        if invalid:
            raise typer.BadParameter(
                f"Índices inválidos: {invalid}. Valores permitidos: {VALID_INDICES}"
            )

        pipe = ZoningPipeline(config_path=config_file)
        result = pipe.run(
            raster_path=raster,
            index_names=index_list,
            output_dir=output_dir,
            force_k=force_k,
            min_zone_size=min_zone_size,
        )

        logger.info(f"Se generaron {len(result.zones)} zonas de manejo.")
        logger.info(f"Se generaron {len(result.samples)} puntos de muestreo.")
        logger.info(f"Índice de silhouette: {result.metrics.silhouette:.3f}.")

    except Exception as e:
        logger.error(f"Error durante la zonificación: {e}")
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
        help=(
            "Cadena por coma de índices a procesar. "
            f"Valores posibles: {VALID_INDICES}"
        ),
    ),
    force_k: int | None = typer.Option(
        None,
        "--force-k",
        "-k",
        help="Si se especifica, fuerza este número específico de clusters.",
    ),
    min_zone_size: float | None = typer.Option(
        None,
        "--min-zone-size",
        help=(
            "Tamaño mínimo de zona en hectáreas. "
            "Si no se especifica, se usa el valor del archivo de configuración"
        ),
    ),
) -> None:
    """Alternativa de CLI para zonificación con nombre de comando 'zonificar'."""
    try:
        if not raster.exists() or not raster.is_file():
            raise typer.BadParameter(
                f"El archivo {raster} no existe o no es un archivo válido"
            )

        index_list = [s.strip().lower() for s in indices.split(",") if s.strip()]
        invalid = [idx for idx in index_list if idx not in VALID_INDICES]
        if invalid:
            raise typer.BadParameter(
                f"Índices inválidos: {invalid}. Valores permitidos: {VALID_INDICES}"
            )

        pipeline = ZoningPipeline()
        result = pipeline.run(
            raster_path=raster,
            index_names=index_list,
            output_dir=output_dir,
            force_k=force_k,
            min_zone_size=min_zone_size,
        )

        logger.info(f"Se generaron {len(result.zones)} zonas de manejo.")
        logger.info(f"Se generaron {len(result.samples)} puntos de muestreo.")
        logger.info(f"Índice de silhouette: {result.metrics.silhouette:.3f}.")

    except Exception as e:
        logger.error(f"Error durante la zonificación: {e}")
        raise typer.Exit(code=1)


def main() -> None:
    """Punto de entrada para CLI; lanza Typer."""
    app()


if __name__ == "__main__":
    main()
