---
title: System Architecture
nav_order: 1
-------------

# System Architecture

<!-- TOC -->

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)

   * [Configuration Loader](#configuration-loader)
   * [CLI & Interface](#cli--interface)
   * [Secure Logging](#secure-logging)
   * [Pipeline Engine](#pipeline-engine)
   * [Index & Zoning Module](#index--zoning-module)
   * [Visualization & Export](#visualization--export)
3. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)

   * [Data Ingestion](#data-ingestion)
   * [Feature Extraction](#feature-extraction)
   * [Clustering & Zoning](#clustering--zoning)
   * [Post-Processing & Export](#post-processing--export)
4. [Interfaces](#interfaces)

   * [Command-Line Interface](#command-line-interface)
   * [Python API](#python-api)
   * [Event Hooks & Callbacks](#event-hooks--callbacks)
5. [Security & ISO 42001 Compliance](#security--iso-42001-compliance)

   * [Audit Trail](#audit-trail)
   * [Manifest & Traceability](#manifest--traceability)
   * [Validation Hooks](#validation-hooks)
   * [Secure Output Policies](#secure-output-policies)
6. [Scalability & Performance](#scalability--performance)

   * [Chunked Processing](#chunked-processing)
   * [Dimensionality Reduction (PCA)](#dimensionality-reduction-pca)
   * [Parallel & Distributed Execution](#parallel--distributed-execution)
   * [Hardware Recommendations](#hardware-recommendations)
7. [Monitoring, Logging & Alerting](#monitoring-logging--alerting)

   * [Operational Metrics](#operational-metrics)
   * [Loguru Configuration](#loguru-configuration)
   * [Automated Alerts](#automated-alerts)
8. [Design Patterns & Extensibility](#design-patterns--extensibility)

   * [Plugin Architecture](#plugin-architecture)
   * [Extension Points](#extension-points)
   * [Future Enhancements](#future-enhancements)
9. [Continuous Integration & Quality Control](#continuous-integration--quality-control)

   * [GitHub Actions Workflow](#github-actions-workflow)
   * [Unit & Integration Testing](#unit--integration-testing)
   * [Type Checking & Linting](#type-checking--linting)
10. [Deployment Patterns](#deployment-patterns)

    * [On-Premise Installation](#on-premise-installation)
    * [Containerization & Kubernetes](#containerization--kubernetes)
    * [Cloud Deployment](#cloud-deployment)
11. [Appendices](#appendices)

    * [A. Glossary](#a-glossary)
    * [B. External References](#b-external-references)

---

## Overview

The **Pascal Zoning ML** system ([https://github.com/australmetrics/agricultural-zoning-ml](https://github.com/australmetrics/agricultural-zoning-ml)) provides a robust, ISO 42001-compliant architecture for agricultural field zonification based on multispectral imagery. Its modular design addresses:

* **High-volume data ingestion** from satellite and drone sources.
* **Automated feature extraction** via industry-standard vegetation indices.
* **Adaptive zoning** using clustering algorithms optimized for spatial data.
* **End-to-end traceability**, auditability, and compliance with international standards.
* **Interoperability** through CLI, Python API, and manifest-driven workflows.

Designed for research, enterprise, and field operations, the system balances flexibility, performance, and regulatory adherence.

---

## Core Components

### Configuration Loader

* **File:** `src/pascal_zoning/config.py`
* **Class/Function:** `load_config(path: Path) -> ZoningConfig`
* **Responsibilities:**

  * Parse YAML/JSON configuration files with pydantic validation.
  * Merge defaults from environment variables and CLI flags.
  * Enforce schema contract: required fields (`input_file`, `indices`, `output_dir`, `min_zone_size_ha`).
  * Provide structured `ZoningConfig` object to downstream modules.

### CLI & Interface

* **File:** `src/pascal_zoning/interface.py`
* **Library:** Typer for CLI parsing.
* **Commands:**

  * `run`: executes full pipeline with options:

    * `--raster`, `--indices`, `--output-dir`, `--force-k`, `--min-zone-size`, `--max-zones`.
    * Audit flags: `--validate-system`, `--validate-model`, `--save-intermediates`.
    * Logging overrides: `--log-file`, `--log-level`.
    * Dimensionality reduction: `--use-pca`, `--pca-variance`.

### Secure Logging

* **File:** `src/pascal_zoning/logging_config.py`
* **Function:** `setup_logging(output_dir: Path, level: str)`
* **Features:**

  * JSON-structured logs with rotating handlers.
  * SHA-256 integrity verification of log files.
  * Configurable retention and backup policies for audit compliance.

### Pipeline Engine

* **File:** `src/pascal_zoning/pipeline.py`
* **Class:** `PascalZoningPipeline`
* **Key Methods:**

  * `execute(...)`: orchestrates end-to-end process.
  * `validate_system()`: checks dependencies, file formats, config schema.
  * `validate_model()`: verifies model artifacts and weights.
  * Emits `manifest_zoning.json` and `audit_log.json`.

### Index & Zoning Module

* **File:** `src/pascal_zoning/zoning.py`
* **Functions:**

  * `calculate_ndvi()`, `calculate_savi()`, `calculate_ndwi()`, `calculate_ndre()`
* **Class:** `AgriculturalZoning`

  * Methods: `run_pipeline()`, `create_mask()`, `prepare_feature_matrix()`,
    `perform_clustering()`, `extract_zones()`, `filter_small_zones()`,
    `compute_zone_statistics()`, `generate_sampling_points()`, `save_intermediates()`.

### Visualization & Export

* **File:** `src/pascal_zoning/viz.py`
* **Functions:** `create_zone_map()`, `export_results()`
* **Capabilities:**

  * Generates GeoPackage (.gpkg) with geospatial attributes.
  * Exports CSV, JSON, and PNG artifacts.
  * Applies ISO-compliant styling: standardized color palettes, metadata tags, georeferencing.

---

## Data Flow & Processing Pipeline

### Data Ingestion

1. **Raster Clipping**: `clip_raster(image_path, shapefile)` uses geopandas and rasterio to subset imagery.
2. **Mask Generation**: `create_mask(bounds, raster)` builds boolean mask for valid data.
3. **Input Validation**: checks CRS compatibility, band count, and file integrity.

### Feature Extraction

1. **Index Computation**: high-performance NumPy vectorization for indices.
2. **Mask Application**: isolate valid pixels.
3. **Feature Matrix**: reshape \[H×W×N] to \[Pixels×Indices], with Imputation and StandardScaler.

### Clustering & Zoning

1. **Parameter Validation**: ensure k\_clusters or range are valid.
2. **Automatic k-selection**: evaluates silhouette and Calinski-Harabasz.
3. **K-Means++**: via scikit-learn with optimized initialization.
4. **Polygonization**: convert labeled pixels to shapely polygons and dissolve contiguous areas.
5. **Small Zone Filtering**: remove areas below threshold and reassign zone IDs.

### Post-Processing & Export

1. **Statistics Computation**: area, perimeter, compactness, per-index mean/std.
2. **Sampling Points**: stratified spatial sampling with minimum distance constraint.
3. **Result Packaging**: writes GeoPackage, CSV, JSON metrics, and composite PNG maps.
4. **Traceability Artifacts**: generate `manifest_zoning.json` and `audit_log.json`.

---

## Interfaces

### Command-Line Interface

```bash
python -m pascal_zoning.pipeline run \
  --raster inputs/field.tif \
  --indices NDVI,NDRE \
  --output-dir results/ \
  --validate-system \
  --validate-model
```

* **Help**: `--help` displays full options.

### Python API

```python
from pascal_zoning.config import ZoningConfig
from pascal_zoning.zoning import AgriculturalZoning

cfg = ZoningConfig.from_yaml("config.yaml")
az = AgriculturalZoning.from_config(cfg)
res = az.run_pipeline(indices=my_indices, bounds=my_polygon)
```

* Returns `ZoningResult` dataclass with `zones`, `samples`, `metrics`, `stats`.

### Event Hooks & Callbacks

```python
def on_progress(step, percent): print(step, percent)

def on_complete(result): print("Done", result)

az.add_progress_listener(on_progress)
az.add_completion_listener(on_complete)
az.run_pipeline(...)
```

---

## Security & ISO 42001 Compliance

### Audit Trail

* `audit_log.json` captures:

  * `timestamp`, `user`, `action`, `input_files`, `parameters`, `exit_code`.

### Manifest & Traceability

* `manifest_zoning.json` includes:

  * `software_version`, `git_sha`, `timestamp`, `inputs`, `outputs`, `validated_system`, `validated_model`, `audit_logging`.
* Validate against `schemas/zoning_output.schema.json`.

### Validation Hooks

* CLI flags: `--validate-system`, `--validate-model`.
* Programmatic checks via `pipeline.validate_system()`, `pipeline.validate_model()`.

### Secure Output Policies

* Files and directories created with `chmod 700`.
* Sensitive files (`.env`, logs) with `chmod 600`.

---

## Scalability & Performance

### Chunked Processing

* `process_in_chunks(raster, chunk_size)` to limit memory footprint.

### Dimensionality Reduction (PCA)

* Optional `--use-pca --pca-variance` to reduce features.

### Parallel & Distributed Execution

* Batch scripts use Python `ProcessPoolExecutor`.
* Future support for Dask and Kubernetes.

### Hardware Recommendations

| Tier        | CPU            | RAM    | Disk      |
| ----------- | -------------- | ------ | --------- |
| Minimum     | 2 cores 2.0GHz | 8 GB   | SSD 20GB  |
| Recommended | 4 cores 3.0GHz | 16 GB  | SSD 50GB  |
| Enterprise  | 8+ cores       | 32 GB+ | SSD 200GB |

---

## Monitoring, Logging & Alerting

### Operational Metrics

* Real-time tracking: memory, CPU, processing time via custom middleware.

### Loguru Configuration

```python
logger.add(sys.stderr, level="$ZONING_LOG_LEVEL")
logger.add(f"{output_dir}/logs/run_{timestamp}.log", rotation="10 MB", retention="30 days")
```

### Automated Alerts

* Integrate with Slack or email for critical errors.
* Threshold-based alerts on resource usage.

---

## Design Patterns & Extensibility

### Plugin Architecture

* Define `IndicesPlugin` protocol for custom index implementations.
* Register via entry points for dynamic discovery.

### Extension Points

1. New vegetation indices in `zoning.calculate_*`.
2. Alternative clustering algorithms via strategy pattern.
3. Additional export formats (e.g., Shapefile, TIFF) in `viz.export_results()`.

### Future Enhancements

* REST API microservice for on-demand processing.
* Integration with workflow managers (Airflow, Prefect).
* Container-native deployment with Helm charts.

---

## Continuous Integration & Quality Control

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    steps: [checkout, black --check, flake8]
  typecheck:
    steps: [checkout, mypy, pyright]
  test:
    steps: [checkout, pytest tests/]
```

* Enforces style, typing, and test coverage.

---

## Deployment Patterns

### On-Premise Installation

1. Clone repo
2. Create Python venv
3. `pip install -r requirements.txt`
4. Configure `.env` and directories
5. Run `pipeline --validate-system`

### Containerization & Kubernetes

* Dockerfile provided under `docker/`.
* Helm chart for k8s deployment with ConfigMap and Secret for `.env`.

### Cloud Deployment

* Terraform modules for AWS S3 + ECS
* Azure ARM templates for Blob Storage + AKS
* GCP Deployment Manager for Cloud Storage + GKE

---

## Appendices

### A. Glossary

* **Zone**: contiguous area representing a management unit.
* **Run ID**: unique UUID per execution.
* **Manifest**: JSON file capturing run metadata.

### B. External References

* **Repository:** [https://github.com/australmetrics/agricultural-zoning-ml](https://github.com/australmetrics/agricultural-zoning-ml)
* **ISO 42001:** AI Management Systems Standard
* **OGC GeoPackage Specification**
* **GDAL & Rasterio Documentation**

---

© 2025 AustralMetrics SpA. All rights reserved.
