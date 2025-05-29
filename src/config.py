"""Global configuration for PASCAL NDVI Block.

Includes safe default values and system constants following ISO 42001 guidelines
for configuration management and security.
"""

from pathlib import Path
from typing import Dict, Any

# Directorios por defecto
DEFAULT_OUTPUT_DIR = Path("results")
DEFAULT_DATA_DIR = Path("data")
DEFAULT_LOG_DIR = DEFAULT_OUTPUT_DIR / "logs"
DEFAULT_BACKUP_DIR = DEFAULT_LOG_DIR / "backup"

# Parámetros de índices vegetativos
VALID_INDICES = ["ndvi", "savi", "ndre"]
DEFAULT_SAVI_L = 0.5  # Factor L por defecto para SAVI
VALID_L_RANGE = (0.0, 1.0)  # Rango válido para factor L

# Límites de seguridad
MAX_IMAGE_SIZE_GB = 10.0
MAX_CLOUD_COVERAGE = 50.0  # Porcentaje máximo de nubes permitido

# Configuración de logging
LOG_RETENTION_DAYS = 90
LOG_FORMAT = "[{time:YYYY-MM-DD HH:mm:ss.SSS}] {level: <8} | {message}"

# Tipos de imágenes soportadas
SUPPORTED_SATELLITES = {
    "sentinel2": {"red_band": "B04", "nir_band": "B08", "resolution": 10},
    "landsat8": {"red_band": "B4", "nir_band": "B5", "resolution": 30},
}


def get_config() -> Dict[str, Any]:
    """Retorna la configuración actual del sistema.

    Contiene toda la configuración necesaria para el funcionamiento del sistema,
    incluyendo directorios, parámetros de índices y configuración de satélites.

    Returns:
        Dict[str, Any]: Diccionario con la configuración actual.
    """
    return {
        "output_dir": DEFAULT_OUTPUT_DIR,
        "data_dir": DEFAULT_DATA_DIR,
        "log_dir": DEFAULT_LOG_DIR,
        "backup_dir": DEFAULT_BACKUP_DIR,
        "indices": {
            "ndvi": {"enabled": True},
            "ndre": {"enabled": True},
            "savi": {
                "enabled": True,
                "l_factor": DEFAULT_SAVI_L,
                "l_range": VALID_L_RANGE,
            },
        },
        "satellites": SUPPORTED_SATELLITES,
        "max_image_size": MAX_IMAGE_SIZE_GB,
        "max_cloud_coverage": MAX_CLOUD_COVERAGE,
        "log_retention": LOG_RETENTION_DAYS,
    }
