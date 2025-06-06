"""
Configuración del Sistema de Zonificación Agronómica
Implementa configuraciones siguiendo ISO 42001 para sistemas de IA responsables.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ClusteringMethod(Enum):
    """Métodos de clustering disponibles."""

    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"
    GAUSSIAN_MIXTURE = "gaussian_mixture"


class ValidationStrategy(Enum):
    """Estrategias de validación."""

    CROSS_VALIDATION = "cross_validation"
    HOLDOUT = "holdout"
    BOOTSTRAP = "bootstrap"


@dataclass
class ModelConfig:
    """
    Configuración de modelos de ML siguiendo ISO 42001.

    Incluye parámetros para reproducibilidad, validación y monitoreo.
    """

    # Parámetros de clustering
    clustering_method: ClusteringMethod = ClusteringMethod.KMEANS
    max_clusters: int = 15
    min_cluster_size: int = 100
    random_state: int = 42

    # Parámetros de PCA
    use_pca: bool = True
    variance_ratio: float = 0.95
    max_components: Optional[int] = None

    # Parámetros de preprocesamiento
    imputation_strategy: str = "median"
    scaling_method: str = "standard"
    outlier_detection: bool = True
    outlier_threshold: float = 3.0

    # Métricas de evaluación
    evaluation_metrics: List[str] = field(
        default_factory=lambda: [
            "silhouette_score",
            "calinski_harabasz_score",
            "davies_bouldin_score",
        ]
    )

    # Control de calidad ISO 42001
    min_silhouette_score: float = 0.3
    max_inertia_ratio: float = 0.8
    stability_threshold: float = 0.85

    def validate(self) -> bool:
        """Valida la configuración del modelo."""
        if self.max_clusters < 2:
            raise ValueError("max_clusters debe ser >= 2")

        if not 0 < self.variance_ratio <= 1:
            raise ValueError("variance_ratio debe estar en (0, 1]")

        if self.min_silhouette_score < 0:
            raise ValueError("min_silhouette_score debe ser >= 0")

        return True


@dataclass
class ValidationConfig:
    """
    Configuración de validación siguiendo ISO 42001.

    Define criterios de calidad y validación para el sistema.
    """

    # Validación de entrada
    spectral_index_range: Tuple[float, float] = (-1.0, 1.0)
    min_valid_pixels_ratio: float = 0.7
    max_nan_ratio: float = 0.3

    # Validación geoespacial
    min_zone_area_ha: float = 0.5
    max_zone_area_ha: float = 1000.0
    min_compactness: float = 0.1
    max_perimeter_area_ratio: float = 0.5

    # Validación de muestreo
    min_points_per_zone: int = 5
    max_points_per_zone: int = 50
    min_distance_between_points: float = 50.0

    # Criterios de calidad
    validation_strategy: ValidationStrategy = ValidationStrategy.CROSS_VALIDATION
    cv_folds: int = 5
    test_size: float = 0.2

    # Umbrales de aceptación
    min_model_accuracy: float = 0.75
    max_processing_time_minutes: int = 30

    def validate_spectral_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos espectrales de entrada."""
        for name, values in data.items():
            # Verificar rango
            min_val, max_val = self.spectral_index_range
            if values.min() < min_val or values.max() > max_val:
                logger.warning(f"Índice {name} fuera de rango esperado")

            # Verificar NaN ratio
            nan_ratio = values.isna().sum() / len(values)
            if nan_ratio > self.max_nan_ratio:
                raise ValueError(f"Demasiados NaN en {name}: {nan_ratio:.2%}")

        return True


@dataclass
class ZoningConfig:
    """
    Configuración principal del sistema de zonificación.

    Integra todas las configuraciones siguiendo ISO 42001.
    """

    # Metadatos del proyecto
    project_name: str = "Zonificación Agronómica"
    project_version: str = "1.0.0"
    created_by: str = "Agricultural Zoning System"

    # Configuración de zonificación
    random_state: int = 42
    min_zone_size_ha: float = 0.5
    max_zones: int = 15
    min_points_per_zone: int = 5

    # Configuraciones de subsistemas
    model: ModelConfig = field(default_factory=ModelConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)

    # Configuración de procesamiento
    parallel_processing: bool = True
    n_jobs: int = -1
    memory_limit_gb: float = 8.0
    temp_dir: Optional[Path] = None

    # Configuración de salida
    output_formats: List[str] = field(
        default_factory=lambda: ["gpkg", "geojson", "shapefile"]
    )
    create_visualizations: bool = True
    save_intermediate_results: bool = False

    # Logging y monitoreo
    log_level: str = "INFO"
    enable_profiling: bool = False
    save_metrics: bool = True

    # Cumplimiento ISO 42001
    data_governance: Dict[str, Any] = field(
        default_factory=lambda: {
            "data_retention_days": 365,
            "audit_trail": True,
            "version_control": True,
            "access_control": True,
        }
    )

    risk_management: Dict[str, Any] = field(
        default_factory=lambda: {
            "bias_detection": True,
            "fairness_metrics": True,
            "robustness_testing": True,
            "uncertainty_quantification": True,
        }
    )

    def validate_all(self) -> bool:
        """Valida toda la configuración."""
        self.model.validate()

        # Validar configuración de zonificación
        if self.min_zone_size_ha <= 0:
            raise ValueError("min_zone_size_ha debe ser > 0")
        if self.max_zones < 2:
            raise ValueError("max_zones debe ser >= 2")
        if self.min_points_per_zone < 1:
            raise ValueError("min_points_per_zone debe ser >= 1")

        # Validar configuración de sistema
        if self.memory_limit_gb <= 0:
            raise ValueError("memory_limit_gb debe ser > 0")
        if self.n_jobs < -1 or self.n_jobs == 0:
            raise ValueError("n_jobs debe ser -1 o > 0")

        return True

    @classmethod
    def from_file(cls, config_path: Path) -> "ZoningConfig":
        """Carga configuración desde archivo JSON."""
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convertir enums
        if "model" in data:
            model_data = data["model"]
            if "clustering_method" in model_data:
                model_data["clustering_method"] = ClusteringMethod(
                    model_data["clustering_method"]
                )

        if "validation" in data:
            val_data = data["validation"]
            if "validation_strategy" in val_data:
                val_data["validation_strategy"] = ValidationStrategy(
                    val_data["validation_strategy"]
                )

        return cls(**data)

    def to_file(self, config_path: Path) -> None:
        """Guarda configuración en archivo JSON."""
        data = self.__dict__.copy()

        # Convertir enums a strings
        if hasattr(data.get("model"), "clustering_method"):
            data["model"].clustering_method = data["model"].clustering_method.value

        if hasattr(data.get("validation"), "validation_strategy"):
            data["validation"].validation_strategy = data[
                "validation"
            ].validation_strategy.value

        # Convertir Paths a strings
        if data.get("temp_dir"):
            data["temp_dir"] = str(data["temp_dir"])

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Configuración por defecto
DEFAULT_CONFIG = ZoningConfig()


def get_default_config() -> ZoningConfig:
    """Retorna configuración por defecto."""
    return DEFAULT_CONFIG


def load_config(config_path: Optional[Path] = None) -> ZoningConfig:
    """
    Carga configuración desde archivo o retorna la por defecto.

    Args:
        config_path: Ruta al archivo de configuración

    Returns:
        Configuración cargada
    """
    if config_path and config_path.exists():
        logger.info(f"Cargando configuración desde {config_path}")
        return ZoningConfig.from_file(config_path)
    else:
        logger.info("Usando configuración por defecto")
        return get_default_config()
