# Simple Usage

This document shows the most basic workflow to run Pascal Zoning ML on a small, pre‐computed set of spectral indices or a clipped GeoTIFF. It demonstrates both the **CLI** approach and the **Python API** approach with minimal configuration.

## 1. Prerequisites

- **Python** 3.11+ installed
- The package installed (editable or via `pip install pascal-zoning-ml`)
- A GeoTIFF (or in‐memory NumPy arrays) representing spectral indices
- Basic familiarity with your terminal (bash / PowerShell) and Python

## 2. Quick CLI Example

### 1. Prepare your input  
- If you already have a clipped GeoTIFF (e.g. `field_clip.tif`), ensure it contains at least the bands required to compute NDVI, NDWI, NDRE, and SI.  
- If you only have separate index arrays (e.g. pre‐computed NDVI & NDRE), you can skip the CLI and use the Python API (see Section 3).

### 2. Run the pipeline via CLI
Open a terminal in your project root (where `pascal_zoning.pipeline` is available) and execute:

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs/simple_run \
  --force-k 3 \
  --min-zone-size 0.5 \
  --max-zones 5
```

### Explanation of flags:

- `--raster ./inputs/field_clip.tif`  
  Path to your clipped GeoTIFF (in EPSG:32719, for example).

- `--indices NDVI,NDWI,NDRE,SI`  
  Comma‐separated list of index names to compute (or ingest if already in the TIFF).

- `--output-dir ./outputs/simple_run`  
  Base folder where Pascal Zoning will create a timestamped subfolder.

- `--force-k 3`  
  Force K‐Means to use exactly 3 clusters (management zones).

- `--min-zone-size 0.5`  
  Filter out zones smaller than 0.5 ha.

- `--max-zones 5`  
  If `--force-k` is omitted, Pascal Zoning will evaluate k = 2, 3, 4, 5 and pick the best via silhouette.

### Check the output folder

After the run completes (exit code 0), navigate into `./outputs/simple_run/YYYYMMDD_HHMMSS_k3_mz0.5/` (timestamp will vary) and you should see at least:

```
zonificacion_agricola.gpkg    # Vector layer of management zones
puntos_muestreo.gpkg         # Vector layer of sampling points
mapa_ndvi.png                # NDVI raster map (PNG)
mapa_clusters.png            # Cluster polygons map (PNG)
estadisticas_zonas.csv       # Tabular CSV of per-zone stats
metricas_clustering.json     # JSON of cluster metrics
zonificacion_results.png     # Overview composite figure (map + bar chart)
```

## 3. Minimal Python API Example

If you already have NumPy arrays for NDVI and NDRE (or any combination of indices), you can skip the CLI and call the pipeline directly from Python.

1. Prepare two 2×2 sample arrays (just for demonstration):

```python
import numpy as np

ndvi_array = np.array([[0.1, 0.2],
                       [0.3, 0.4]], dtype=float)

ndre_array = np.array([[0.0, 0.1],
                       [0.2, 0.3]], dtype=float)

indices = {
    "NDVI": ndvi_array,
    "NDRE": ndre_array
}
```

2. Define a simple square boundary (for a 2 m×2 m field):

```python
from shapely.geometry import Polygon

bounds_polygon = Polygon([
    (0, 0),
    (2, 0),
    (2, 2),
    (0, 2)
])
```

3. Run the pipeline from Python:

```python
from pathlib import Path
import geopandas as gpd
from pascal_zoning.zoning import AgriculturalZoning

# 1) Instantiate the zoning engine
zoning = AgriculturalZoning(
    random_state=42,
    min_zone_size_ha=0.0001,   # Allow very small zones (0.0001 ha = 1 m²)
    max_zones=3,
    output_dir=Path("./outputs/simple_api")
)

# 2) Execute the full pipeline
result = zoning.run_pipeline(
    indices=indices,
    bounds=bounds_polygon,
    points_per_zone=2,
    crs="EPSG:32719",         # CRS must match how you interpret world coordinates
    force_k=None              # Allow automatic selection of k
)

# 3) Inspect results
zones_gdf   = result.zones     # GeoDataFrame of polygons
samples_gdf = result.samples   # GeoDataFrame of points
metrics     = result.metrics   # ClusterMetrics (n_clusters, silhouette, inertia, etc.)
stats_list  = result.stats     # List of ZoneStats (per-zone area, compactness, mean/std, …)

print(f"Number of zones: {metrics.n_clusters}")
print(f"Silhouette score: {metrics.silhouette:.4f}")

for s in stats_list:
    print(f"  Zone {s.zone_id}: area={s.area_ha:.6f} ha, compactness={s.compactness:.4f}")
```

Examine the `./outputs/simple_api/YYYYMMDD_HHMMSS_kAUTO_mz0.0001/` folder:
```
zonificacion_agricola.gpkg
puntos_muestreo.gpkg
estadisticas_zonas.csv
metricas_clustering.json
zonificacion_results.png
```

## 4. What Just Happened?

### `create_mask()`
- Builds a boolean mask of "valid pixels" (inside your polygon & non‐NaN).

### `prepare_feature_matrix()`
- Stacks the indices ([H×W×N]) and extracts only valid pixels into a 2D array
- Imputes any missing values (median), standardizes via StandardScaler.

### `perform_clustering()`
- If `force_k` is set, uses that; otherwise scans k = 2…max_zones
- Computes Silhouette + Calinski–Harabasz for each k, picks best
- Runs final K-Means, records cluster labels per valid pixel

### `extract_zone_polygons()`
- Converts each labeled pixel (1 m²) into a square shapely.Polygon
- Dissolves by cluster → contiguous zones

### `filter_small_zones()`
- Computes area of each zone (m² → ha) and filters out zones < min_zone_size_ha
- Re‐indices cluster IDs to be consecutive

### `compute_zone_statistics()`
For each zone, calculates:
- area_ha (ha)
- perimeter_m (m)
- compactness = 4π · area / (perimeter²)
- Mean & standard deviation of each index within that zone

### `generate_sampling_points()`
- For each zone, collects pixel centers → world coordinates
- Chooses up to points_per_zone sample points by spatial inhibition
- Attaches spectral index values to each sample

### `save_results()` / `visualize_results()`
- Writes GeoPackage (.gpkg), CSV (.csv), JSON (.json), and PNG maps (.png)

## 5. Troubleshooting Tips

If you see `ProcessingError: No valid pixels inside polygon`, check that:
- Your polygon's CRS matches the GeoTIFF's CRS (e.g., both EPSG:32719).
- The TIFF has nonzero values inside the polygon (no all‐zero or NaN).

If K-Means throws an error like `n_samples < n_clusters`, reduce `--force-k` or lower `max_zones`.

If all zones disappear (empty `zones_gdf`), try decreasing `min_zone_size_ha` (e.g., 0.0001).