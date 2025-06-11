# Pascal Zoning ML — Functions Reference

**Version:** 1.0.2  |  **Owner:** AustralMetrics SpA  |  **ISO 42001 Compliant**

This document describes the architecture and public API of the `pascal_zoning` package, aligned with ISO 42001 standards for quality and security.

---

## Module Structure

```
src/
└── pascal_zoning/
    ├── __init__.py
    ├── config.py
    ├── interface.py
    ├── logging_config.py
    ├── pipeline.py
    ├── py.typed
    ├── viz.py
    └── zoning.py
```

---

## 1. Configuration (`config.py`)

### Function: `load_config(path: Path) -> Dict[str, Any]`

Loads and validates a YAML or JSON configuration file.

* **Parameters**:

  * `path`: Path to the configuration file.
* **Returns**:

  * Dictionary containing all parameters required to initialize the pipeline.
* **Validations**:

  * File existence and read permissions.
  * Required schema fields (`input_file`, `output_dir`, `k_clusters`, `min_zone_size`).
  * Audit log entries for traceability.

---

## 2. User Interface (`interface.py`)

### Function: `parse_args() -> argparse.Namespace`

Parses command-line arguments for CLI execution.

* **Main arguments**:

  * `--input-file`: Input raster file (GeoTIFF).
  * `--output-dir`: Output directory.
  * `--config`: Path to configuration file.
  * `--k-clusters`: Number of clusters.
  * `--min-zone-size`: Minimum zone size (hectares).
  * `--verbose`: Logging verbosity level.
* **Returns**:

  * Namespace with all parsed arguments.

---

## 3. Secure Logging (`logging_config.py`)

### Function: `setup_logging(output_dir: Path, level: str = "INFO") -> None`

Configures the structured logging system with rotation and backup.

* **Features**:

  * Structured JSON logs.
  * Automatic file rotation (RotatingFileHandler).
  * SHA-256 integrity verification of log files.
  * Audit trail preservation.

---

## 4. Main Pipeline (`pipeline.py`)

### Class: `PascalZoningPipeline`

Primary engine for agricultural zoning workflows.

```python
from src.pascal_zoning.pipeline import PascalZoningPipeline

pipeline = PascalZoningPipeline(
    input_file=Path("field.tif"),
    output_dir=Path("results"),
    k_clusters=3,
    min_zone_size=0.5,
)
```

#### Key Methods

* **`execute(progress_callback: Optional[Callable] = None) -> Dict[str, Any]`**

  * Runs the full workflow: preprocessing, clustering, and post-processing.
  * Returns quality metrics and paths to generated files.
  * Ensures ISO-42001 compliance at each step.

* **`prepare_features() -> np.ndarray`**

  * Builds a feature matrix from the raster input.
  * Validates data integrity and metadata consistency.

* **`perform_clustering(features: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]`**

  * Executes K-means clustering with parameter validation.
  * Returns zone labels and clustering metrics (silhouette score, inertia).

---

## 5. Index Calculation (`zoning.py`)

### Function: `calculate_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray`

Computes the NDVI (Normalized Difference Vegetation Index) with ISO compliance.

* **Validations**:

  * Matching array dimensions.
  * Enforced value range \[-1, 1].
  * Division-by-zero handling.

### Function: `calculate_savi(red: np.ndarray, nir: np.ndarray, l: float = 0.5) -> np.ndarray`

Computes the SAVI (Soil Adjusted Vegetation Index).

* **Parameters**:

  * `l`: Soil adjustment factor (0.0–1.0).

---

## 6. Visualization and Export (`viz.py`)

### Function: `create_zone_map(zones_gdf: geopandas.GeoDataFrame, output_path: Path, title: str = "Agricultural Zones") -> None`

Generates a professional map of agricultural zones.

* Utilizes Matplotlib and GeoPandas.
* Applies ISO-42001 styling (colors, labels, georeferencing).

### Function: `export_results(results: Dict[str, Any], output_dir: Path, format: str = "all") -> None`

Exports results in multiple formats.

* Supported formats: GeoPackage, JSON, PNG.
* Post-export checksum verification.

---

## 7. System Requirements

* **Python**: ≥ 3.8
* **Memory**: Minimum 8 GB RAM
* **Dependencies**:

  * rasterio
  * geopandas
  * scikit-learn
  * numpy
  * matplotlib

## Quality and Performance Metrics

* **Zoning accuracy**: ≥ 95%
* **Processing time**: < 2 minutes per 100 MB
* **Peak memory usage**: < 4 GB

---

© 2025 AustralMetrics SpA. All rights reserved.

```