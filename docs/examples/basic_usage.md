---
title: Basic Usage
nav_order: 6
-------------

# Basic Usage

<!-- TOC -->

## Table of Contents

1. [Environment Variables & Configuration File](#environment-variables--configuration-file)
2. [Command-Line Interface (CLI) Examples](#command-line-interface-cli-examples)
3. [Saving Intermediate Artifacts](#saving-intermediate-artifacts)
4. [Python API Examples](#python-api-examples)
5. [Common Advanced Options](#common-advanced-options)
6. [Input/Output Manifest](#inputoutput-manifest)
7. [System & Model Validation](#system--model-validation)
8. [Summary](#summary)

---

## 1. Environment Variables & Configuration File

Pascal Zoning ML supports default settings via environment variables and an optional `config.yaml`. The precedence order is:

1. **CLI flags**
2. **Configuration file**
3. **Environment variables**

### 1.1 Environment Variables

Set these in your shell before running the CLI or Python API:

```bash
# Default logging level (DEBUG, INFO, WARNING, ERROR)
export ZONING_LOG_LEVEL="DEBUG"

# Default output directory (if --output-dir is omitted)
export ZONING_OUTPUT_DIR="/path/to/outputs"

# Maximum memory in GB
export ZONING_MAX_MEMORY_GB="16"

# Enable ISO 42001 audit logging (JSON audit trail)
export ZONING_AUDIT_LOGGING="true"

# Embed software version in audit entries
export ZONING_SOFTWARE_VERSION="1.0.2"

# Enforce secure output permissions
export ZONING_SECURE_OUTPUT="true"
```

### 1.2 config.yaml

Create `config.yaml` in your project root with this structure:

```yaml
zoning:
  random_state: 123
  min_zone_size_ha: 0.2
  max_zones: 8
  use_pca: true

sampling:
  points_per_zone: 5
  min_distance_m: 10.0

i/o:
  default_output_dir: "./outputs/from_config"
```

Invoke the CLI with the `--config` flag to apply these defaults:

```bash
python -m pascal_zoning.pipeline run \
  --config config.yaml \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDRE
```

---

## 2. Command-Line Interface (CLI) Examples

### 2.1 Using config.yaml with flags and validation overrides

```bash
python -m pascal_zoning.pipeline run \
  --config config.yaml \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDRE \
  --force-k 4 \
  --output-dir ./outputs/cli_basic \
  --validate-system \
  --validate-model
```

* Loads defaults from `config.yaml`.
* Overrides indices, forced k, output directory.
* Runs system and model validation before execution.

### 2.2 Using only environment variables with validation

```bash
export ZONING_OUTPUT_DIR="./outputs/env_basic"
export ZONING_LOG_LEVEL="INFO"
export ZONING_AUDIT_LOGGING="true"

python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --max-zones 6 \
  --validate-system
```

* Uses `$ZONING_OUTPUT_DIR` for outputs.
* Logging set to INFO.
* Audit logging enabled.
* Validates system integrity before clustering.

---

## 3. Saving Intermediate Artifacts

To preserve intermediate files (mask, feature matrix, raw clusters):

```bash
export ZONING_SAVE_INTERMEDIATES="true"

python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI \
  --output-dir ./outputs/intermediates_example \
  --validate-system
```

Inside the timestamped folder, you will find:

```
<timestamped_folder>/
├── intermediate/
│   ├── valid_mask.npy
│   ├── feature_matrix.npy
│   ├── cluster_labels.npy
│   └── raw_zones.geojson
├── zonificacion_agricola.gpkg
├── puntos_muestreo.gpkg
... (final outputs) ...
```

---

## 4. Python API Examples

```python
from pathlib import Path
import numpy as np
import geopandas as gpd
from pascal_zoning.zoning import AgriculturalZoning

# Load precomputed index arrays
datasets = {
    "NDVI": np.load("data/ndvi.npy"),
    "NDWI": np.load("data/ndwi.npy"),
    "NDRE": np.load("data/ndre.npy"),
    "SI":   np.load("data/si.npy")
}

# Load field boundary
gdf = gpd.read_file("data/field_boundary.gpkg")
boundary = gdf.geometry.iloc[0]

# Instantiate the engine with PCA and a fixed seed
zoning = AgriculturalZoning(
    random_state=2023,
    min_zone_size_ha=0.1,
    max_zones=5,
    output_dir=Path("outputs/api_basic")
)

# Run with custom sampling, PCA, and validation
result = zoning.run_pipeline(
    indices=datasets,
    bounds=boundary,
    points_per_zone=10,
    crs="EPSG:32719",
    use_pca=True,
    validate_system=True,
    validate_model=True
)

print(f"Selected k: {result.metrics.n_clusters}")
```

---

## 5. Common Advanced Options

### 5.1 Adjusting PCA variance

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --pca-variance 0.90 \
  --validate-model
```

### 5.2 Logging to a file with secure output

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs/logging_example \
  --log-file ./outputs/logging_example/run.log
```

Combine with:

```bash
export ZONING_SECURE_OUTPUT="true"
```

---

## 6. Input/Output Manifest

Pascal Zoning ML will generate a JSON manifest (`manifest_zoning.json`) inside the run folder, containing:

* **Inputs**: raster path, indices list, parameters.
* **Outputs**: file names and paths.
* **Metadata**: timestamp, software\_version, processing time.
* **Audit**: flags indicating which validations ran.

Example schema:

```json
{
  "name": "pascal-zoning-ml",
  "version": "1.0.2",
  "timestamp": "2025-06-04T15:23:10Z",
  "software_version": "1.0.2",
  "interfaces": { ... },
  "metadata": { ... },
  "audit": {
    "validated_system": true,
    "validated_model": true
  }
}
```

---

## 7. System & Model Validation

Always include validation steps to ensure ISO 42001 compliance:

```bash
# System integrity checks (dependencies, config)
python -m pascal_zoning.pipeline --validate-system

# Model consistency checks (schema, weights)
python -m pascal_zoning.pipeline --validate-model
```

These commands perform input/output schema validation, dependency verification, and model artifact consistency checks.

---

## 8. Summary

This guide extends basic usage by adding ISO 42001–compliant audit and validation controls, secure output enforcement, and updated manifest contents. It ensures end-to-end traceability and system integrity for all runs. For full advanced examples, see `advanced_examples.md`.
