# Basic Usage

This guide expands on **Simple Usage** by showing additional CLI flags, configuration file support, environment‐variable overrides, and richer Python‐API options. We assume you have Pascal Zoning ML installed (either via `pip install -e .` or from PyPI) and a working GeoTIFF or precomputed index arrays.

---

## 1. Environment Variables & Config File

Pascal Zoning ML can read default settings from environment variables or a `config.yaml` file. CLI flags override configuration entries, and configuration entries override environment variables.

### 1.1 Environment Variables

You can set these in your shell before invoking the CLI or Python API. For example:

```bash
# Set default logging level
export ZONING_LOG_LEVEL="DEBUG"

# Set a default output directory (if you omit --output-dir in the CLI)
export ZONING_OUTPUT_DIR="/path/to/outputs"

# Limit RAM used (if supported by your environment)
export ZONING_MAX_MEMORY_GB="16"
```

Pascal Zoning ML will pick up these environment variables automatically at runtime (via Typer and internal logic).

### 1.2 config.yaml

Create a file named `config.yaml` in your project root with the following structure:

```yaml
zoning:
  random_state: 123
  min_zone_size_ha: 0.2
  max_zones: 8
  use_pca: true

clustering:
  # (These are advanced parameters if exposed later)
  n_init: 10
  max_iter: 300

sampling:
  points_per_zone: 5
  min_distance_m: 10.0

io:
  # These sections are purely illustrative; currently only CLI flags matter
  default_output_dir: "./outputs/from_config"
```

When you run the CLI with `--config config.yaml`, Pascal Zoning ML will read these defaults and then apply any CLI overrides you supply.

## 2. Command‐Line Interface (CLI) Examples

### 2.1 Using a config file + overriding flags

Suppose you have:
- `config.yaml` as shown above
- A GeoTIFF at `./inputs/field_clip.tif` (EPSG:32719, 5 bands: SWIR, NIR, RED_EDGE, RED, GREEN)

Run:

```bash
python -m pascal_zoning.pipeline run \
  --config config.yaml \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDRE \
  --force-k 4 \
  --output-dir ./outputs/cli_basic
```

What happens?

**Load defaults from config.yaml:**
- `random_state = 123`
- `min_zone_size_ha = 0.2`
- `max_zones = 8`
- `use_pca = true`
- `points_per_zone = 5` (from sampling)

**CLI overrides:**
- `--indices NDVI,NDRE` (compute only those two indices)
- `--force-k 4` (force exactly 4 clusters)
- `--output-dir ./outputs/cli_basic`

Output will go into a timestamped subfolder under `./outputs/cli_basic`.

### 2.2 Specifying only environment variables

If you export:

```bash
export ZONING_OUTPUT_DIR="./outputs/env_basic"
export ZONING_LOG_LEVEL="INFO"
```

and then run:

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --max-zones 6
```

Because `--output-dir` is omitted, Pascal Zoning ML writes to `$ZONING_OUTPUT_DIR/YYYYMMDD_HHMMSS_kAUTO_mz0.5` (default `min_zone_size_ha = 0.5` unless overridden).

- Logging will honor INFO level (less verbose than DEBUG).
- `k` is chosen automatically from 2..6.

### 2.3 Saving intermediate files

By default, Pascal Zoning ML only writes final outputs into the timestamped folder. To keep intermediate artifacts (such as the raw mask, feature matrix, or raw cluster labels), set the environment variable:

```bash
export ZONING_SAVE_INTERMEDIATES="true"
```

Then run:

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI \
  --output-dir ./outputs/intermediates_example
```

You will find additional files inside the timestamped folder:

```
YYYYMMDD_HHMMSS_kAUTO_mz0.5/
├── intermediate/
│   ├── valid_mask.npy
│   ├── feature_matrix.npy
│   ├── cluster_labels.npy
│   └── zones_raw.geojson
├── zonificacion_agricola.gpkg
├── puntos_muestreo.gpkg
... (rest of final outputs) ...
```

*(Note: Pascal Zoning ML may require implementation of `save_intermediates()`—check future versions.)*

## 3. Python API Examples

### 3.1 Custom sampling strategy

By default, `points_per_zone` is fixed. You can override it per‐zone or apply a minimum distance constraint:

```python
from pathlib import Path
import numpy as np
import geopandas as gpd
from pascal_zoning.zoning import AgriculturalZoning, ZoningResult, ClusterMetrics, ZoneStats

# Pre‐computed indices (e.g., 100×100 arrays)
ndvi = np.load("data/ndvi.npy")
ndwi = np.load("data/ndwi.npy")
ndre = np.load("data/ndre.npy")
si   = np.load("data/si.npy")

indices = {
    "NDVI": ndvi,
    "NDWI": ndwi,
    "NDRE": ndre,
    "SI": si
}

# Load a boundary from GeoPackage
field_gdf = gpd.read_file("data/field_boundary.gpkg")
bounds_polygon = field_gdf.geometry.iloc[0]

# Instantiate engine with PCA enabled and a custom random_state
zoning = AgriculturalZoning(
    random_state=2023,
    min_zone_size_ha=0.1,
    max_zones=5,
    output_dir=Path("outputs/api_basic")
)

# Run, but change points_per_zone to 10, enable PCA, and let k be automatic
result: ZoningResult = zoning.run_pipeline(
    indices=indices,
    bounds=bounds_polygon,
    points_per_zone=10,
    crs="EPSG:32719",
    force_k=None,     # auto‐select k
    use_pca=True      # turn on PCA
)

# Post‐process: filter out any sample points that lie too close (< 5 m) to each other
samples_gdf = result.samples.copy()
samples_gdf = samples_gdf[samples_gdf.geometry.apply(lambda p: p.distance(p) >= 5.0)]

# Print summary
print(f"Chosen k = {result.metrics.n_clusters}")
print(f"Zone areas (ha): {[s.area_ha for s in result.stats]}")
```

### 3.2 Programmatic Configuration

Rather than using environment variables or CLI flags, you can programmatically assign default parameters:

```python
from pascal_zoning.config import ZoningConfig
from pascal_zoning.zoning import AgriculturalZoning

# Create a config object (matching config.yaml schema)
app_config = ZoningConfig(
    zoning={
        "random_state": 555,
        "min_zone_size_ha": 0.3,
        "max_zones": 6,
        "use_pca": False
    },
    sampling={
        "points_per_zone": 8,
        "min_distance_m": None
    }
)

# Instantiate using the config directly
zoning = AgriculturalZoning.from_config(app_config)
# (Assumes `from_config` static method reads the dictionary and sets attributes)

# Proceed as normal with zoning.run_pipeline(...)
```

*(Note: The `ZoningConfig` class and `.from_config()` method may require you to implement them or consult the `config.py` file.)*

## 4. Common Advanced Options

### 4.1 Changing PCA variance ratio

By default, PCA retains 95% of variance. To adjust:

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs/basic_pca \
  --use-pca \
  --pca-variance 0.90
```

*(Note: The `--pca-variance` flag must be implemented in `pipeline.py` to override `PCA(n_components=variance)`. If not yet available, you can modify `zoning.pca` manually in code.)*

### 4.2 Logging to a file

To save logs to disk (ISO 42001 traceability):

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs/logging_example \
  --log-file ./outputs/logging_example/run.log
```

This assumes the CLI supports `--log-file <path>` to write Loguru output. Otherwise, set:

```bash
export ZONING_LOG_FILE="./outputs/logging_example/run.log"
```

and Pascal Zoning ML will detect and write to that file.

## 5. Input/Output Tracking

When you run a "basic" or "advanced" example, Pascal Zoning ML will generate a JSON "manifest" of inputs and outputs for auditing. The default filename is `manifest_zoning.json` within the timestamped folder:

```json
{
  "name": "pascal-zoning-ml",
  "version": "0.1.0",
  "timestamp": "2025-06-04T15:23:10Z",
  "interfaces": {
    "input": {
      "raster": "./inputs/field_clip.tif",
      "indices": ["NDVI", "NDRE"]
    },
    "output": {
      "geopackages": {
        "zonificacion_agricola": "zonificacion_agricola.gpkg",
        "puntos_muestreo": "puntos_muestreo.gpkg"
      },
      "csv": "estadisticas_zonas.csv",
      "json": "metricas_clustering.json",
      "png": {
        "mapa_ndvi": "mapa_ndvi.png",
        "mapa_clusters": "mapa_clusters.png",
        "zonificacion_results": "zonificacion_results.png"
      },
      "log": "pipeline_run.log"
    }
  },
  "metadata": {
    "processing_time": 12.345,
    "software_version": "0.1.0"
  }
}
```

Use this manifest to provide ISO 42001–compliant traceability:
- Timestamps
- Parameter lists
- Exact file paths

## 6. Summary

- **Simple Usage** is best for first‐time runs.
- **Basic Usage** introduces configuration files, environment variables, and more CLI flags.
- **Advanced Usage** (see `advanced_examples.md`) covers multi‐field batch runs, custom cluster metrics export, and integration with downstream analytics.

For additional details on coding patterns, configuration conventions, and ISO 42001 traceability, consult the following:
- `advanced_examples.md`
- `iso42001_compliance.md`
- `normative_dependencies.md`