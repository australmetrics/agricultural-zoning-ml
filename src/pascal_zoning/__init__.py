"""
PASCAL – Agri-Zoning Block
Paquete principal de zonificación agronómica.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:     # ejecución en editable / dev
    __version__ = "0.0.0-dev"

# API pública
from .zoning import (
    AgriculturalZoning,
    ZoningResult,
    ClusterMetrics,
    ZoneStats,
    ZonificationError,
    ValidationError,
    ProcessingError,
)
from .config import load_config, ZoningConfig
from .pipeline import ZoningPipeline

__all__ = [
    "AgriculturalZoning",
    "ZoningResult",
    "ClusterMetrics",
    "ZoneStats",
    "ZonificationError",
    "ValidationError",
    "ProcessingError",
    "load_config",
    "ZoningConfig",
    "ZoningPipeline",
]

