# Pascal Zoning (Agricultural Zoning ML)

A machine learning–powered system for generating agricultural management zones and optimized sampling points based on spectral‐index analysis. Part of the **`pascal-zoning-ml`** repository, this project complies with ISO 42001 (AI Management System Standard)..

---
## Project Status

[![Tests & Lint](https://github.com/australmetrics/agricultural-zoning-ml/actions/workflows/test.yml/badge.svg)](https://github.com/australmetrics/agricultural-zoning-ml/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/australmetrics/agricultural-zoning-ml/branch/main/graph/badge.svg)](https://codecov.io/gh/australmetrics/agricultural-zoning-ml)
[![ISO 42001](https://img.shields.io/badge/ISO-42001-blue.svg)](docs/compliance/iso42001_compliance.md)



## 🌾 Overview

Pascal Zoning processes a clipped GeoTIFF of an agricultural block and performs:

1. **Mask Creation**  
   - Generates a boolean mask to isolate field pixels (inside polygon, non‐null indices).  
2. **Feature Preprocessing**  
   - Median imputation for missing values.  
   - Standardization (Z-score) of spectral indices.  
   - (Optional) PCA to retain 95% variance.  
3. **Clustering (K-Means)**  
   - Evaluate *k* from 2 to `max_zones` using Silhouette and Calinski-Harabasz indices.  
   - Select the best *k* (or force *k* with `--force-k`).  
   - Generate a raster of cluster labels.  
4. **Zone Extraction & Filtering**  
   - Dissolve cluster-labeled pixels into polygons.  
   - Compute area (m² → ha) and perimeter (m).  
   - Filter out zones smaller than `min_zone_size_ha`.  
   - Reassign cluster IDs consecutively (0, 1, 2…).  
5. **Sampling Point Generation**  
   - Within each zone, sample up to `points_per_zone` points via spatial inhibition (maximizing the minimum distance).  
   - Attach spectral index values to each point.  
6. **Zone Statistics**  
   - For each zone:  
     - **Geometric**: `area_ha`, `perimeter_m`, `compactness = 4π·area / (perimeter²)`.  
     - **Spectral**: mean and standard deviation for each index.  
7. **Visualization**  
   - **NDVI Map**: Raster NDVI clipped to field, masked out-of-field pixels.  
   - **Cluster Map**: Zones colored by cluster ID.  
   - **Overview Figure**: Combined cluster map + bar chart of zone areas.  
8. **Export / Outputs**  
   - **GeoPackage**:  
     - `zonificacion_agricola.gpkg` (polygons of management zones)  
     - `puntos_muestreo.gpkg` (sampling points with index values)  
   - **CSV / JSON**:  
     - `estadisticas_zonas.csv` (tabular zone statistics)  
     - `metricas_clustering.json` (cluster quality metrics)  
   - **PNG Figures**:  
     - `mapa_ndvi.png` (NDVI raster)  
     - `mapa_clusters.png` (cluster polygons)  
     - `zonificacion_results.png` (overview figure)

All processing steps are exposed both via a **CLI** (`pascal_zoning.pipeline`) and a **Python API** (`AgriculturalZoning` class).

---

## ✨ Features

- **Command-Line Interface (CLI)**  
  - Built with Typer for straightforward invocation.  
  - Example:  
    ```bash
    python -m pascal_zoning.pipeline run \
      --raster ./inputs/field.tif \
      --indices NDVI,NDWI,NDRE,SI \
      --output-dir ./outputs \
      --force-k 3 \
      --min-zone-size 0.5
    ```  

- **Python API** (`AgriculturalZoning`)  
  - Full pipeline accessible programmatically.  
  - Modular methods for each stage (mask creation, clustering, sampling, etc.).  
  - Returns a `ZoningResult` dataclass containing zones, samples, metrics, and stats.

- **Automatic *k* Selection**  
  - Silhouette and Calinski-Harabasz metrics for *k* ∈ [2, `max_zones`].  
  - Option to override with `--force-k`.

- **Zone Filtering**  
  - Remove zones below a minimum area threshold (hectares).  
  - Reassign cluster IDs consecutively.

- **Optimized Sampling**  
  - Spatial inhibition algorithm: place up to `points_per_zone` per zone maximizing pairwise distance.

- **Detailed Zone Statistics**  
  - Area (ha), perimeter (m), compactness.  
  - Mean & standard deviation per index.

- **Integrated Visualization**  
  - NDVI heatmap (masked to field).  
  - Cluster map (colored polygons).  
  - Overview composite (cluster map + bar chart of areas).

- **Export Formats**  
  - GeoPackage (`.gpkg`) for GIS-ready vector outputs.  
  - CSV & JSON for tabular data.  
  - PNG for graphical outputs.

- **ISO 42001 Compliant**  
  - Detailed logging (timestamp, module, message).  
  - Metadata in outputs (creation date, cluster parameters).  
  - Automated tests (unit, integration).  
  - Version control and change tracking.

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+  
- **GDAL/OGR** installed on the system (for `rasterio`)  
- **Git** (optional, for cloning repository)

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/australmetrics/agricultural-zoning-ml.git
   cd agricultural-zoning-ml
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install the package in editable mode**
   ```bash
   pip install -e .
   ```

---

## 🛠️ Usage

### Command-Line Interface (CLI)

```bash
python -m pascal_zoning.pipeline run \
  --raster ./inputs/field.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir ./outputs \
  --force-k 3 \
  --min-zone-size 0.5 \
  --max-zones 10 \
  --use-pca
```

**Parameters:**

- `--raster` (required): Path to clipped GeoTIFF of the field (must include bands needed for indices)
- `--indices` (required): Comma-separated list of spectral indices (NDVI,NDWI,NDRE,SI)
- `--output-dir` (required): Base folder where a timestamped subfolder will be created
- `--force-k <int>` (optional): Force K-Means to use exactly k clusters
- `--min-zone-size <float>` (optional): Minimum zone area (ha). Default: 0.5
- `--max-zones <int>` (optional): Maximum number of clusters to evaluate. Default: 10
- `--use-pca` (flag): If present, enable PCA before clustering (retain 95% variance)

**Example:**

```bash
python -m pascal_zoning.pipeline run \
  --raster data/field_clip.tif \
  --indices NDVI,NDWI,NDRE,SI \
  --output-dir results/ \
  --force-k 4 \
  --min-zone-size 0.2 \
  --max-zones 8
```

After execution, `results/` will contain a subdirectory named like:
```
20250604_164532_k4_mz0.2/
```

Inside that folder you'll find:
```
zonificacion_agricola.gpkg
puntos_muestreo.gpkg
mapa_ndvi.png
mapa_clusters.png
estadisticas_zonas.csv
metricas_clustering.json
zonificacion_results.png
```

### Python API

```python
from pathlib import Path
import numpy as np
import geopandas as gpd
from pascal_zoning.zoning import AgriculturalZoning

# 1) Load or generate spectral indices (example: 2×2 arrays)
indices = {
    "NDVI": np.array([[0.1, 0.2],[0.3, 0.4]]),
    "NDRE": np.array([[0.0, 0.1],[0.2, 0.3]])
}

# 2) Load field boundary as a single polygon
field_gdf = gpd.read_file("data/field_boundary.gpkg")
bounds_polygon = field_gdf.geometry.iloc[0]

# 3) Instantiate the zoning engine
zoning = AgriculturalZoning(
    random_state=42,
    min_zone_size_ha=0.5,
    max_zones=5
)

# 4) Run the full pipeline
result = zoning.run_pipeline(
    indices=indices,
    bounds=bounds_polygon,
    points_per_zone=5,
    crs="EPSG:32719",
    force_k=None,        # automatic k selection
    use_pca=False,
    output_dir=Path("outputs")
)

# 5) Access results
zones_gdf   = result.zones     # GeoDataFrame of polygons
samples_gdf = result.samples   # GeoDataFrame of points
metrics     = result.metrics   # ClusterMetrics (n_clusters, silhouette, CH, inertia)
stats_list  = result.stats     # List of ZoneStats (area_ha, perimeter_m, compactness…)

print(f"Number of zones: {metrics.n_clusters}")
print(f"Silhouette score: {metrics.silhouette:.4f}")
for s in stats_list:
    print(f"  Zone {s.zone_id}: area={s.area_ha:.3f} ha, compactness={s.compactness:.3f}")
```

---

## 📋 System Requirements

### Hardware
- **Memory**: ≥ 8 GB RAM recommended for medium‐sized fields
- **CPU**: ≥ 4 CPU cores recommended
- **GPU**: Optional, only if pre- or post-processing is GPU-accelerated

### Software Dependencies

**Python**: 3.11+

**Geospatial:**
- GDAL/OGR (install via OS packages or conda)
- rasterio
- geopandas
- shapely
- fiona

**Scientific / ML:**
- numpy
- pandas
- scikit-learn

**Visualization:**
- matplotlib

**CLI & Logging:**
- typer
- loguru

Install all core dependencies via:
```bash
pip install -r requirements.txt
```

For development (linters, test frameworks):
```bash
pip install -r requirements-dev.txt
```

---

## 🔧 Configuration

You can adjust parameters via environment variables or a `config.yaml` file. If both are present, CLI flags → config.yaml → environment variables → defaults.

### Environment Variables

```bash
# Set default logging level (DEBUG, INFO, WARN, ERROR)
export ZONING_LOG_LEVEL=INFO

# Default output directory if not provided in CLI
export ZONING_OUTPUT_DIR="/path/to/outputs"

# Max memory (GB) for processing large rasters
export ZONING_MAX_MEMORY_GB=16
```

### config.yaml (Optional)

Create a `config.yaml` in the project root:

```yaml
zoning:
  min_zone_size_ha: 0.5
  max_zones: 15
  random_state: 42

clustering:
  algorithm: kmeans
  n_init: 20
  max_iter: 300

sampling:
  points_per_zone: 10
  min_distance_m: 50.0

preprocessing:
  use_pca: true
  variance_ratio: 0.95
  imputation_strategy: median
```

Call the CLI with:
```bash
python -m pascal_zoning.pipeline run \
  --config config.yaml \
  --raster data/field.tif \
  --indices NDVI,NDWI,NDRE,SI
```

The CLI will read `config.yaml` and override defaults accordingly.

---

## 🧪 API Reference

### AgriculturalZoning Class

```python
class AgriculturalZoning:
    def __init__(
        self,
        random_state: int = 42,
        min_zone_size_ha: float = 0.5,
        max_zones: int = 10,
        output_dir: Optional[Path] = None
    ):
        """
        Args:
            random_state: Seed for reproducibility.
            min_zone_size_ha: Minimum zone area in hectares.
            max_zones: Maximum clusters to evaluate.
            output_dir: Default directory to save outputs (can be overridden).
        """
```

### Key Public Methods

- `run_pipeline(indices, bounds, points_per_zone, crs, force_k=None, output_dir=None, use_pca=False)` → `ZoningResult`  
  Execute full workflow; returns a ZoningResult object.

- `create_mask()`  
  Generate boolean mask (inside polygon & non-NaN pixels).

- `prepare_feature_matrix()`  
  Impute, scale, (and optionally PCA) the stacked indices.

- `perform_clustering(force_k=None)`  
  Determine optimal k or use force_k, run K-Means, store cluster_labels & metrics.

- `extract_zone_polygons()`  
  Convert cluster_labels raster to vector polygons (GeoDataFrame).

- `filter_small_zones()`  
  Remove zones with area_ha < min_zone_size_ha and reindex clusters.

- `generate_sampling_points(points_per_zone)`  
  Create sampling points via spatial inhibition, store in samples_gdf.

- `compute_zone_statistics()`  
  For each zone: compute area_ha, perimeter_m, compactness, mean/std per index.

- `save_results(output_dir=None)`  
  Export layers to GeoPackage, CSV & JSON, generate folder structure.

- `visualize_results()`  
  Plot and save NDVI map & cluster map.

### Data Classes

#### ZoningResult
```python
@dataclass
class ZoningResult:
    zones: gpd.GeoDataFrame         # Polygons of management zones
    samples: gpd.GeoDataFrame       # Sampling points
    metrics: ClusterMetrics         # Clustering metrics
    stats: List[ZoneStats]          # Per-zone statistics
```

#### ClusterMetrics
```python
@dataclass
class ClusterMetrics:
    n_clusters: int
    silhouette: float
    calinski_harabasz: float
    inertia: float
    cluster_sizes: Dict[int, int]
    timestamp: str
```

#### ZoneStats
```python
@dataclass
class ZoneStats:
    zone_id: int
    area_ha: float
    perimeter_m: float
    compactness: float
    mean_values: Dict[str, float]
    std_values: Dict[str, float]
```

---

## 📊 Output Formats

When you run the pipeline (either via CLI or API), a timestamped subfolder is created in `--output-dir`:

```
outputs/
└── YYYYMMDD_HHMMSS_k{K}_mz{min_zone_size}/
    ├── zonificacion_agricola.gpkg      # Zone polygons (vector)
    ├── puntos_muestreo.gpkg            # Sampling points (vector)
    ├── mapa_ndvi.png                   # NDVI raster map (if NDVI was given)
    ├── mapa_clusters.png               # Cluster polygons map
    ├── estadisticas_zonas.csv          # CSV: zone_id, area_ha, perimeter_m, compactness, <Index>_mean, <Index>_std
    ├── metricas_clustering.json        # JSON: n_clusters, silhouette, calinski_harabasz, inertia, cluster_sizes, timestamp
    └── zonificacion_results.png        # Overview figure (map + bar chart)
```

- **GeoPackage (.gpkg)**: GIS-ready vector layers
- **CSV**: Tabular zone statistics
- **JSON**: Machine-readable clustering metrics
- **PNG**: High-resolution figures for quick inspection or reports

---

## 🧮 Algorithm Details

### Feature Preprocessing

1. Stack indices into an (H, W, N_indices) array
2. Mask by polygon & non-NaN values
3. Impute missing (median) and scale (StandardScaler)
4. (Optional) PCA with n_components=0.95

### Optimal k Selection

1. For each k ∈ [2, max_zones]:
   - Fit KMeans(n_clusters=k)
   - Compute Silhouette Score and Calinski–Harabasz Index
   - Compute inertia (within-cluster sum of squares)
2. Select the k with highest Silhouette

### Final Clustering

1. Fit KMeans with chosen k
2. Reconstruct a 2D raster of cluster labels (−1 for outside polygon)

### Zone Extraction & Filtering

1. Convert each labeled pixel to a 1×1 m polygon (Shapely)
2. Dissolve pixel-polygons by cluster into contiguous polygon(s)
3. Compute area_m2 (geom.area) → area_ha = area_m2 / 10000
4. Filter out zones with area_ha < min_zone_size_ha
5. Reset index and reassign cluster IDs consecutively

### Sampling Points

For each zone:

1. Collect coordinates of valid pixels → world coordinates via affine transform
2. Decide number of points = max(points_per_zone, sqrt(#valid_pixels))
3. If n_points ≥ #valid_pixels, take all pixel centers
4. Else, select points via spatial inhibition:
   - Choose a random "seed" pixel
   - Iteratively choose the remaining pixel that maximizes the minimum Euclidean distance to already selected points
5. Create a GeoDataFrame of points with geometry and index values at that pixel

### Zone Statistics

For each zone polygon:

1. Compute area_m2, area_ha, perimeter_m, compactness = 4π·area_m2 / (perimeter_m²)
2. Within that zone mask, compute mean and std of each index

### Visualization

**NDVI map:**
- Mask invalid/outside pixels to NaN
- Plot with "RdYlGn" colormap, masked background in white

**Cluster map:**
- Plot each polygon with a discrete color from "viridis", black outlines
- Draw boundary of entire field in red or blue

**Overview figure:**
- Left: cluster map + sampling points
- Right: bar chart of zone areas (bars colored to match cluster colors)
- Save figures as high-resolution PNG

---

## 📈 Performance Metrics

- **Silhouette Score**: −1 to 1, higher means better cluster separation
- **Calinski–Harabasz Index**: Ratio of between-cluster to within-cluster variance, higher = better
- **Inertia**: Sum of squared distances of samples to their closest cluster center (lower = tighter clusters)
- **Compactness**: Ranges [0, 1], where 1 = perfect circle; measures shape regularity
- **Coverage**: % of field area actually zonified (vs. masked out)

---

## 🔍 Troubleshooting

### Common Issues

**"No valid pixels inside polygon"**
- The input GeoTIFF's nonzero area may not overlap the polygon
- Ensure TIFF and polygon share the same CRS (e.g., both EPSG:32719)
- Check for NaN values: indexing arrays must be finite

**"n_samples < n_clusters" or "Number of distinct clusters < k"**
- If forcing `--force-k` too high relative to pixels, K-Means cannot form k
- Solution: use `--force-k` ≤ #valid_pixels or rely on automatic selection (no `--force-k`)

**All zones filtered out**
- If `min_zone_size_ha` > actual zone sizes (e.g., tiny test images), reduce `--min-zone-size`
- For very small fields, try `--min-zone-size 0.0001` (0.0001 ha = 1 m²)

**MemoryError / Out of Memory**
- Split large TIFF into smaller tiles, process separately
- Increase machine RAM or adjust `ZONING_MAX_MEMORY_GB` if available

**DeprecationWarning: unary_union**
- In newer GeoPandas/Shapely, use `zones.union_all()` instead of `zones.unary_union`
- Tests ignore this warning via filterwarnings in pytest.ini

### Error Codes

- **ValidationError**: Input indices missing or invalid (e.g., all NaNs)
- **ProcessingError**: Any intermediate step failed (mask creation, clustering, sampling)
- **ZonificationError**: Generic top-level exception

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository and create a new branch:**
   ```bash
   git checkout -b feature/my-change
   ```

2. **Run tests locally to ensure nothing breaks:**
   ```bash
   pytest -q
   ```

3. **Follow the coding style:**
   - `black` for formatting (`black src/`)
   - `flake8` for linting (`flake8 src/`)
   - Docstrings should follow NumPy or Google style

4. **Submit a Pull Request (PR) with a clear description of your changes**
   - Reference any related issue numbers
   - Ensure CI passes (unit tests, integration tests)

### Review & Merge

- A maintainer will review your PR
- Once approved, it will be merged into main

For more details, see CONTRIBUTING.md in the repo.

---

## 📄 License

This project is licensed under the MIT License. See LICENSE for full text.

---

## 🏢 About AustralMetrics

AustralMetrics is a leading agtech company focusing on AI-powered agricultural solutions. Pascal Zoning is part of our precision-agriculture software suite, enabling data-driven farm management.

- **Website**: https://australmetrics.com
- **Contact**: info@australmetrics.com

### Other projects:
- pascal-ndvi-block
- crop-prediction-ai

---

## 📚 Related Standards

This project follows **ISO 42001: AI Management Systems** guidelines in:

### Traceability
- Every run logs detailed events with timestamps (Loguru)

### Dependency & Version Documentation
- requirements.txt and requirements-dev.txt list explicit versions

### Reproducible Procedures
- Full pipeline exposed via CLI, API, and automated tests (unit & integration)

### Quality Control
- Comprehensive test suite ensures each module behaves as expected
- Continuous integration can be configured to run pytest

### Change Tracking
- Maintain a CHANGELOG.md (optional) with version history and release notes

For more information on ISO 42001 compliance, refer to official documentation:
- **ISO 42001 – Artificial Intelligence Management System**
- International Organization for Standardization
- https://www.iso.org/standard/77566.html

---

**Thank you for using Pascal Zoning!**

For questions or issues, please open a GitHub Issue or contact info@australmetrics.com.

