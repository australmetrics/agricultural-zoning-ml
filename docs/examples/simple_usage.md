---
title: Simple Usage
nav_order: 5
-------------

# Simple Usage

<!-- TOC -->

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick CLI Example](#quick-cli-example)
3. [Inspecting Outputs](#inspecting-outputs)
4. [Minimal Python API Example](#minimal-python-api-example)
5. [ISO 42001 Compliance Enhancements](#iso-42001-compliance-enhancements)
6. [Pipeline Stages Overview](#pipeline-stages-overview)
7. [Troubleshooting Tips](#troubleshooting-tips)

---

## 1. Prerequisites

* **Python**: 3.11 or higher installed.
* **Installation**: Pascal Zoning ML installed (`pip install -e .` or via PyPI).
* **Input Data**: A clipped GeoTIFF with required bands or in-memory NumPy arrays of indices.
* **Environment**: Familiarity with terminal (bash, PowerShell) and Python scripting.
* **Audit Settings** (ISO 42001):

  * `export ZONING_AUDIT_LOGGING="true"` to enable JSON audit trail.
  * `export ZONING_SOFTWARE_VERSION="<version>"` to embed software version.
  * `export ZONING_SECURE_OUTPUT="true"` to enforce secure permissions on outputs.

---

## 2. Quick CLI Example

Run the zoning workflow with basic ISO validation:

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs/simple_run \
  --force-k 3 \
  --min-zone-size 0.5 \
  --max-zones 5 \
  --validate-system \
  --validate-model
```

**Flags explained:**

* `--raster`: Path to GeoTIFF.
* `--indices`: Comma-separated indices.
* `--output-dir`: Base folder for timestamped results.
* `--force-k`: (Optional) Fixed number of clusters.
* `--min-zone-size`: (Optional) Threshold for zone area (ha).
* `--max-zones`: (Optional) Max k when auto-selecting.
* `--validate-system`: Ensure system integrity (deps, config).
* `--validate-model`: Validate model artifacts (schema, weights).

---

## 3. Inspecting Outputs

After success, inspect:

```
./outputs/simple_run/YYYYMMDD_HHMMSS_k3_mz0.5/
```

Includes:

* `zonificacion_agricola.gpkg` — management zones
* `puntos_muestreo.gpkg` — sampling points
* `mapa_ndvi.png` — NDVI map
* `mapa_clusters.png` — cluster map
* `estadisticas_zonas.csv` — zone stats
* `metricas_clustering.json` — clustering metrics
* `zonificacion_results.png` — overview figure
* `audit_log.json` — audit trail for ISO 42001
* `manifest_zoning.json` — inputs, outputs, metadata including `software_version` and validation flags

---

## 4. Minimal Python API Example

```python
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from pascal_zoning.zoning import AgriculturalZoning

# Sample index arrays
datasets = {"NDVI": np.array([[0.1,0.2],[0.3,0.4]]),
            "NDRE": np.array([[0.0,0.1],[0.2,0.3]])}

# Field boundary
boundary = Polygon([(0,0),(2,0),(2,2),(0,2)])

# Instantiate engine with audit and validation enabled
zoning = AgriculturalZoning(
    random_state=42,
    min_zone_size_ha=0.0001,
    max_zones=3,
    output_dir=Path("./outputs/simple_api"),
    audit_logging=True,
    software_version="1.0.2",
    secure_output=True
)

# Run pipeline with validations
result = zoning.run_pipeline(
    indices=datasets,
    bounds=boundary,
    points_per_zone=2,
    crs="EPSG:32719",
    force_k=None,
    validate_system=True,
    validate_model=True
)

print(f"Zones: {result.metrics.n_clusters}, Silhouette: {result.metrics.silhouette:.3f}")
```

Outputs include audit log and manifest with ISO fields.

---

## 5. ISO 42001 Compliance Enhancements

* **Audit Trail**: All runs generate `audit_log.json` with timestamps, user, action, parameters, and outcomes.
* **Manifest Fields**: `manifest_zoning.json` includes:

  * `software_version` (env or config)
  * `validated_system`: true/false
  * `validated_model`: true/false
  * `audit_logging`: true/false
* **Secure Output**: Directories and files created with restricted permissions (e.g., `chmod 700`).
* **Traceability**: Input and output file paths recorded verbatim in manifest and audit.

---

## 6. Pipeline Stages Overview

1. `create_mask()` — valid pixel mask.
2. `prepare_features()` — assemble and standardize features.
3. `perform_clustering()` — K-Means++.
4. `extract_zones()` — polygonize clusters.
5. `filter_zones()` — remove small zones.
6. `compute_statistics()` — area, perimeter, stats.
7. `generate_samples()` — spatial sampling.
8. `save_results()`/`visualize()` — export all artifacts.

---

## 7. Troubleshooting Tips

* **No valid pixels**: Check CRS alignment and valid raster values.
* **Insufficient samples**: Reduce `--force-k` or `--max-zones`.
* **Empty zones**: Lower `--min-zone-size`.

---

© 2025 AustralMetrics SpA. All rights reserved.
