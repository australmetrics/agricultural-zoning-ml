---
title: API Documentation
nav_order: 4
-------------

# API Documentation

This document describes the public Python API of **Pascal Zoning ML**. It is aimed at developers who need to integrate, extend, or automate zoning workflows in their own applications, with ISO 42001 traceability built‑in.

## Contents

1. [Getting Started](#getting-started)
2. [Package Structure](#package-structure)
3. [Core Classes & Methods](#core-classes--methods)
4. [Data Classes & Return Types](#data-classes--return-types)
5. [Configuration & Overrides](#configuration--overrides)
6. [Logging & Traceability](#logging--traceability)
7. [Exceptions](#exceptions)
8. [CLI Integration (pipeline)](#cli-integration-pipeline)
9. [Extension Points](#extension-points)
10. [ISO 42001 Compliance Notes](#iso-42001-compliance-notes)

---

## Getting Started

```bash
pip install pascal-zoning
```

Or, for development:

```bash
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml
pip install -e .
```

### Verify Installation & Import

In a Python REPL or script:

```python
import pascal_zoning
print(pascal_zoning.__version__)
```

Or via command line:

```bash
python -c "import pascal_zoning; print(pascal_zoning.__version__)"
```

## Package Structure

```
src/pascal_zoning/
├── __init__.py        # Public API exports
├── zoning.py          # Core pipeline: mask, preprocessing, clustering, sampling, stats, export
├── pipeline.py        # CLI entrypoint (Typer)
├── config.py          # YAML/env config loader
├── logging_config.py  # Loguru setup
├── interface.py       # Typed interfaces & validation helpers
└── viz.py             # Visualization utilities
```

Support files: `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, etc.

## Core Classes & Methods

### `AgriculturalZoning`

Main engine for zoning workflows.

```python
from pascal_zoning.zoning import AgriculturalZoning
# Instantiate
az = AgriculturalZoning(
    random_state=42,
    min_zone_size_ha=0.1,
    max_zones=8,
    output_dir="outputs"
)

# Run full pipeline
result = az.run_pipeline(
    indices_dir="indices/",
    bounds=field_polygon,        # Shapely Polygon
    points_per_zone=10,
    crs="EPSG:4326",
    force_k=None,
    use_pca=True
)
```

#### Key methods:

* `create_mask(bounds: Polygon, indices: Dict[str, np.ndarray]) -> None`
  Masks the input polygon based on indices and assigns the resulting mask for downstream processing.
* `prepare_feature_matrix() -> None`
  Builds the feature matrix by stacking, imputing, and scaling indices in preparation for clustering.
* `select_optimal_clusters() -> int`
  Determines the optimal number of clusters using Silhouette and Calinski-Harabasz metrics and returns the chosen k.
* `perform_clustering(force_k: Optional[int]) -> None`
  Executes k-means clustering on the feature matrix, optionally forcing a specific number of clusters.
* `extract_zone_polygons() -> None`
  Converts cluster labels into vector polygons representing each management zone.
* `filter_small_zones() -> None`
  Removes zones below the configured minimum area threshold to avoid noise.
* `generate_sampling_points(n: int) -> None`
  Generates stratified sampling points within each zone using a spatial inhibition algorithm.
* `compute_zone_statistics() -> None`
  Calculates per-zone metrics (area, perimeter, compactness, mean and standard deviation of indices).
* `save_results(output_dir: Optional[Path]) -> None`
  Exports zones, sampling points, metrics, and metadata to the specified output directory.
* `visualize_results() -> None`
  Creates visual summaries (PNG maps and charts) of zoning results.

## Data Classes & Return Types & Return Types

### `ZoningResult`

Returned by `run_pipeline()`, bundling outputs:

```python
class ZoningResult:
    zones: geopandas.GeoDataFrame
    samples: geopandas.GeoDataFrame
    metrics: ClusterMetrics
    stats: List[ZoneStats]
```

### `ClusterMetrics`

Holds clustering summary:

* `n_clusters: int`
* `silhouette: float`
* `calinski_harabasz: float`
* `inertia: float`
* `cluster_sizes: Dict[int,int]`
* `timestamp: str`

### `ZoneStats`

Per-zone metrics:

* `zone_id: int`
* `area_ha: float`
* `perimeter_m: float`
* `compactness: float`
* `mean_values: Dict[str,float]`
* `std_values: Dict[str,float]`

## Configuration & Overrides

The `config.py` module loads values in the following priority order:

1. **YAML file** specified via `--config` flag
2. **`config.yaml`** in the current working directory
3. **Environment variables** prefixed with `ZONING_` (e.g., `ZONING_MAX_ZONES`)
4. **CLI flags** (highest priority)

### Example `config.yaml`

```yaml
# config.yaml
min_zone_size_ha: 0.05      # Minimum zone area in hectares
max_zones: 8                # Maximum number of clusters (zones)
random_state: 42            # Seed for reproducibility
output_dir: "./outputs"    # Directory for saving outputs
use_pca: true               # Enable PCA for feature reduction
```

### Override Precedence in Practice

* **Environment Variable** override (skips YAML):

  ```bash
  export ZONING_MAX_ZONES=10
  ```
* **CLI Flag** override (skips both YAML and env):

  ```bash
  pascal-zoning zoning \
    --config config.yaml \
    --max-zones 12
  ```

Use the loader in code as follows:

```python
from pascal_zoning.config import load_config
cfg = load_config(Path("config.yaml"))
```

## Logging & Traceability

Configuration in `logging_config.py` ensures all steps are logged with timestamps, levels, and module context. Enable debug via:

```bash
export ZONING_LOG_LEVEL=DEBUG
```

Logs written to console and, if configured, file sinks.

## Exceptions

All custom exceptions are defined in `pascal_zoning/exceptions.py`, importable via:

```python
import pascal_zoning.exceptions as exc
```

This module contains:

```python
class ZonificationError(Exception): pass
class ValidationError(ZonificationError): pass
class ProcessingError(ZonificationError): pass
```

For detailed function and exception references, see the [Exceptions Module](../technical/functions_reference.md#exceptions).

```python
class ZonificationError(Exception):
    """Base exception for zoning errors."""
    pass

class ValidationError(ZonificationError):
    """Raised when input validation fails."""
    pass

class ProcessingError(ZonificationError):
    """Raised on runtime processing errors."""
    pass
```

Catch these exceptions to differentiate between user errors (invalid inputs) and runtime failures (processing issues).

## CLI Integration (pipeline)

The Typer-based CLI provides three primary commands for end-to-end workflows:

| Command                 | Description                                    | Example                                                                                   |
| ----------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `pascal-zoning indices` | Compute vegetation indices (NDVI, NDRE, SAVI)  | `pascal-zoning indices --input image.tif --output-dir indices/ --overwrite`               |
| `pascal-zoning zoning`  | Generate management zones and sampling points  | `pascal-zoning zoning --indices-dir indices/ --output-dir zonation/ --points-per-zone 10` |
| `pascal-zoning run`     | Single-command pipeline for indices and zoning | `pascal-zoning run --input image.tif --output-dir out/ --points-per-zone 5`               |

This pipeline is implemented in the `run` command, which wraps `AgriculturalZoning.run_pipeline()` with:

* Argument parsing and validation via Typer
* Configuration loading (YAML, env vars, CLI flags)
* Structured logging and exit codes

Use `pascal-zoning --help` for full flag list.

## Extension Points

* **Custom Clustering**: subclass `AgriculturalZoning` to override clustering behavior. Example:

  ```python
  from pascal_zoning.zoning import AgriculturalZoning

  class CustomClustering(AgriculturalZoning):
      def select_optimal_clusters(self) -> int:
          # Implement custom k-selection logic (e.g., elbow method)
          return 5
  ```

* **Visualization**: import and call utilities in `viz.py` with custom GeoDataFrames:

  ```python
  from pascal_zoning.viz import zoning_overview
  zoning_overview(custom_zones, output_path="custom_map.png")
  ```

* **Index Calculation**: bypass the built-in indices step and supply precomputed arrays to the pipeline.

## ISO 42001 Compliance Notes

* For the full compliance specification, see the [ISO 42001 Compliance Statement](../compliance/iso42001_compliance.md).

* All public methods and pipeline steps log parameters and timestamps (traceability).

* `save_results()` writes a `metadata.json` with version, timestamp, parameters, and inputs.

* Exceptions and non-conformities are logged and surfaced via custom exception types.

* Reproducible runs ensured by `random_state` and pinned dependency versions, with output conformity validated against `schemas/manifest.schema.json` via `jsonschema -i metadata.json schemas/manifest.schema.json`.

---

*For advanced examples, see `docs/advanced_examples.md` and review the `schemas/metadata.schema.json` for the exact metadata.json format (fields: version, timestamp, parameters, inputs). For detailed class references, consult source docstrings.*
