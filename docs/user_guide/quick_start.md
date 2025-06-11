---
title: Quick Start
nav_order: 3
-------------

# Quick Start

This quick start guide demonstrates how to run an end-to-end zoning workflow with **Pascal Zoning ML** in minutes, using both the CLI and Python API. Follow the steps below to generate vegetation indices, produce management zones, and review outputs with full traceability.

## Prerequisites

* **Pascal Zoning ML** installed (see [Installation](installation.md)).
* Sample GeoTIFF raster file with correct CRS and valid data.
* Virtual environment activated (recommended).

Verify the CLI is accessible:

```bash
pascal-zoning --version
```

## CLI Workflow

### 1. Generate Vegetation Indices

Compute standard indices (NDVI, NDRE, SAVI) if not precomputed:

```bash
pascal-zoning indices \
  --input path/to/image.tif \
  --output-dir indices/ \
  --overwrite
```

**Default outputs in `indices/`:**

* `ndvi.tif`
* `ndre.tif`
* `savi.tif`
* `manifest.json` (summary of index files)

### 2. Run Zoning Pipeline

Execute the zoning algorithm with default parameters:

```bash
pascal-zoning zoning \
  --indices-dir indices/ \
  --output-dir zonation/ \
  --points-per-zone 10 \
  --min-distance 50
```

**Default outputs in `zonation/`:**

* `zone_polygons.gpkg` (management zones)
* `sampling_points.gpkg` (stratified sampling locations)
* `zonation_results.png` (map overview)
* `logs/` folder containing `pascal_zoning_<timestamp>.log`

#### Advanced CLI Options

* **`--force-k`**: specify a fixed number of clusters.
* **`--min-zone-size`**: minimum area (ha) to filter small zones.
* **`--use-pca` / `--no-pca`**: enable or disable dimensionality reduction.
* **`--dpi`**: set output map resolution.

Run `pascal-zoning zoning --help` to view all flags.

### 3. Inspect Logs for Traceability

Review the last lines of the processing log to confirm parameter values and performance metrics:

```bash
tail -n 20 zonation/logs/pascal_zoning_*.log
```

## Python API Example

Integrate the same workflow into Python scripts for customized analysis:

```python
from pascal_zoning import AgriculturalZoning

az = AgriculturalZoning()
results = az.run_pipeline(
    indices_dir="indices/",
    output_dir="zonation/",
    points_per_zone=10,
    min_distance=50.0,
    force_k=None,         # optional override
    use_pca=True          # default True
)

# Access GeoDataFrames
zones = results.zone_polygons
samples = results.sampling_points
```

Use the `results` object to compute additional statistics or integrate with GIS tools.

## Verify Outputs

List files to ensure all artifacts were created:

```bash
ls zonation/
```

Preview maps in your local viewer or GIS platform:

```bash
open zonation/zonation_results.png
```

## Next Steps

* Customize the clustering by adjusting `--force-k` or PCA settings.
* Combine `pascal-zoning indices` and `zoning` into a single command:

  ```bash
  pascal-zoning run --input image.tif --output out/ --points-per-zone 5
  ```
* Explore advanced examples in [Usage Examples](examples.md).
* Refer to [API Documentation](../technical/api_documentation.md) for full parameter list.

---

*This quick start ensures ISO 42001 traceability with consistent logs, metadata, and versioned artifacts.*
title: Installation
nav\_order: 2
-------------

# Installation

Follow these steps to prepare your environment and install **Pascal Zoning ML**.

## Prerequisites

* Python 3.11 or higher
* GDAL 3.6+ (includes `gdal-bin` and `libgdal-dev` on Ubuntu/Debian)
* C compiler (e.g., `gcc`, `clang`)
* *(Optional)* `conda` or `pyenv` for Python version management

## Virtual Environment

Create and activate a virtual environment for project isolation:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

## Install from PyPI

```bash
pip install pascal-zoning
```

Verify the CLI is available:

```bash
pascal-zoning --help
```

## Install from Source

Clone the repository and install in editable mode:

```bash
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml
pip install -e .
```

Confirm the package version:

```bash
pascal-zoning --version
```

## Optional Dependencies

Install extras for extended functionality (metrics, telemetry):

```bash
pip install pascal-zoning[extras]
```

## Docker

For a containerized setup, build and run the provided Dockerfile:

```bash
# Build the Docker image
docker build -t pascal-zoning:latest .

# Run a container and execute CLI
docker run --rm -v "$(pwd)":/data pascal-zoning:latest pascal-zoning --help
```

## Uninstall

```bash
pip uninstall pascal-zoning
```

---

For detailed dependency versions, refer to `requirements.txt` and `requirements-dev.txt`. If you encounter any issues, open an issue on our [GitHub tracker](https://github.com/australmetrics/agricultural-zoning-ml/issues).
