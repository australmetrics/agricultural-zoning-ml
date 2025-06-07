"""Paquete principal de pascal_zoning.

Este paquete expone la API principal para zonificación agronómica,
incluyendo clases para configuración, pipeline y resultados.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # ejecución en editable / dev
    __version__ = "0.0.0-dev"

# API pública
__all__ = [
    "AgriculturalZoning",
    "ZoningResult",
    "ClusterMetrics",
    "ZoneStats",
    "ZonificationError",
    "ValidationError",
    "ProcessingError",
    "NDVIBlockInterface",
    "load_config",
    "ZoningConfig",
    "ZoningPipeline",
]

from .zoning import (
    AgriculturalZoning,
    ZoningResult,
    ClusterMetrics,
    ZoneStats,
    ZonificationError,
    ValidationError,
    ProcessingError,
)
from .interface import NDVIBlockInterface
from .config import load_config, ZoningConfig
from .pipeline import ZoningPipeline
