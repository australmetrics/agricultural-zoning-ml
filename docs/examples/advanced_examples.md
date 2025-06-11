---
title: Advanced Examples
nav_order: 7
-------------

# Advanced Examples

<!-- TOC -->

## Table of Contents

1. [Batch Processing Multiple Fields](#batch-processing-multiple-fields)
2. [Temporal Analysis (Time Series)](#temporal-analysis-time-series)
3. [Multi-Site Regional Assessment](#multi-site-regional-assessment)
4. [Complex Multi-Sensor Fusion](#complex-multi-sensor-fusion)
5. [Enterprise-Level Automation](#enterprise-level-automation)
6. [Performance Optimization Techniques](#performance-optimization-techniques)

   * [Memory-Efficient Processing](#memory-efficient-processing)
   * [Parallel Processing for Multiple Files](#parallel-processing-for-multiple-files)
7. [Advanced Quality Control](#advanced-quality-control)
8. [Integration with External Tools](#integration-with-external-tools)

   * [GDAL Integration](#gdal-integration)
   * [Database Integration](#database-integration)
9. [Custom Cluster-Metrics Export](#custom-cluster-metrics-export)
10. [Downstream Analytics & Reporting](#downstream-analytics--reporting)
11. [ISO 42001–Level Traceability Hooks](#iso-42001–level-traceability-hooks)

    * [Extended Manifest Schema](#extended-manifest-schema)
    * [Logging & Audit Trail](#logging--audit-trail)
    * [Git Commit & Dependency Freeze](#git-commit--dependency-freeze)
12. [Continuous Integration (CI)](#continuous-integration-ci)
13. [Summary](#summary)

---

## 1. Batch Processing Multiple Fields

Run zonification on dozens of clipped GeoTIFFs in parallel, preserving ISO 42001 audit trails.

### 1.1 Directory Structure

```text
project_root/
├── inputs/                # field_A.tif, field_B.tif, ...
├── configs/
│   └── batch_config.yaml  # Shared parameters
├── outputs/               # Populated per-field
└── scripts/
    └── batch_run.py       # Batch driver script
```

### 1.2 configs/batch\_config.yaml

```yaml
zoning:
  random_state: 2025
  min_zone_size_ha: 0.25
  max_zones: 6
audit:
  logging: true
  software_version: "1.0.2"
```

### 1.3 scripts/batch\_run.py

```python
#!/usr/bin/env python3
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from pascal_zoning.config import ZoningConfig
from pascal_zoning.zoning import AgriculturalZoning

# Load shared configuration
def load_config(path: str):
    return ZoningConfig.from_yaml(Path(path))

# Process a single field
def process_field(raster_path: Path, cfg: ZoningConfig):
    # Compute zonification via CLI invocation or API
    engine = AgriculturalZoning.from_config(cfg)
    engine.output_dir = Path(cfg.output_base) / raster_path.stem
    return engine.run_pipeline(
        indices=engine.compute_indices(raster_path),
        bounds=engine.derive_boundary(raster_path),
        points_per_zone=cfg.sampling.points_per_zone,
        crs=engine.default_crs,
        validate_system=True,
        validate_model=True
    )

if __name__ == "__main__":
    import glob, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs-dir", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    cfg = load_config(args.config)
    cfg.output_base = args.output_dir
    rasters = glob.glob(f"{args.inputs_dir}/*.tif")

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(lambda p: process_field(Path(p), cfg), rasters):
            print(f"Field {result.run_id}: {result.metrics.n_clusters} zones")
```

Outputs for each field are under `outputs/{field_name}/{timestamp}_k{K}_mz{min_zone_size}/`, including audit and manifest files.

---

## 2. Temporal Analysis (Time Series)

Monitor vegetation changes over multiple acquisitions.

**Structure:**

```text
data/temporal_analysis/
├── 20240301_field.tif
├── 20240401_field.tif
└── ...
boundaries/field_boundary.shp
```

**Bash Script:**

```bash
#!/bin/bash
for date in 20240301 20240401 20240501; do
  python -m pascal_zoning.pipeline run \
    --raster "data/temporal_analysis/${date}_field.tif" \
    --indices NDVI,NDRE,SAVI \
    --output-dir "outputs/temporal/${date}" \
    --validate-system --validate-model
done
```

Collate metrics across dates by reading each `metricas_clustering.json` or manifest.

---

## 3. Multi-Site Regional Assessment

Apply zonification across multiple geographically dispersed sites.

**Data Layout:**

```text
data/sites/
├── site_001/image.tif
├── site_001/boundary.shp
├── site_002/image.tif
├── site_002/boundary.shp
└── ...
```

**Processing Script:**

```bash
#!/bin/bash
for site in data/sites/site_*; do
  python -m pascal_zoning.pipeline run \
    --raster "$site/image.tif" \
    --raster "$site/boundary.shp" \
    --output-dir "outputs/regional/$(basename $site)" \
    --validate-system --validate-model
done
```

Per-site audit logs and manifests are stored under each output directory.

---

## 4. Complex Multi-Sensor Fusion

Combine Sentinel-2 and Landsat-8 data for fused analysis.

**Structure:**

```text
data/fusion_analysis/
├── sentinel2/S2_20240515.tif
├── sentinel2/S2_20240530.tif
├── landsat8/L8_20240507.tif
├── landsat8/L8_20240523.tif
└── boundaries/study_area.shp
```

**Fusion Workflow:**

```bash
#!/bin/bash
PROJECT="sensor_fusion"
mkdir -p "results/${PROJECT}"/({sentinel2,landsat8,analysis_log})

echo "Fusion analysis start: $(date)" > "results/${PROJECT}/analysis_log/fusion.log"

# Process Sentinel-2
for img in data/fusion_analysis/sentinel2/*.tif; do
  python -m pascal_zoning.pipeline run \
    --raster "$img" \
    --shapefile "data/fusion_analysis/boundaries/study_area.shp" \
    --output-dir "results/${PROJECT}/sentinel2/$(basename $img .tif)" \
    --validate-system --validate-model 2>&1 | tee -a "results/${PROJECT}/analysis_log/fusion.log"
done

# Process Landsat-8
for img in data/fusion_analysis/landsat8/*.tif; do
  python -m pascal_zoning.pipeline run \
    --raster "$img" \
    --shapefile "data/fusion_analysis/boundaries/study_area.shp" \
    --output-dir "results/${PROJECT}/landsat8/$(basename $img .tif)" \
    --validate-system --validate-model 2>&1 | tee -a "results/${PROJECT}/analysis_log/fusion.log"
done

echo "Fusion analysis completed: $(date)" >> "results/${PROJECT}/analysis_log/fusion.log"
```

---

## 5. Enterprise-Level Automation

Define a single configuration for large-scale, audit-ready deployments.

**enterprise\_config.yaml:**

```yaml
project:
  name: "enterprise_monitoring"
  version: "1.0"
  audit:
    logging: true
    retention_days: 90
input:
  base_path: "data/enterprise"
output:
  base_path: "results/enterprise"
processing:
  indices: [NDVI, NDRE, SAVI]
  quality_control: true
cli:
  validate_system: true
  validate_model: true
```

**Enterprise Script:**

```bash
python -m pascal_zoning.pipeline run \
  --config enterprise_config.yaml \
  --batch-mode \
  --validate-system \
  --validate-model
```

Generates structured logs, manifests, and QC reports per batch.

---

## 6. Performance Optimization Techniques

### Memory-Efficient Processing

Use system limits and chunking for large rasters:

```bash
ulimit -v 4000000  # Limit virtual memory ~4GB
echo "Processing with memory cap..."
python -m pascal_zoning.pipeline run \
  --raster data/large.tif \
  --indices NDVI,NDWI \
  --output-dir results/memory_opt \
  --validate-system
```

### Parallel Processing for Multiple Files

```bash
MAX_PARALLEL=4
find data/ -name "*.tif" | parallel -j $MAX_PARALLEL \
  python -m pascal_zoning.pipeline run --raster {} --output-dir results/parallel/{}
```

---

## 7. Advanced Quality Control

Validate outputs and logs post-processing:

```bash
QC_DIR="results/quality_control"
mkdir -p "$QC_DIR"
for dir in results/*/*/; do
  python - <<EOF
from pathlib import Path
from pascal_zoning.validation import validate_results
validate_results(Path('$dir'))
EOF
done
```

---

## 8. Integration with External Tools

### GDAL Integration

```bash
# Build overviews
gdaladdo -r average results/*/*/*_ndvi.tif 2 4 8 16
# Generate hillshade
gdaldem hillshade data/dem.tif results/hillshade.tif
```

### Database Integration

```bash
DB_CONN="postgresql://user:pass@localhost:5432/db"
for tif in results/*/*/*_ndvi.tif; do
  raster2pgsql -s 32719 -I -C -M "$tif" vegetation_indices | psql "$DB_CONN"
done
```

---

## 9. Custom Cluster-Metrics Export

Extend `ClusterMetrics` to include additional metrics:

```python
from sklearn.metrics import davies_bouldin_score
def perform_clustering(...):
    # After labels
    db_score = davies_bouldin_score(features, labels)
    metrics.db_score = db_score
```

---

## 10. Downstream Analytics & Reporting

Generate PDF reports with Jinja2 & WeasyPrint:

```bash
pip install jinja2 weasyprint
python scripts/generate_report.py \
  outputs/field_A/.../manifest_zoning.json \
  templates/ \
  outputs/field_A/.../report.pdf
```

---

## 11. ISO 42001–Level Traceability Hooks

### Extended Manifest Schema

Validate `manifest_zoning.json` against `schemas/zoning_output.schema.json` to ensure required fields:

* `version`, `timestamp`, `software_version`
* `validated_system`, `validated_model`, `audit_logging`

### Logging & Audit Trail

Use Loguru in CLI entrypoint:

```python
from loguru import logger
from datetime import datetime

timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
logger.add(sys.stderr, level=os.getenv("ZONING_LOG_LEVEL", "INFO"))
logger.add(f"{output_dir}/logs/run_{timestamp}.log", level="DEBUG")
```

### Git Commit & Dependency Freeze

Before production runs:

```bash
git rev-parse HEAD > output/.../git_sha.txt
pip freeze > output/.../requirements_frozen.txt
```

---

## 12. Continuous Integration (CI)

Automate ISO 42001–compliant quality gates via GitHub Actions:

```yaml
# .github/workflows/ci.yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |-
          pip install -r requirements-dev.txt
          black --check src/
          flake8 src/
  typecheck:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |-
          pip install -r requirements.txt
          pip install mypy pyright
          mypy src/
          pyright
  test:
    needs: [lint, typecheck]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |-
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pytest tests/unit tests/integration
```

---

## 13. Summary

This comprehensive guide covers advanced batch workflows, time-series and multi-site analyses, enterprise automation, performance tuning, quality control, external integrations, custom metrics, reporting, ISO 42001 traceability, and CI/CD best practices. By following these patterns, you can integrate Pascal Zoning ML into enterprise-grade, audit-ready precision agriculture systems at scale.
