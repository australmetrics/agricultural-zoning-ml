"""PASCAL NDVI Block - Vegetation index calculation module."""

from .main import process_image
from .indices import (
    calculate_ndvi,
    calculate_savi,
    calculate_ndre,
    calculate_all_indices,
)
from .preprocessor import clip_image_with_shapefile
from .config import get_config
from .logging_config import setup_logging

__version__ = "1.0.0"
__author__ = "AustralMetrics SpA"
__license__ = "Propietario"

__all__ = [
    "process_image",
    "calculate_ndvi",
    "calculate_savi",
    "calculate_ndre",
    "calculate_all_indices",
    "clip_image_with_shapefile",
    "get_config",
    "setup_logging",
]
