"""Main module for PASCAL NDVI Block.

Provides the command-line interface and core functions for processing satellite
imagery and calculating vegetation indices following ISO 42001 guidelines.
"""

from pathlib import Path
import typer
from loguru import logger
from typing import Optional, List, Dict
from src.preprocessor import clip_image_with_shapefile
from src.indices import calculate_all_indices
from src.logging_config import setup_logging

app = typer.Typer()


def init_logging(output_dir: Path) -> None:
    """Initializes the ISO 42001 compliant logging system."""
    setup_logging(output_dir)
    logger.info("🚀 Iniciando P.A.S.C.A.L NDVI Block")
    logger.info(f"📁 Directorio de salida: {output_dir}")


@app.command("clip")
def clip(
    image: Path = typer.Option(..., exists=True, help="Multiband .tif file"),
    shapefile: Path = typer.Option(..., exists=True, help="Polygon .shp file"),
    output: Path = typer.Option("results", help="Output directory"),
) -> Path:
    """Clips a satellite image using a shapefile.

    Clips input raster to the extent of provided shapefile while preserving
    all bands and metadata.

    Args:
        image: Path to multiband image file
        shapefile: Path to polygon shapefile
        output: Directory to save results

    Returns:
        Path: Path to clipped file
    """
    # Inicializar logging
    init_logging(Path(output))
    """
    Recorta una imagen satelital usando un shapefile de polígonos.
    """
    logger.info(f"🛰️ Iniciando recorte de: {image}")
    logger.info(f"🗺️ Usando shapefile: {shapefile}")

    output.mkdir(parents=True, exist_ok=True)

    clipped_path = clip_image_with_shapefile(image, shapefile, output)
    logger.success(f"✅ Imagen recortada guardada en: {clipped_path}")

    return clipped_path


@app.command("indices")
def indices(
    image: Path = typer.Option(..., exists=True, help="Multiband .tif file"),
    output: Path = typer.Option("results", help="Output directory"),
    indices_list: Optional[List[str]] = typer.Option(
        None,
        help="List of indices to calculate (ndvi,ndre,savi). Calculates all by default.",
    ),
) -> Dict[str, Path]:
    """Calculates vegetation indices for a satellite image.

    Processes input image to generate requested vegetation indices following
    ISO 42001 calculation standards.

    Args:
        image: Path to multiband image file
        output: Directory to save results
        indices_list: Optional list of indices to calculate

    Returns:
        Dict[str, Path]: Dictionary mapping index names to result files
    """
    # Inicializar logging
    init_logging(Path(output))
    """
    Calcula índices vegetativos (NDVI, NDRE, SAVI) a partir de una imagen.
    """
    logger.info(f"🛰️ Procesando imagen: {image}")
    logger.info("📊 Calculando índices vegetativos")  # Removido f-string innecesario

    output.mkdir(parents=True, exist_ok=True)

    result_paths = calculate_all_indices(image, output)

    for index_name, path in result_paths.items():
        logger.success(f"✅ Índice {index_name.upper()} guardado en: {path}")

    return result_paths


@app.command("auto")
def auto_process(
    image: Path = typer.Option(..., exists=True, help="Multiband .tif file"),
    shapefile: Optional[Path] = typer.Option(
        None, exists=True, help="Optional .shp file"
    ),
    output: Path = typer.Option("results", help="Output directory"),
) -> Dict[str, Path]:
    """Processes an image automatically, optionally with clipping.

    Provides a complete processing pipeline including optional clipping and
    calculation of all vegetation indices.

    Args:
        image: Path to multiband image file
        shapefile: Optional path to clipping shapefile
        output: Directory to save results

    Returns:
        Dict[str, Path]: Dictionary mapping index names to result files
    """
    # Inicializar logging
    init_logging(Path(output))
    """
    Proceso automático: opcional recorte + cálculo de todos los índices.
    """
    logger.info(f"🚀 Iniciando procesamiento automático de {image}")

    output.mkdir(parents=True, exist_ok=True)

    # Paso 1: Recortar si se proporciona shapefile
    processed_image = image
    if shapefile:
        logger.info("✂️ Recortando imagen")
        logger.debug(f"Usando shapefile: {shapefile}")
        processed_image = clip_image_with_shapefile(
            image_path=image, shapefile_path=shapefile, output_path=output
        )  # Realizar recorte

    # Paso 2: Calcular índices
    logger.info("📊 Calculando índices vegetativos")
    result_paths = calculate_all_indices(processed_image, output)

    for index_name, path in result_paths.items():
        logger.success(f"✅ Índice {index_name.upper()} guardado en: {path}")

    logger.success(f"🏁 Procesamiento completo. Resultados en: {output}")
    return result_paths


def process_image(
    image_path: Path, output_dir: Path, indices: List[str], savi_l: float = 0.5
) -> Dict[str, Path]:
    """Main function for processing satellite imagery and calculating indices.

    Implements the core processing workflow according to ISO 42001 standards,
    including validation, calculation, and logging.

    Args:
        image_path: Path to multiband satellite image
        output_dir: Directory to save results
        indices: List of indices to calculate (ndvi, savi, ndre)
        savi_l: Adjustment factor for SAVI index

    Returns:
        Dictionary mapping index names to generated file paths
    """
    # Inicializar logging
    init_logging(output_dir)

    # Crear directorio de salida
    output_dir.mkdir(parents=True, exist_ok=True)

    # Procesar imagen y calcular índices
    logger.info(f"🛰️ Procesando imagen: {image_path}")
    logger.info(f"📊 Calculando índices: {', '.join(indices)}")

    result_paths = calculate_all_indices(image_path, output_dir)

    # Registrar resultados
    for index_name, path in result_paths.items():
        if index_name in indices:
            logger.success(f"✅ Índice {index_name.upper()} guardado en: {path}")

    # Filtrar solo los índices solicitados
    return {k: v for k, v in result_paths.items() if k in indices}


if __name__ == "__main__":
    app()
