# Pascal Zoning ML — NDVI Integration Interface

**Version:** main  |  **Owner:** AustralMetrics SpA  |  **ISO 42001 Compliant**

This document describes how to integrate externally computed spectral indices—particularly NDVI—from a dedicated index block into the core Pascal Zoning ML pipeline as implemented in the `agricultural-zoning-ml` repository.

---

## 1. CLI Interface

### 1.1 Inputs

* **`--raster`** (Path): Path to a clipped multi-band GeoTIFF containing all bands needed for requested indices.
* **`--indices`** (str): Comma-separated list of indices to compute. Supported: `NDVI`, `NDWI`, `NDRE`, `SI`.
* **`--output-dir`** (Path): Base directory where a timestamped run folder will be created.
* **Optional flags**:

  * `--force-k <int>`: Force K‑Means to use exactly `k` clusters.
  * `--min-zone-size <float>`: Minimum zone area (ha). Default: `0.5`.
  * `--max-zones <int>`: Maximum clusters to evaluate. Default: `10`.
  * `--use-pca`: Enable PCA to reduce feature dimensions to 95% variance.

### 1.2 Command Example

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field_clip.tif \
  --indices NDVI,NDWI,NDRE \
  --output-dir ./outputs \
  --force-k 4 \
  --min-zone-size 0.2 \
  --max-zones 8 \
  --use-pca
```

### 1.3 Run Outputs

After execution, the pipeline creates a subfolder under `<output-dir>`:

```
<output-dir>/
└── YYYYMMDD_HHMMSS_k4_mz0.2/
    ├── zonificacion_agricola.gpkg     # Management zone polygons
    ├── puntos_muestreo.gpkg           # Sampling points with index attributes
    ├── mapa_ndvi.png                  # NDVI raster visualization
    ├── mapa_clusters.png              # Clustered zone map
    ├── estadisticas_zonas.csv         # Zone statistics table
    ├── metricas_clustering.json       # Clustering quality metrics
    └── zonificacion_results.png       # Composite overview figure
```

---

## 2. Python API Interface

### 2.1 Class: `AgriculturalZoning`

Defined in `pascal_zoning/zoning.py`.

#### Constructor Parameters

```python
AgriculturalZoning(
    random_state: Optional[int] = None,
    min_zone_size_ha: float,
    max_zones: int
)
```

#### Method: `run_pipeline`

```python
ZoningResult = zoning.run_pipeline(
    indices: Dict[str, np.ndarray],
    bounds: shapely.geometry.Polygon,
    points_per_zone: int,
    crs: str,
    force_k: Optional[int] = None,
    use_pca: bool = False,
    output_dir: Path
)
```

* **`indices`**: Mapping from index name (e.g., `"NDVI"`) to its 2D NumPy array.
* **`bounds`**: Field boundary polygon for masking.
* **`points_per_zone`**: Number of sample points per zone.
* **`crs`**: CRS string (e.g., `"EPSG:32719"`).
* **`force_k`**: Override automatic cluster selection.
* **`use_pca`**: Apply PCA for dimensionality reduction.
* **`output_dir`**: Directory where outputs are saved.

#### Returns: `ZoningResult`

The returned dataclass includes:

* **`zones`**: `geopandas.GeoDataFrame` of zone polygons.
* **`samples`**: `geopandas.GeoDataFrame` of sampling points.
* **`metrics`**: `ClusterMetrics` with fields: `n_clusters`, `silhouette`, `calinski_harabasz`, `inertia`.
* **`stats`**: List of `ZoneStats` with fields: `zone_id`, `area_ha`, `perimeter_m`, `compactness`, per-index mean & standard deviation.

---

## 3. Version & Compatibility

* **Repository Version**: Main (see `pyproject.toml`).
* **Python Requirement**: ≥ 3.11.
* **ISO Standard**: 42001.
* **Dependencies**: See `requirements.txt`.

---

© 2025 AustralMetrics SpA. All rights reserved.

