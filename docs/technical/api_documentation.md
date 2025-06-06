# API Documentation

This document describes the public Python API of Pascal Zoning ML, detailing classes, methods, and data structures that users can invoke programmatically.

---

## 1. Introduction

Welcome to the API documentation for **Pascal Zoning ML**. This guide is designed for developers who want to integrate or extend the core functionality of the zoning system within their own Python applications. It covers:

- An overview of available classes and data structures.
- Usage patterns and code snippets.
- Error handling best practices.
- Integration examples with other geospatial workflows (e.g., pascal-ndvi-block).

Use this documentation to understand how to:
- Instantiate the main `AgriculturalZoning` engine.
- Run the full zoning pipeline programmatically.
- Access and interpret clustering metrics and zone statistics.
- Customize or extend specific steps (e.g., sampling, visualization).

Subsequent sections dive into installation, package structure, detailed method references, and examples. If you are looking for quick CLI usage, refer back to `simple_usage.md` or `basic_usage.md` in the `docs/` directory.

---
## 2. Installation

Before using the Python API, ensure that Pascal Zoning ML and its dependencies are installed in your environment. You can install the package in editable mode (recommended for development) or from PyPI (when a release is published).

### 2.1. Clone Repository (Development)

```bash
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml
```

### 2.2. Create and Activate a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment named "venv"
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2.3. Install Core Dependencies

All core requirements are listed in `requirements.txt`. For development (including linting and testing), install `requirements-dev.txt`.

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (linters, type checkers, test frameworks)
pip install -r requirements-dev.txt
```

### 2.4. Install Pascal Zoning ML Package

#### 2.4.1. Editable Mode (Recommended for Contributors)

```bash
pip install -e .
```
This ensures that changes made in the src/pascal_zoning/ directory are immediately reflected without reinstallation.

#### 2.4.2. From PyPI (When Released)

Once Pascal Zoning ML is published to PyPI, you can install via:

```bash
pip install pascal-zoning-ml
```

### 2.5. Verify Installation

After installation, verify that you can import the main module and check its version:

```bash
python - <<EOF
import pascal_zoning
from pascal_zoning import __version__  # if __version__ is defined in __init__.py
print("Pascal Zoning ML version:", __version__)
EOF
```
If no errors occur, the package is installed correctly and ready for API usage.

## 3. Package Structure

The Pascal Zoning ML package follows a standard Python project layout, with source code under `src/pascal_zoning/`. Below is the top-level directory tree and brief descriptions of each module:

# Agricultural Zoning ML - Project Structure

```
agricultural-zoning-ml/
├── src/
│   └── pascal_zoning/
│       ├── __init__.py
│       ├── zoning.py              # Core pipeline implementation (masking, clustering, sampling, stats)
│       ├── pipeline.py            # CLI entrypoint using Typer (defines "run" command, logging, argument parsing)
│       ├── config.py              # Optional configuration loader (e.g., reading config.yaml or environment variables)
│       ├── logging_config.py      # Loguru logger setup and formatting
│       ├── interface.py           # Typed data structures, protocol definitions, and helper functions for type validation
│       └── viz.py                 # Visualization functions (maps, bar charts, overview figures)
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies (pytest, mypy, flake8, etc.)
├── pytest.ini                    # pytest configuration (test discovery, filterwarnings)
├── mypy.ini                      # mypy static-typing configuration
├── pyproject.toml                # Project metadata, build system (setuptools)
├── setup.cfg                     # (Optional) setuptools configuration, flake8/black settings
├── CHANGELOG.md                  # Change history (semantic version entries)
├── CODE_OF_CONDUCT.md           # Contributor guidelines and community standards
├── LICENSE.md                   # Project license (MIT)
└── docs/
    ├── simple_usage.md          # Quick CLI example for power users
    ├── basic_usage.md           # Basic command-line and Python API usage
    ├── advanced_examples.md     # Advanced configuration and custom workflows
    ├── api_documentation.md     # (Under construction) Public Python API reference outline
    └── …                        # Other documentation files (e.g., SECURITY.md, TECHDEBT.md)
```


### 3.1. `zoning.py`

- **Purpose:** Implements the core agricultural zoning functionality:
  1. `create_mask()`: generate boolean mask from input polygon and spectral‐index arrays
  2. `prepare_feature_matrix()`: stack, impute, scale (and PCA if requested) to create a feature matrix
  3. `perform_clustering()`: run KMeans, compute clustering metrics (`ClusterMetrics`), store cluster labels
  4. `extract_zone_polygons()`: convert each cluster‐labeled pixel to a polygon, dissolve by cluster ID
  5. `filter_small_zones()`: remove zones smaller than `min_zone_size_ha`, reindex clusters
  6. `generate_sampling_points()`: spatial inhibition sampling within each zone, produce `samples_gdf`
  7. `compute_zone_statistics()`: compute `ZoneStats` (area, perimeter, compactness, mean/std per index)
  8. `save_results()`: persist GeoPackage (zones, samples), CSV (zone stats), JSON (metrics), and folder structure
  9. `visualize_results()`: generate and save PNGs (`mapa_ndvi.png`, `mapa_clusters.png`, `zonificacion_results.png`)

- **Key Classes/Dataclasses:**
  - `ClusterMetrics`: Holds clustering quality metrics (`n_clusters`, `silhouette`, `calinski_harabasz`, `inertia`, `cluster_sizes`, `timestamp`)
  - `ZoneStats`: Holds per‐zone statistics (`zone_id`, `area_ha`, `perimeter_m`, `compactness`, `mean_values`, `std_values`)
  - `ZoningResult`: Aggregates final outputs (`zones: GeoDataFrame`, `samples: GeoDataFrame`, `metrics: ClusterMetrics`, `stats: List[ZoneStats]`)
  - Exceptions: `ZonificationError` (base), `ValidationError`, `ProcessingError`

### 3.2. `pipeline.py`

- **Purpose:** Defines the Typer-based CLI `pascal_zoning.pipeline`. Parses command-line arguments, initializes the `AgriculturalZoning` engine, and invokes `run_pipeline()`.
- **Commands & Options:**
  - `run`: Main subcommand to execute a full zoning workflow
    - `--raster <path>` (required): path to a clipped GeoTIFF
    - `--indices <comma-separated>` (required): list of spectral indices (e.g., `NDVI,NDWI,NDRE,SI`)
    - `--output-dir <path>` (required): base folder for timestamped subfolder
    - `--force-k <int>` (optional): override for number of clusters
    - `--min-zone-size-ha <float>` (optional): minimum area threshold in hectares
    - `--max-zones <int>` (optional): maximum number of clusters to evaluate
    - `--use-pca` (flag): enable PCA on feature matrix
    - `--crs <string>` (optional): force a CRS if not inferable from inputs
- **Logging:** Configures Loguru via `logging_config.py` and prints progress, warnings, and errors to console.

### 3.3. `config.py` (Optional)

- **Purpose:** Load configuration from a `config.yaml` file or environment variables.
- **Typical Responsibilities:**
  - Provide a function like `load_config(path: Path) -> dict` that reads YAML and merges values with environment variables
  - Validate required keys (e.g., `min_zone_size_ha`, `max_zones`, etc.)
  - Expose a single `Config` dataclass or dictionary used by `pipeline.py` to set default values for CLI flags

### 3.4. `logging_config.py`

- **Purpose:** Centralize Loguru configuration (format, level, sinks).
- **Key Features:**
  - Define a default format string (timestamp, level, message)
  - Optionally read a `ZONING_LOG_LEVEL` environment variable
  - Attach console and/or file sinks

### 3.5. `interface.py` (Optional)

- **Purpose:** Provide type-hinted protocols, helper functions, or schemas for validating input data structures.
- **Possible Contents:**
  - Pydantic models or TypedDicts for manifest parsing (if JSON schemas are used)
  - Helper functions like `validate_indices_dict(indices: Dict[str, np.ndarray]) -> None` that raise `ValidationError`

### 3.6. `viz.py`

- **Purpose:** Contains reusable plotting functions using Matplotlib for visualizing zones and sampling points.
- **Key Functions:**
  - `zoning_overview(zones: GeoDataFrame, samples: GeoDataFrame, out_png: Path) -> None`: Creates a two-panel figure (cluster map + bar chart of area) and saves to PNG.
  - Additional helper functions for custom plot styling (e.g., color palettes, saving with high DPI).

---

Each Python module in `src/pascal_zoning/` is installed under the same namespace (`import pascal_zoning.zoning`, `import pascal_zoning.pipeline`, etc.). When you install the package (editable or via PyPI), this directory structure is the only code users need to interact with. Other top-level files (e.g., `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `LICENSE.md`, `pytest.ini`, `mypy.ini`, etc.) reside next to `src/` and support CI/testing, documentation, and project governance.

# Agricultural Zoning ML - Project Structure

```
agricultural-zoning-ml/
├── src/
│   └── pascal_zoning/
│       ├── __init__.py
│       ├── zoning.py              # Core pipeline implementation (masking, clustering, sampling, stats)
│       ├── pipeline.py            # CLI entrypoint using Typer (defines "run" command, logging, argument parsing)
│       ├── config.py              # Optional configuration loader (e.g., reading config.yaml or environment variables)
│       ├── logging_config.py      # Loguru logger setup and formatting
│       ├── interface.py           # Typed data structures, protocol definitions, and helper functions for type validation
│       └── viz.py                 # Visualization functions (maps, bar charts, overview figures)
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies (pytest, mypy, flake8, etc.)
├── pytest.ini                    # pytest configuration (test discovery, filterwarnings)
├── mypy.ini                      # mypy static-typing configuration
├── pyproject.toml                # Project metadata, build system (setuptools)
├── setup.cfg                     # (Optional) setuptools configuration, flake8/black settings
├── CHANGELOG.md                  # Change history (semantic version entries)
├── CODE_OF_CONDUCT.md           # Contributor guidelines and community standards
├── LICENSE.md                   # Project license (MIT)
└── docs/
    ├── simple_usage.md          # Quick CLI example for power users
    ├── basic_usage.md           # Basic command-line and Python API usage
    ├── advanced_examples.md     # Advanced configuration and custom workflows
    ├── api_documentation.md     # (Under construction) Public Python API reference outline
    └── …                        # Other documentation files (e.g., SECURITY.md, TECHDEBT.md)
```

## 4. Core Exceptions

All custom exceptions inherit from `ZonificationError`, allowing users to catch and handle zoning-related errors at different levels:

```python
class ZonificationError(Exception):
    """Base exception for all zoning-related errors."""
    pass

class ValidationError(ZonificationError):
    """Raised when input spectral indices or parameters are invalid."""
    pass

class ProcessingError(ZonificationError):
    """Raised when any step of the zoning pipeline encounters a problem."""
    pass
```

### ZonificationError
Base class for every exception in this module. Use to catch any issue arising from the zoning workflow.

### ValidationError
Thrown when inputs (e.g., spectral index arrays, polygon type, configuration parameters) fail validation checks.

**Example scenarios:**
- Missing required indices in the input dictionary.
- Indices arrays having mismatched shapes.
- Out‐of‐range or nonsensical parameter values (like a negative `min_zone_size_ha`).

### ProcessingError
Raised for runtime failures during pipeline execution:
- No valid pixels found after masking.
- K-Means clustering cannot proceed (e.g., too few samples for a given k).
- Zone extraction yields zero valid polygons.
- Sampling point generation fails because a zone has insufficient area for the desired number of points.

### Usage Suggestion

When invoking any method of `AgriculturalZoning`, wrap calls in a try/except block to handle these exceptions gracefully. For example:

```python
from pascal_zoning.zoning import AgriculturalZoning, ValidationError, ProcessingError

zoning = AgriculturalZoning(random_state=0, min_zone_size_ha=0.1, max_zones=5)

try:
    result = zoning.run_pipeline(
        indices=indices_dict,
        bounds=field_polygon,
        points_per_zone=5,
        crs="EPSG:32719",
    )
    # Proceed with using result.zones, result.samples, etc.
except ValidationError as ve:
    print(f"Input validation failed: {ve}")
    # Perform corrective actions (e.g., notify user, adjust inputs)
except ProcessingError as pe:
    print(f"Processing error during zoning: {pe}")
    # Log error, possibly retry with different parameters
except ZonificationError:
    print("A general zoning error occurred.")
    # This will catch any other unexpected zoning-related issues
```

By distinguishing between `ValidationError` and `ProcessingError`, you can provide more targeted error handling:

- **Recoverable**: If it's a `ValidationError`, inform the user about incorrect inputs.
- **Runtime failure**: If it's a `ProcessingError`, log detailed diagnostics or attempt fallback strategies (e.g., adjust `min_zone_size_ha` or drop PCA).
- **Catch‐all**: Use `ZonificationError` as a safeguard for any unanticipated issues within the zoning module.

# Agricultural Zoning ML - Project Structure

```
agricultural-zoning-ml/
├── src/
│   └── pascal_zoning/
│       ├── __init__.py
│       ├── zoning.py              # Core pipeline implementation (masking, clustering, sampling, stats)
│       ├── pipeline.py            # CLI entrypoint using Typer (defines "run" command, logging, argument parsing)
│       ├── config.py              # Optional configuration loader (e.g., reading config.yaml or environment variables)
│       ├── logging_config.py      # Loguru logger setup and formatting
│       ├── interface.py           # Typed data structures, protocol definitions, and helper functions for type validation
│       └── viz.py                 # Visualization functions (maps, bar charts, overview figures)
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies (pytest, mypy, flake8, etc.)
├── pytest.ini                    # pytest configuration (test discovery, filterwarnings)
├── mypy.ini                      # mypy static-typing configuration
├── pyproject.toml                # Project metadata, build system (setuptools)
├── setup.cfg                     # (Optional) setuptools configuration, flake8/black settings
├── CHANGELOG.md                  # Change history (semantic version entries)
├── CODE_OF_CONDUCT.md           # Contributor guidelines and community standards
├── LICENSE.md                   # Project license (MIT)
└── docs/
    ├── simple_usage.md          # Quick CLI example for power users
    ├── basic_usage.md           # Basic command-line and Python API usage
    ├── advanced_examples.md     # Advanced configuration and custom workflows
    ├── api_documentation.md     # (Under construction) Public Python API reference outline
    └── …                        # Other documentation files (e.g., SECURITY.md, TECHDEBT.md)
```

## 4. Core Exceptions

All custom exceptions inherit from `ZonificationError`, allowing users to catch and handle zoning-related errors at different levels:

```python
class ZonificationError(Exception):
    """Base exception for all zoning-related errors."""
    pass

class ValidationError(ZonificationError):
    """Raised when input spectral indices or parameters are invalid."""
    pass

class ProcessingError(ZonificationError):
    """Raised when any step of the zoning pipeline encounters a problem."""
    pass
```

### ZonificationError
Base class for every exception in this module. Use to catch any issue arising from the zoning workflow.

### ValidationError
Thrown when inputs (e.g., spectral index arrays, polygon type, configuration parameters) fail validation checks.

**Example scenarios:**
- Missing required indices in the input dictionary.
- Indices arrays having mismatched shapes.
- Out‐of‐range or nonsensical parameter values (like a negative `min_zone_size_ha`).

### ProcessingError
Raised for runtime failures during pipeline execution:
- No valid pixels found after masking.
- K-Means clustering cannot proceed (e.g., too few samples for a given k).
- Zone extraction yields zero valid polygons.
- Sampling point generation fails because a zone has insufficient area for the desired number of points.

### Usage Suggestion

When invoking any method of `AgriculturalZoning`, wrap calls in a try/except block to handle these exceptions gracefully. For example:

```python
from pascal_zoning.zoning import AgriculturalZoning, ValidationError, ProcessingError

zoning = AgriculturalZoning(random_state=0, min_zone_size_ha=0.1, max_zones=5)

try:
    result = zoning.run_pipeline(
        indices=indices_dict,
        bounds=field_polygon,
        points_per_zone=5,
        crs="EPSG:32719",
    )
    # Proceed with using result.zones, result.samples, etc.
except ValidationError as ve:
    print(f"Input validation failed: {ve}")
    # Perform corrective actions (e.g., notify user, adjust inputs)
except ProcessingError as pe:
    print(f"Processing error during zoning: {pe}")
    # Log error, possibly retry with different parameters
except ZonificationError:
    print("A general zoning error occurred.")
    # This will catch any other unexpected zoning-related issues
```

By distinguishing between `ValidationError` and `ProcessingError`, you can provide more targeted error handling:

- **Recoverable**: If it's a `ValidationError`, inform the user about incorrect inputs.
- **Runtime failure**: If it's a `ProcessingError`, log detailed diagnostics or attempt fallback strategies (e.g., adjust `min_zone_size_ha` or drop PCA).
- **Catch‐all**: Use `ZonificationError` as a safeguard for any unanticipated issues within the zoning module.

## 5. The `AgriculturalZoning` Class

This class encapsulates the entire zoning pipeline, exposing methods to configure, execute, and retrieve results. Users typically interact with `AgriculturalZoning` either via the CLI wrapper (`pipeline.py`) or programmatically via its public methods.

### 5.1 Overview

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
        Initialize an AgriculturalZoning instance.

        Args:
            random_state (int): Seed for reproducibility (affects KMeans & sampling).
            min_zone_size_ha (float): Minimum area (in hectares) for a valid zone.
            max_zones (int): Maximum number of clusters to evaluate automatically.
            output_dir (Optional[Path]): Default directory to save outputs (can be overridden).
        """
```

**random_state**  
Controls randomness in K-Means initialization and sampling. Passing a fixed integer ensures reproducible behavior.

**min_zone_size_ha**  
Filters out any cluster whose final polygon area is below this threshold (hectares). Smaller values allow very fine-grained zones.

**max_zones**  
When automatic cluster‐count selection is used (no force_k), the algorithm evaluates k = 2 up to k = max_zones via Silhouette and Calinski–Harabasz metrics.

**output_dir**  
Default directory where all output artifacts—GeoPackages, CSV, JSON, and PNG figures—will be written. If omitted here, must be supplied in run_pipeline().

### 5.2 Constructor & Attributes

Upon instantiation, the following internal attributes are initialized (simplified view):

**Preprocessing Components**

```python
self.scaler = StandardScaler()       # Standardizes features to zero mean / unit variance
self.pca = PCA(n_components=0.95)    # Reduces dimensionality, retaining 95% variance
self.imputer = SimpleImputer(strategy="median")  # Fills missing values with median
```

**Internal State Placeholders**

```python
self.indices: Dict[str, np.ndarray] = {}          # Spectral indices (2D arrays)
self.valid_mask: Optional[np.ndarray] = None      # Boolean mask of valid pixels
self.features_array: Optional[np.ndarray] = None  # Flattened, preprocessed feature matrix
self.cluster_labels: Optional[np.ndarray] = None  # 2D array of cluster IDs (float64)
self.n_clusters_opt: Optional[int] = None         # Chosen number of clusters
self.zones_gdf: Optional[gpd.GeoDataFrame] = None # Dissolved polygons per cluster
self.samples_gdf: Optional[gpd.GeoDataFrame] = None  # Sampling points GeoDataFrame
self.metrics: Optional[ClusterMetrics] = None        # Quality metrics dataclass
self.zone_stats: List[ZoneStats] = []                # Computed statistics per zone
self.crs: Optional[str] = None                       # Coordinate Reference System
self.transform: Optional[Affine] = None               # Affine transform object
self.width: Optional[int] = None                      # Raster width (pixels)
self.height: Optional[int] = None                     # Raster height (pixels)
```

**Logger Initialization**

```python
self.logger = logging.getLogger("AgriculturalZoning")
```

Controls all informational, warning, and error messages during pipeline execution.

### 5.3 Public Methods

#### 5.3.1 run_pipeline

```python
def run_pipeline(
    self,
    indices: Dict[str, np.ndarray],
    bounds: BaseGeometry,
    points_per_zone: int,
    crs: str,
    force_k: Optional[int] = None,
    use_pca: bool = False,
    output_dir: Optional[Path] = None
) -> ZoningResult:
    """
    Execute the full zoning pipeline:
      1. Validate inputs & initialize spatial metadata
      2. Create mask (inside polygon & non‐NaN)
      3. Prepare feature matrix (impute, scale, optional PCA)
      4. Perform clustering (KMeans) → cluster_labels + metrics
      5. Extract zone polygons → dissolve, compute areas
      6. Filter small zones (< min_zone_size_ha)
      7. Compute per‐zone statistics (area, perimeter, compactness, spectral mean/std)
      8. Generate sampling points (spatial inhibition per zone)
      9. Save all outputs (GPkg, CSV, JSON, PNG) if `output_dir` is set
    Args:
        indices (Dict[str, np.ndarray]): Mapping of index name → 2D numpy array
        bounds (BaseGeometry): Shapely polygon/MultiPolygon for the field boundary
        points_per_zone (int): Minimum sampling points per zone
        crs (str): Coordinate reference system (e.g., "EPSG:32719")
        force_k (Optional[int]): If set, force KMeans to use exactly this k (overrides automatic selection)
        use_pca (bool): If True, perform PCA in `prepare_feature_matrix()`
        output_dir (Optional[Path]): Directory where all files will be saved (overrides instance default)
    Returns:
        ZoningResult: Dataclass containing zones, samples, metrics, and stats
    Raises:
        ProcessingError: If any intermediate step fails (e.g., no valid pixels, clustering errors, zero zones)
    """
```

**indices**  
Keys must match the names used later in visualization and statistics (e.g., "NDVI", "NDRE"). Arrays must share the same (height, width) shape.

**bounds**  
A Shapely Polygon or MultiPolygon that fully encloses the nonzero area of the raster. Used to generate valid_mask.

**crs**  
String representation of the coordinate system, passed along to all GeoDataFrames (e.g., "EPSG:32719").

**force_k**  
If None, select_optimal_clusters() is called; otherwise, perform_clustering() uses the provided integer.

**Behavior on Failure**  
The method wraps each stage in try/except blocks. If a ProcessingError is raised at any stage, log an error and bubble it up.

#### 5.3.2 create_mask

```python
def create_mask(self) -> None:
    """
    Generate a boolean mask that identifies pixels inside the polygon AND without NaN values.
    Steps:
      1. Validate that `self.bounds`, `self.indices` (non-empty), `self.transform`, `self.width`, and `self.height` are initialized.
      2. Rasterize the polygon into a boolean mask (`mask_poly`).
      3. Stack index arrays and identify NaN pixels (`valid_data_mask`).
      4. Combine polygon mask & valid-data mask → `self.valid_mask`.
      5. Log counts: pixels inside field, with data, and final valid count.
      6. Raise `ProcessingError` if zero valid pixels found.
    Raises:
      ProcessingError: On missing inputs or zero valid pixels.
    """
```

**Outputs**  
`self.valid_mask`: a (height, width) boolean array where True indicates the pixel is both inside bounds and non‐NaN across all indices.

#### 5.3.3 prepare_feature_matrix

```python
def prepare_feature_matrix(self, use_pca: bool = False) -> None:
    """
    Build the feature matrix for clustering:
      1. Stack 2D index arrays into a 3D array `(H, W, N_indices)`.
      2. Filter by `self.valid_mask` → obtain a 2D "valid pixels" subset.
      3. Impute missing values (median) using `self.imputer`.
      4. Scale features (zero mean, unit variance) using `self.scaler`.
      5. If `use_pca` is True, apply `self.pca.fit_transform()` on scaled data.
      6. Store the final `(n_valid_pixels, n_features)` array in `self.features_array`.
    Raises:
      ProcessingError: If called before `create_mask()` (i.e., `self.valid_mask` is None) or if no valid pixels.
    """
```

**Optional PCA**  
If use_pca=True, dimensionality is reduced; otherwise, PCA is skipped. The boolean flag use_pca comes from run_pipeline() arguments.

#### 5.3.4 select_optimal_clusters

```python
def select_optimal_clusters(self) -> int:
    """
    Evaluate KMeans for k in [2, self.max_zones] on `self.features_array`.
    1. For each k:
         - Fit KMeans(n_clusters=k, random_state=self.random_state).
         - Compute Silhouette Score and Calinski–Harabasz Index.
         - Record inertia (sum of squared distances).
    2. Track the best silhouette score; choose corresponding k.
    3. Log metrics for each k and final selected k.
    Returns:
        best_k (int): The cluster count with highest silhouette score.
    Raises:
        ProcessingError: If `self.features_array` is None or contains too few samples.
    """
```

**Outputs**  
Returns the integer k that maximizes silhouette. Called internally by perform_clustering() when force_k is None.

#### 5.3.5 perform_clustering

```python
def perform_clustering(self, force_k: Optional[int] = None) -> None:
    """
    Perform the K-Means clustering step:
      1. Determine k:
           - If `force_k` is provided, use it.
           - Otherwise, call `select_optimal_clusters()`.
      2. Fit KMeans(n_clusters=k, random_state=self.random_state) on `self.features_array`.
      3. Generate a 2D cluster label array (`clusters_img`) of shape `(height, width)`:
           - Initialize all values to -1.
           - Assign predicted labels to `clusters_img[valid_mask]`.
           - Convert to float64 and store in `self.cluster_labels`.
      4. Compute clustering metrics:
           - `silhouette_score`, `calinski_harabasz_score`, and `inertia`.
           - Build `ClusterMetrics(n_clusters=k, silhouette=…, calinski_harabasz=…, inertia=…, cluster_sizes={…}, timestamp=…)`.
           - Store metrics in `self.metrics`.
      5. Log summary: total pixels, valid pixels, labeled pixels, and metrics.
    Raises:
      ProcessingError: If `self.features_array` or spatial metadata is not initialized, or if KMeans fails (e.g., too few samples for k).
    """
```

**Cluster Label Array**  
`self.cluster_labels`: 2D float64 array, with cluster IDs for valid pixels and -1 for outside/invalid.

**ClusterMetrics Dataclass**

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

Includes per‐cluster sample counts and a timestamp of when clustering was completed.

#### 5.3.6 extract_zone_polygons

```python
def extract_zone_polygons(self) -> None:
    """
    Convert the 2D `self.cluster_labels` array into vector polygons:
      1. Loop over each pixel (row, col):
           - If label >= 0: compute world‐coordinates corners using `self.transform`.
           - Build a 1×1‐meter polygon for that pixel.
           - Add a record {"cluster": label, "geometry": Polygon} to a temporary list.
      2. Create a GeoDataFrame `gdf_pixels` with all pixel‐level polygons.
      3. Dissolve by "cluster" to merge adjacent pixels into contiguous zone polygons.
      4. Reset index, yielding `self.zones_gdf` with columns `["cluster", "geometry"]`.
      5. Log the number of zones extracted.
    Raises:
      ProcessingError: If `self.cluster_labels` or `self.transform` or `self.crs` is not initialized, or if no pixel‐polygons are generated.
    """
```

**Output**  
`self.zones_gdf`: GeoDataFrame with columns: `cluster` (int), `geometry` (Shapely Polygon).

Post‐extraction, each row corresponds to a management zone.

#### 5.3.7 filter_small_zones

```python
def filter_small_zones(self) -> None:
    """
    Remove any zone whose area (in hectares) is below `self.min_zone_size_ha`:
      1. Compute `area_m2 = geometry.area` for each zone.
      2. Compute `area_ha = area_m2 / 10000.0`.
      3. Filter `self.zones_gdf` to keep only rows with `area_ha >= min_zone_size_ha`.
      4. Reset index, reassign `cluster` IDs consecutively (0, 1, 2, …).
      5. Log how many zones were filtered out vs. retained.
    Raises:
      ProcessingError: If `self.zones_gdf` is not initialized (i.e., `extract_zone_polygons()` was not called).
    """
```

**Effect on cluster_labels**  
After filtering, some cluster IDs may no longer exist. Currently, cluster_labels is not re‐mapped; downstream steps rely only on self.zones_gdf.

#### 5.3.8 compute_zone_statistics

```python
def compute_zone_statistics(self) -> None:
    """
    Calculate statistics for each zone in `self.zones_gdf`:
      1. For each row in `self.zones_gdf`:
           - `zone_id = int(cluster)`
           - `geometry`: compute `area_m2 = geom.area` → `area_ha = area_m2 / 10000.0`
           - `perimeter_m = geom.length`
           - `compactness = 4 * π * area_m2 / (perimeter_m ** 2)` (if `perimeter_m > 0` else 0)
           - Build `zone_mask = (self.cluster_labels == zone_id)`
           - For each index name & array in `self.indices`:
               - Extract `vals = array[zone_mask]`
               - Compute `mean = np.nanmean(vals)` and `std = np.nanstd(vals)`
           - Construct a `ZoneStats(zone_id, area_ha, perimeter_m, compactness, mean_values, std_values)`
           - Append to `self.zone_stats` list.
      2. Log that statistics have been computed for all zones.
    Raises:
      ProcessingError: If `self.zones_gdf` or `self.cluster_labels` is not initialized.
    """
```

**ZoneStats Dataclass**

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

Holds per‐zone geometric and spectral summary.

#### 5.3.9 generate_sampling_points

```python
def generate_sampling_points(self, points_per_zone: int) -> None:
    """
    Generate sampling points within each zone using a spatial inhibition algorithm:
      1. For each `zone_id` in `self.zones_gdf["cluster"]`:
           - `zone_mask = (self.cluster_labels == zone_id)`
           - `ys, xs = np.where(zone_mask)` → pixel coordinates
           - Convert pixel coordinates → world (x, y) via `self._pixel_to_world_coords()`
           - Determine `n_points = max(points_per_zone, int(sqrt(#pixels_in_zone)))`
           - If `n_points >= #pixels`: choose all pixel centers
             Else:
               a. Randomly pick one "seed" pixel index
               b. Iteratively choose the next pixel that maximizes the minimum Euclidean distance to all already-selected points
           - For each selected pixel index:
               - Build a Shapely `Point(xw, yw)`
               - Extract spectral values at that pixel for each index name
               - Add a record to `samples_list`: `{"geometry": Point, "cluster": zone_id, <index_name>: value, …}`
      2. Create `self.samples_gdf = GeoDataFrame(samples_list, crs=self.crs)`
      3. Log the number of points generated.
    Raises:
      ProcessingError: If no zones exist (`self.zones_gdf` is None) or if `self.cluster_labels`, `self.transform`, or `self.crs` are missing. Also raises if no sampling points could be placed in any zone.
    """
```

**Output**  
`self.samples_gdf`: GeoDataFrame with columns: `geometry` (Shapely Point), `cluster` (int), then one column per index (e.g., "NDVI", "NDRE") containing the spectral value at that location.

#### 5.3.10 save_results

```python
def save_results(self, output_dir: Optional[Path] = None) -> None:
    """
    Persist all major outputs to disk under `output_dir`:
      1. Create `output_dir` if not existing.
      2. If `self.zones_gdf` exists:
           - Save to GeoPackage: `<output_dir>/zonificacion_agricola.gpkg` (layer "zonas").
      3. If `self.samples_gdf` exists:
           - Save to GeoPackage: `<output_dir>/puntos_muestreo.gpkg` (layer "muestras").
      4. If `self.zone_stats` exists:
           - Construct a pandas DataFrame from `ZoneStats` list.
           - Save to CSV: `<output_dir>/estadisticas_zonas.csv`.
      5. If `self.metrics` exists:
           - Serialize to JSON: `<output_dir>/metricas_clustering.json`.
      6. Log each file path written.
    """
```

**File Naming Conventions**
- GeoPackage filenames: `zonificacion_agricola.gpkg`, `puntos_muestreo.gpkg`
- CSV: `estadisticas_zonas.csv`
- JSON: `metricas_clustering.json`

#### 5.3.11 visualize_results

```python
def visualize_results(self) -> None:
    """
    Generate and save PNG maps to `self.output_dir`:
      1. **NDVI Map** (if "NDVI" in `self.indices`):
           - Mask out-of-field or NaN pixels → `ndvi_masked`.
           - Plot with "RdYlGn" colormap; white for invalid areas.
           - Overlay field boundary from `self.gdf_predio`.
           - Save as `<output_dir>/mapa_ndvi.png`.
      2. **Cluster Map** (if `self.zones_gdf` exists):
           - Plot each zone polygon colored by `cluster` with "viridis" colormap.
           - Overlay zone boundaries.
           - Save as `<output_dir>/mapa_clusters.png`.
      3. Errors are caught and logged; all figures closed on exception.
    """
```

**Resulting Figures**
- `mapa_ndvi.png`
- `mapa_clusters.png`

### 5.4 Example Usage of AgriculturalZoning (Python API)

```python
from pathlib import Path
import numpy as np
import geopandas as gpd
from pascal_zoning.zoning import AgriculturalZoning, ZoningResult

# Load or generate spectral index arrays (example: NDVI & NDRE; both 2×2)
indices = {
    "NDVI": np.array([[0.1, 0.2],[0.3, 0.4]]),
    "NDRE": np.array([[0.0, 0.1],[0.2, 0.3]])
}

# Load field boundary polygon
field_gdf = gpd.read_file("data/field_boundary.gpkg")
bounds_polygon = field_gdf.geometry.iloc[0]

# Instantiate the zoning engine
zoning = AgriculturalZoning(
    random_state=42,
    min_zone_size_ha=0.00005,
    max_zones=3,
    output_dir=Path("outputs")
)

# Run the complete pipeline (automatic k-selection)
result: ZoningResult = zoning.run_pipeline(
    indices=indices,
    bounds=bounds_polygon,
    points_per_zone=2,
    crs="EPSG:32719",
    force_k=None,       # Let algorithm choose optimal k
    use_pca=False,
    output_dir=Path("outputs")
)

# Access resulting GeoDataFrames & dataclasses
zones_gdf   = result.zones     # Polygons of management zones
samples_gdf = result.samples   # Sampling points with index values
metrics     = result.metrics   # ClusterMetrics: (n_clusters, silhouette, CH, inertia)
stats_list  = result.stats     # List of ZoneStats: per-zone metrics

print(f"Number of zones: {metrics.n_clusters}")
for stat in stats_list:
    print(f"Zone {stat.zone_id} → Area (ha): {stat.area_ha:.6f}, Compactness: {stat.compactness:.4f}")
```

If any stage fails (e.g., ProcessingError), catch exceptions around run_pipeline(...) to inspect the error message and adjust inputs/parameters accordingly.

### 5.5 Notes & Best Practices

**Naming Conventions for Indices**  
The keys of the indices dictionary must match exactly what zoning.py expects later (case‐sensitive). Common examples: "NDVI", "NDWI", "NDRE", "SI".

**CRS Consistency**  
Ensure the input bounds (Shapely polygon) shares the same CRS as the raster used to generate indices. Mismatched CRS will yield incorrect masking and invalid world‐coordinate transforms.

**Parameter Tuning**  
- `min_zone_size_ha`: For small sample or test rasters, set this to a very small value (e.g., 0.00005 ha = 0.5 m²). For production fields, typical values range from 0.1 to 1.0 ha.
- `max_zones`: Larger values increase computation time; limit to a reasonable upper bound.

**Performance Considerations**  
Feature matrix size = n_valid_pixels × n_indices. Very high‐resolution rasters may consume significant memory during scaling and clustering. PCA can reduce dimensionality (faster clustering) but adds overhead. Use use_pca=True only if you have ≥ 3 indices and want to reduce noise.

**Extending or Overriding**  
To add a new index type (e.g., "EVI"), supply the array under key "EVI" in indices and update any plotting or CSV‐export logic in save_results() if needed. To customize sampling (e.g., different inhibition radius), modify generate_sampling_points() accordingly or subclass AgriculturalZoning.

# Pascal Zoning - Other Modules and Utilities

Beyond the core `zoning.py` implementation, the `pascal_zoning` package includes several auxiliary modules that support configuration loading, logging setup, type interfaces, and visualization helpers. This section describes each of these files, their purpose, and the key functions/structures they expose.

## 6.1 `config.py`

This optional module provides a centralized way to load configuration values from a `config.yaml` file or environment variables. It allows users to override default values without modifying code.

```python
# src/pascal_zoning/config.py

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigError(Exception):
    """Raised when configuration cannot be loaded or is invalid."""
    pass

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads configuration from YAML file or environment variables.

    Priority:
      1. If `config_path` is provided and exists, parse it as YAML.
      2. Otherwise, look for `config.yaml` in the current working directory.
      3. Fall back to environment variables prefixed with `ZONING_`.

    Returns:
      A dictionary with keys: 'zoning', 'clustering', 'sampling', 'preprocessing', etc.

    Raises:
      ConfigError: If neither file nor required environment variables are found or YAML is invalid.
    """
    # Example implementation:
    # 1. If config_path is given and exists:
    #      data = yaml.safe_load(config_path.read_text())
    # 2. If not, if ./config.yaml exists:
    #      data = yaml.safe_load(Path("config.yaml").read_text())
    # 3. If not:
    #      data = {}  # We'll try to read from environment variables
    #
    # 4. For each expected config key, override with env var if present:
    #      os.getenv("ZONING_MIN_ZONE_SIZE_HA"), etc.
    #
    # 5. Validate that required keys are present; if not, raise ConfigError.
    #
    # 6. Return consolidated config dictionary.
    pass
```

### Usage in CLI (pipeline.py)

Inside the Typer-based CLI, `config.load_config()` is invoked early. Any flags passed explicitly on the command line override values in `config.yaml` or environment variables.

### Example config.yaml Section

```yaml
zoning:
  min_zone_size_ha: 0.5
  max_zones: 12
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

## 6.2 `logging_config.py`

This module centralizes Loguru logger configuration so that all modules emit consistent log messages, formatted according to ISO 42001 "traceability" guidelines.

```python
# src/pascal_zoning/logging_config.py

from loguru import logger
import sys
import os

def configure_logging():
    """
    Configures the Loguru logger:
      - Reads log level from `ZONING_LOG_LEVEL` environment variable (default: INFO)
      - Adds a console sink with structured format:
          [<timestamp>] <level> | <module> | <message>
      - Optionally adds a file sink if the `ZONING_LOG_FILE` env var is set.
    """
    # 1. Remove default handlers
    logger.remove()

    # 2. Determine log level
    log_level = os.getenv("ZONING_LOG_LEVEL", "INFO").upper()

    # 3. Add console sink
    logger.add(
        sys.stderr,
        level=log_level,
        format="[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] "
               "<level>{level: <8}</level> | "
               "<cyan>{module}</cyan> | <level>{message}</level>"
    )

    # 4. If a LOG_FILE is specified, add file sink
    log_file = os.getenv("ZONING_LOG_FILE")
    if log_file:
        logger.add(
            log_file,
            rotation="10 MB",
            retention="10 days",
            level=log_level,
            serialize=False,  # readable JSON format is optional
        )

# Configure logging automatically on import, so CLI and API code can write logs immediately.
configure_logging()
```

### Behavior
- If `ZONING_LOG_LEVEL` is set (e.g., "DEBUG"), all modules log at that level or higher.
- If `ZONING_LOG_FILE` points to a file path, logs are also appended to that file for permanent audit.

### ISO 42001 Traceability

- Each log record includes precise timestamp, log level, source module, and message.
- File retention policies (e.g., "keep 10 days") ensure logs remain available for audit.

## 6.3 `interface.py`

Defines typed data structures, Protocols, and helper functions for validating inputs/outputs at runtime. This is optional but recommended for strict type safety.

```python
# src/pascal_zoning/interface.py

from typing import Any, Dict, List, Protocol, Union
import numpy as np
from shapely.geometry import Polygon, BaseGeometry

# ------------------------------------------------------------------
# 6.3.1 Protocolo SpectralIndices
# ------------------------------------------------------------------

class SpectralIndices(Protocol):
    """
    Protocolo que especifica el contrato para índices espectrales de entrada:
      - Las claves deben ser strings en mayúsculas (ej., "NDVI", "NDRE", etc.).
      - Cada valor debe ser un numpy.ndarray[float64] 2D.
    """
    def __getitem__(self, name: str) -> np.ndarray: ...
    def keys(self) -> List[str]: ...

def validate_indices(indices: Dict[str, Any]) -> Dict[str, np.ndarray]:
    """
    Verificación en tiempo de ejecución:
      1. Asegurar que `indices` es un dict con al menos una clave.
      2. Para cada (clave, valor):
           - `clave` debe ser un string no vacío en mayúsculas.
           - `valor` debe ser un numpy.ndarray 2D de dtype float64 o convertible a float64.
      3. Lanzar ValueError o TypeError si alguna verificación falla.
      4. Retornar un dict limpio con todos los arrays cast a np.ndarray[np.float64].
    """
    # Ejemplo de esquema:
    #   if not isinstance(indices, dict) or len(indices)==0: raise ValueError
    #   for key, arr in indices.items():
    #       if not (isinstance(key, str) and key.isupper()):
    #           raise TypeError(f"Index name '{key}' must be uppercase string")
    #       try:
    #           np_arr = np.asarray(arr, dtype=np.float64)
    #       except:
    #           raise TypeError(f"Index '{key}' could not be cast to numpy float64 array")
    #       if np_arr.ndim != 2:
    #           raise ValueError(f"Index '{key}' must be 2D array, got ndim={np_arr.ndim}")
    #   return {key: np_arr for key, arr in indices.items()}
    pass

# ------------------------------------------------------------------
# 6.3.2 Protocolo BoundsValidator
# ------------------------------------------------------------------

class BoundsValidator(Protocol):
    """
    Protocolo para entrada de límites geométricos:
      - Debe ser un Shapely Polygon o MultiPolygon.
      - No debe estar vacío.
    """
    def __geo_interface__(self) -> Any: ...

def validate_bounds(bounds: Any) -> BaseGeometry:
    """
    Verificación en tiempo de ejecución:
      1. Asegurar que `bounds` implementa __geo_interface__ o es un Shapely BaseGeometry.
      2. Retornar la geometría si es válida; si no, lanzar TypeError/ValueError.
    """
    pass
```

### Purpose

By enforcing these runtime validations at the beginning of `run_pipeline()`, the pipeline can fail fast if inputs are malformed.

This aligns with the "input validation" requirements of ISO 42001.

## 6.4 `viz.py`

Contains plotting functions to generate standalone figures or combined summary plots, used by `visualize_results()`.

```python
# src/pascal_zoning/viz.py

from pathlib import Path
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from loguru import logger

def zoning_overview(
    zones: gpd.GeoDataFrame,
    samples: gpd.GeoDataFrame,
    out_png: Path
) -> None:
    """
    Dibuja una figura de dos paneles:
      1. Panel izquierdo: polígonos de cluster coloreados por `cluster` con `samples` superpuestos (puntos negros).
      2. Panel derecho: gráfico de barras de áreas de zona (ha), cada barra coloreada para coincidir con la zona correspondiente.
    Guarda la figura combinada en `out_png`.
    """
    fig, (ax_map, ax_bar) = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor("white")
    ax_map.set_facecolor("white")
    ax_bar.set_facecolor("white")

    # --- Panel 1: Mapa de Zonas + Muestras ---
    if not zones.empty:
        # Determinar límites totales
        xmin, ymin, xmax, ymax = zones.total_bounds
        margin_x = (xmax - xmin) * 0.05
        margin_y = (ymax - ymin) * 0.05

        # Generar colores discretos desde "tab10"
        n_zones = len(zones)
        cmap = plt.get_cmap("tab10")
        colors = [cmap(i) for i in range(n_zones)]

        # Plotear cada zona manualmente para controlar el color
        for idx, row in zones.iterrows():
            cluster_id = int(row["cluster"])
            poly = row.geometry
            color = colors[cluster_id]
            if isinstance(poly, MultiPolygon):
                for part in poly.geoms:
                    x, y = part.exterior.xy
                    ax_map.fill(x, y, facecolor=color, edgecolor="black", linewidth=0.5)
                    for hole in part.interiors:
                        hx, hy = hole.xy
                        ax_map.fill(hx, hy, facecolor="white")
            elif isinstance(poly, Polygon):
                x, y = poly.exterior.xy
                ax_map.fill(x, y, facecolor=color, edgecolor="black", linewidth=0.5)
                for hole in poly.interiors:
                    hx, hy = hole.xy
                    ax_map.fill(hx, hy, facecolor="white")

        # Dibujar límites de zona
        boundary = gpd.GeoDataFrame(geometry=[zones.unary_union], crs=zones.crs)
        boundary.boundary.plot(ax=ax_map, color="black", linewidth=1)

        ax_map.set_xlim(xmin - margin_x, xmax + margin_x)
        ax_map.set_ylim(ymin - margin_y, ymax + margin_y)
        ax_map.set_xticks([])
        ax_map.set_yticks([])
        ax_map.set_title("Vista General de Zonificación")

    # Plotear puntos de muestreo si están presentes
    if not samples.empty:
        samples.plot(ax=ax_map, color="black", markersize=5)

    # --- Panel 2: Gráfico de Barras de Áreas de Zona ---
    if not zones.empty:
        if "area_ha" not in zones.columns:
            zones["area_ha"] = zones.geometry.area / 10000.0
        zones_sorted = zones.sort_values("cluster").reset_index(drop=True)
        cluster_ids = zones_sorted["cluster"].tolist()
        areas = zones_sorted["area_ha"].tolist()
        cmap = plt.get_cmap("tab10")
        colors_bar = [cmap(i) for i in cluster_ids]

        ax_bar.bar(cluster_ids, areas, color=colors_bar, edgecolor="black")
        ax_bar.set_xticks(cluster_ids)
        ax_bar.set_xlabel("Zona (cluster)")
        ax_bar.set_ylabel("Área (ha)")
        ax_bar.set_title("Área por Zona")

    plt.tight_layout()
    plt.savefig(out_png, dpi=250, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    logger.info(f"Figura de vista general de zonificación guardada en {out_png}")
```

### Usage

- Llamado internamente por `AgriculturalZoning.visualize_results()`.
- También puede ser invocado directamente si el usuario quiere una vista general independiente (pasar GeoDataFrames personalizados).

## 6.5 `__init__.py`

```python
# src/pascal_zoning/__init__.py

"""
pascal_zoning — Una librería de zonificación agrícola potenciada por machine learning.

Proporciona:
  - Clase `AgriculturalZoning` para funcionalidad completa de pipeline.
  - Clases de datos: `ClusterMetrics`, `ZoneStats`, `ZoningResult`.
  - Funciones de utilidad y excepciones.
"""

from .zoning import AgriculturalZoning, ZonificationError, ValidationError, ProcessingError
from .zoning import ClusterMetrics, ZoneStats, ZoningResult
from .pipeline import app  # Punto de entrada CLI de Typer (si se desea importar directamente)
```

### Importaciones Bomb

Asegura que los usuarios puedan importar las clases principales y excepciones directamente:

```python
from pascal_zoning import AgriculturalZoning, ProcessingError
```

## 6.6 Resumen de Responsabilidades de Módulos

| Módulo | Responsabilidad |
|--------|----------------|
| `zoning.py` | Pipeline central: creación de máscaras, preprocesamiento de características, clustering, extracción de polígonos, filtrado, muestreo, estadísticas. |
| `pipeline.py` | Punto de entrada CLI (Typer): parsing de argumentos, carga de configuración, invocación de `run_pipeline()`, impresión de resúmenes. |
| `config.py` | Cargar y fusionar configuración desde `config.yaml` y variables de entorno (opcional). |
| `logging_config.py` | Configurar logger Loguru con formato compatible con ISO 42001, sinks de consola/archivo. |
| `interface.py` | Definir Protocolos y helpers de validación para verificación de tipos en tiempo de ejecución de entradas (índices espectrales, límites, parámetros). |
| `viz.py` | Helpers de visualización: generar mapas y gráficos de barras, usado por `visualize_results()`. |
| `__init__.py` | Exponer API público: clases, excepciones, app CLI; metadatos a nivel de paquete. |

Al entender estos módulos auxiliares, los desarrolladores pueden personalizar el logging, extender las opciones de configuración, hacer cumplir la validación de tipos estricta, o crear visualizaciones personalizadas—mientras siguen dependiendo de la implementación del pipeline central en `zoning.py`.

## 7. Excepciones y Manejo de Errores

La librería `pascal_zoning` define una jerarquía de excepciones personalizadas para señalar varios modos de falla. Todos los métodos orientados al usuario en la clase `AgriculturalZoning` y utilidades relacionadas lanzarán una de estas excepciones cuando ocurra un problema. Los consumidores de la API (o CLI) deben capturar estas excepciones para manejar errores graciosamente o realizar limpieza/logging según requerido por ISO 42001.

### 7.1 Jerarquía de Excepciones

```python
# src/pascal_zoning/zoning.py

class ZonificationError(Exception):
    """
    Base exception for all zoning-related errors.
    Indicates a general failure in the zoning pipeline.
    """
    pass


class ValidationError(ZonificationError):
    """
    Raised when input spectral indices or parameters are invalid.
    Use this to signal missing/incorrect index arrays, bad CRS, etc.
    """
    pass


class ProcessingError(ZonificationError):
    """
    Raised when any step of the zoning pipeline encounters a problem.
    Examples:
      - No valid pixels found inside the polygon.
      - KMeans cannot form the requested number of clusters.
      - Zero zones remain after size filtering.
      - No sampling points can be generated.
    """
    pass
```

### 7.2 Common Error Scenarios

**No Valid Pixels**

- **When**: During `create_mask()`, if there are zero pixels inside the polygon that also have valid, non‐NaN index values.
- **Exception**: `ProcessingError("No se encontraron píxeles válidos dentro del polígono.")`
- **Action**: Ensure that the input GeoTIFF overlaps the polygon and contains non‐NaN values.

**Invalid Indices Dictionary**

- **When**: If `indices` passed to `run_pipeline(...)` is empty or contains inconsistent array shapes.
- **Exception**: `ValidationError("No hay índices inicializados")` or custom validation logic.
- **Action**: Verify that `indices` is a non‐empty dict of NumPy 2D arrays of equal shape.

**Clustering Failures**

- **When**:
  - In `select_optimal_clusters()`, if silhouette calculation fails for every k, or
  - In `perform_clustering(force_k)`, if forced k is greater than n_valid_pixels.
- **Exception**: `ProcessingError("Number of labels is 1. Valid values are 2 to n_samples - 1 (inclusive)")` or similarly propagated from scikit‐learn.
- **Action**: Lower `force_k` or rely on automatic k selection. Ensure at least k distinct valid pixels exist.

**Zero Zones After Filtering**

- **When**: In `filter_small_zones()`, if every zone's computed area_ha is below `min_zone_size_ha`.
- **Exception**: `ProcessingError("No zones remain after filtering for minimum zone size.")` (thrown in subsequent logic).
- **Action**: Reduce `min_zone_size_ha` or provide larger input areas.

**Sampling Point Generation Fails**

- **When**: In `generate_sampling_points()`, if no valid pixels exist inside any zone or inhibition logic yields zero selected points.
- **Exception**: `ProcessingError("No se generaron puntos de muestreo en ninguna zona.")`
- **Action**: Decrease `points_per_zone`, adjust `min_zone_size_ha`, or ensure zones are large enough.

**File I/O Errors**

- **When**: In `save_results()`, if writing GeoPackage/CSV/JSON fails due to permission or path errors.
- **Potential Exceptions**: `IOError`, `OSError` (propagated).
- **Action**: Verify `output_dir` exists and is writable. Catch `OSError` externally if needed.

### 7.3 Manejo de Excepciones en CLI y API

#### 7.3.1 En el CLI (pipeline.py)

```python
# src/pascal_zoning/pipeline.py

from pascal_zoning.zoning import (
    AgriculturalZoning,
    ValidationError,
    ProcessingError
)
import typer

app = typer.Typer(help="Pascal Zoning ML CLI")

@app.command()
def run(
    raster: str = typer.Option(..., help="Ruta del GeoTIFF de entrada"),
    indices: str = typer.Option(..., help="Índices separados por comas (ej., NDVI,NDWI)"),
    output_dir: str = typer.Option(..., help="Directorio base de salida"),
    force_k: int | None = typer.Option(None, help="Forzar número de clusters"),
    min_zone_size: float = typer.Option(0.5, help="Área mínima de zona (ha)"),
    max_zones: int = typer.Option(10, help="Máximo clusters a evaluar"),
    points_per_zone: int = typer.Option(5, help="Puntos de muestreo por zona"),
    use_pca: bool = typer.Option(False, help="Habilitar PCA")
):
    try:
        # 1. Parsear y validar argumentos CLI
        indices_list = [idx.strip().upper() for idx in indices.split(",")]
        # 2. Leer GeoTIFF, computar índices espectrales vía bloque externo o omitir si están precomputados
        #    (no se muestra aquí; asumir índices precomputados cargados en `indices_dict`)
        # 3. Instanciar motor de zonificación
        zoning = AgriculturalZoning(
            random_state=42,
            min_zone_size_ha=min_zone_size,
            max_zones=max_zones,
            output_dir=Path(output_dir)
        )
        # 4. Llamar run_pipeline()
        result = zoning.run_pipeline(
            indices=indices_dict,
            bounds=field_polygon,
            points_per_zone=5,
            crs=crs_str,
            force_k=force_k,
            use_pca=use_pca
        )
        typer.secho("¡Zonificación completada exitosamente!", fg=typer.colors.GREEN)
        typer.Exit(code=0)

    except ValidationError as ve:
        typer.secho(f"Falló la validación de entrada: {ve}", fg=typer.colors.RED, err=True)
        typer.Exit(code=1)
    except ProcessingError as pe:
        typer.secho(f"Error de procesamiento: {pe}", fg=typer.colors.RED, err=True)
        typer.Exit(code=2)
    except Exception as ex:
        typer.secho(f"Error inesperado: {ex}", fg=typer.colors.RED, err=True)
        typer.Exit(code=3)
```

**Códigos de Salida:**
- 1: Validación falló
- 2: Procesamiento falló (error de pipeline en tiempo de ejecución)
- 3: Cualquier otro error inesperado

**Retroalimentación al Usuario:**
- El CLI imprime un mensaje legible para humanos, incluyendo el mensaje de excepción.
- Para auditoría (ISO 42001), el archivo de log subyacente (si se configura vía ZONING_LOG_FILE) contendrá stack traces completos y timestamps.

#### 7.3.2 En Uso de API de Python

```python
from pascal_zoning.zoning import (
    AgriculturalZoning,
    ValidationError,
    ProcessingError
)
import geopandas as gpd
import numpy as np

try:
    # Preparar entradas
    indices_dict = {
        "NDVI": np.load("ndvi.npy"),
        "NDRE": np.load("ndre.npy")
    }
    field_gdf = gpd.read_file("field_boundary.gpkg")
    bounds_polygon = field_gdf.geometry.iloc[0]

    # Instanciar y ejecutar
    zoning = AgriculturalZoning(random_state=123, min_zone_size_ha=0.1, max_zones=5)
    result = zoning.run_pipeline(
        indices=indices_dict,
        bounds=bounds_polygon,
        points_per_zone=10,
        crs="EPSG:32719",
        force_k=None,       # selección automática de k
        use_pca=True,
        output_dir=Path("outputs")
    )

    # Acceder a resultados si es exitoso
    zones_gdf = result.zones
    samples_gdf = result.samples

except ValidationError as ve:
    print(f"[ValidationError] {ve}")
    # Posiblemente logear los errores o notificar al usuario

except ProcessingError as pe:
    print(f"[ProcessingError] {pe}")
    # Manejar salidas parciales o limpieza

except Exception as ex:
    print(f"[UnexpectedError] {ex}")
    # Re-lanzar o logear para investigación adicional
```

**Recomendación:**
- Siempre envuelve las llamadas a `run_pipeline()` en un bloque try/except.
- Distingue entre ValidationError (lado cliente, arreglar entradas) y ProcessingError (lado servidor, ej., falla algorítmica).

### 7.4 Mensajes de Error Comunes y Remedios

| Excepción | Mensaje Típico | Causa Probable | Acción Sugerida |
|-----------|----------------|----------------|-----------------|
| ValidationError | "Index 'NDVI' must be a 2D numpy array" | Forma/dtype de array de entrada incorrecto | Asegurar que los arrays sean numpy.ndarray[float64] con 2 dims |
| ValidationError | "Bounds geometry is not a valid Polygon" | Geometría inválida o vacía pasada | Verificar que bounds viene de un polígono GeoDataFrame válido |
| ProcessingError | "n_samples < n_clusters" o "Number of labels is 1. Valid…" | Forzar k muy alto relativo al número de píxeles válidos | Reducir force_k o confiar en selección automática de k |
| ProcessingError | "No zones remain after filtering (min_zone_size_ha too large)." | Umbral min_zone_size_ha filtra todas las zonas pequeñas | Bajar min_zone_size_ha o usar un raster de entrada más grande |
| ProcessingError | "No sampling points generated in any zone." | points_per_zone > píxeles disponibles o lógica de inhibición falla | Bajar points_per_zone o inspeccionar mask/raster para asegurar datos suficientes |

### 7.5 Logging para Debugging

**Impresiones Loguru:**
- Logs detallados de nivel info se emiten en cada paso (ej., número de píxeles válidos, puntuaciones de silueta, tamaños de cluster).
- En caso de falla, logs de nivel error incluyen stack trace completo.

**Cumplimiento ISO 42001:**
- Cada evento de excepción se logea con un timestamp preciso.
- Los archivos de log pueden ser archivados para auditoría futura o análisis de causa raíz.

## 8. Data Classes & Return Types

The `pascal_zoning` library uses Python `@dataclass` constructs to encapsulate structured outputs. Consumers should inspect these classes to understand what attributes are available and how to retrieve results programmatically. All data classes are defined in `src/pascal_zoning/zoning.py`.

---

### 8.1 `ClusterMetrics`

```python
# src/pascal_zoning/zoning.py

@dataclass
class ClusterMetrics:
    """
    Metrics summarizing the quality and characteristics of the final clustering.
    - n_clusters: The number of clusters actually used (int).
    - silhouette: Silhouette score (float, in [-1.0, 1.0])—higher is better.
    - calinski_harabasz: Calinski‐Harabasz index (float)—higher is better.
    - inertia: Within‐cluster sum of squared distances (float)—lower is better.
    - cluster_sizes: Dict[int, int] mapping each cluster ID to its pixel count.
    - timestamp: ISO‐formatted timestamp of when clustering finished (str).
    """
    n_clusters: int
    silhouette: float
    calinski_harabasz: float
    inertia: float
    cluster_sizes: Dict[int, int]
    timestamp: str
```

**Usage Example**

```python
metrics: ClusterMetrics = result.metrics
print(metrics.n_clusters)            # e.g., 4
print(metrics.silhouette)            # e.g., 0.62
print(metrics.cluster_sizes[0])      # pixel count in cluster 0
print(metrics.timestamp)             # e.g., "2025-06-10 14:32:05"
```

### 8.2 ZoneStats

```python
# src/pascal_zoning/zoning.py

@dataclass
class ZoneStats:
    """
    Statistics computed for each management zone.
    - zone_id: Cluster ID (int, reindexed after filtering to be consecutive from 0).
    - area_ha: Zone area in hectares (float).
    - perimeter_m: Zone perimeter in meters (float).
    - compactness: Ratio 4π·area_m2/(perimeter_m²) (float in [0, 1]).
    - mean_values: Dict[str, float] of spectral index means (e.g., {'NDVI': 0.34}).
    - std_values: Dict[str, float] of spectral index standard deviations.
    """
    zone_id: int
    area_ha: float
    perimeter_m: float
    compactness: float
    mean_values: Dict[str, float]
    std_values: Dict[str, float]
```

**Key Attributes**

- **zone_id**: Matches the cluster column in zones GeoDataFrame.
- **area_ha**: Computed as (geometry.area) / 10000.0.
- **perimeter_m**: Computed as geometry.length.
- **compactness**: A shape index ∈ [0, 1].
- **mean_values**: Example keys: "NDVI", "NDRE".
- **std_values**: Corresponding per‐index standard deviation.

**Usage Example**

```python
stats_list: list[ZoneStats] = result.stats
for zs in stats_list:
    print(f"Zone {zs.zone_id}: {zs.area_ha:.4f} ha, compactness={zs.compactness:.3f}")
    print(f"  NDVI mean = {zs.mean_values['NDVI']:.4f}, std = {zs.std_values['NDVI']:.4f}")
```

### 8.3 ZoningResult

```python
# src/pascal_zoning/zoning.py

@dataclass
class ZoningResult:
    """
    Container for the complete output of the zoning pipeline.
    - zones: GeoDataFrame of dissolved zone polygons (one row per zone, with columns "cluster", "geometry", "area_ha", etc.).
    - samples: GeoDataFrame of sampling points (columns: "geometry", "cluster", plus one column per index name).
    - metrics: A `ClusterMetrics` instance summarizing clustering quality.
    - stats: List[ZoneStats] containing per‐zone statistics.
    """
    zones: gpd.GeoDataFrame
    samples: gpd.GeoDataFrame
    metrics: ClusterMetrics
    stats: List[ZoneStats]
```

**zones GeoDataFrame**

Each row corresponds to one management zone.

Columns:
- **"cluster"**: Zone ID (int).
- **"geometry"**: Shapely Polygon or MultiPolygon.
- **"area_m2"** (internal) and **"area_ha"** (exported).
- Possibly other index‐derived attributes if extended.

**samples GeoDataFrame**

One row per sampling point.

Columns:
- **"geometry"**: Shapely Point in world coordinates.
- **"cluster"**: Zone ID where the point lies.
- One column for each index name in indices (e.g., "NDVI", "NDRE") containing the pixel's index value.

**metrics**

Instance of ClusterMetrics (see section 8.1).

**stats**

List of ZoneStats instances (see section 8.2), in ascending order by zone_id.

**Usage Example**

```python
result: ZoningResult = zoning.run_pipeline(...)
# Inspect zones
print(result.zones.head())
# Inspect one point and its index values
sample0 = result.samples.iloc[0]
print(sample0.cluster, sample0.NDVI, sample0.NDRE)
# Metrics
print(result.metrics.n_clusters, result.metrics.silhouette)
# Stats
for zs in result.stats:
    print(zs.zone_id, zs.area_ha, zs.genre)  # "genre" is not a real attribute, just illustrative
```

### 8.4 Return Types for Public Methods

All public methods in the AgriculturalZoning class that return values adhere strictly to these data‐class schemas. Below is a summary:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `run_pipeline(...)` | `ZoningResult` | Executes full workflow, returns zones, samples, metrics, stats. |
| `create_mask()` | `None` | Populates self.valid_mask, no return. |
| `prepare_feature_matrix()` | `None` | Populates self.features_array, no return. |
| `select_optimal_clusters()` | `int` | Returns optimal k selected via Silhouette. |
| `perform_clustering(force_k=None)` | `None` | Populates self.cluster_labels and self.metrics, no return. |
| `extract_zone_polygons()` | `None` | Populates self.zones_gdf, no return. |
| `filter_small_zones()` | `None` | Updates self.zones_gdf by removing small polygons, no return. |
| `generate_sampling_points(n)` | `None` | Populates self.samples_gdf, no return. |
| `compute_zone_statistics()` | `None` | Populates self.zone_stats, no return. |
| `save_results(output_dir=None)` | `None` | Writes GeoPackage, CSV, JSON to disk, no return. |
| `visualize_results()` | `None` | Saves PNG figures to disk, no return. |

### 8.5 Example: Inspecting Return Values

```python
from pascal_zoning.zoning import AgriculturalZoning

# Prepare dummy 2×2 arrays
indices = {
    "NDVI": np.array([[0.1, 0.2],
                      [0.3, 0.4]]),
    "NDRE": np.array([[0.0, 0.1],
                      [0.2, 0.3]])
}

# Dummy bounds (simple square)
bounds = Polygon([(0,0), (2,0), (2,2), (0,2)])

# Run pipeline
zoning = AgriculturalZoning(random_state=0, min_zone_size_ha=0.00001, max_zones=2)
result = zoning.run_pipeline(
    indices=indices,
    bounds=bounds,
    points_per_zone=2,
    crs="EPSG:32719",
    force_k=2,
    use_pca=False,
    output_dir=None  # skip saving to disk
)

# `result` is a ZoningResult
print(type(result))                    # <class 'pascal_zoning.zoning.ZoningResult'>
print(result.metrics)                  # ClusterMetrics(...)
print(result.zones.columns)            # ["cluster","geometry","area_m2","area_ha",...]
print(result.samples.columns)          # ["geometry","cluster","NDVI","NDRE"]
print([zs.zone_id for zs in result.stats])  # [0,1]
```

### 8.6 Notes on Data Consistency

**Coordinate Reference Systems (CRS)**

Both zones and samples GeoDataFrames share the same CRS string provided to `run_pipeline(...)`.

When writing to disk, `to_file()` preserves the CRS so that GIS tools can correctly overlay layers.

**Index Value Types**

In `samples_gdf`, each index column is typed as float (converted from the original numpy float64).

If any input index array contained NaN, those corresponding points would have been filtered out by the mask.

**Cluster ID Reindexing**

After filtering out small zones, cluster IDs are reassigned to consecutive integers starting at 0.

Therefore, `zone_id` in ZoneStats and `cluster` in zones refer to the post‐filtering IDs, not the original KMeans labels.

**Time‐Stamped Outputs**

The timestamp field in ClusterMetrics is generated at the moment of clustering completion (`datetime.now().strftime(...)`).

Every run therefore produces unique metrics and output folder names (if `output_dir` is specified).

## 9. Exceptions & Error Handling

The `pascal_zoning` library defines a hierarchy of custom exceptions to signal different failure modes. All exceptions inherit from the base `ZonificationError`. Users of the API should catch specific exceptions where appropriate to recover or fail gracefully.

---

### 9.1 Exception Classes

```python
# src/pascal_zoning/zoning.py

class ZonificationError(Exception):
    """
    Base exception for all zoning-related errors.
    Indicates a general failure in the zoning pipeline.
    """
    pass


class ValidationError(ZonificationError):
    """
    Raised when input spectral indices or parameters are invalid.
    Use this to signal missing/incorrect index arrays, bad CRS, etc.
    """
    pass


class ProcessingError(ZonificationError):
    """
    Raised when any step of the zoning pipeline encounters a problem.
    Examples:
      - No valid pixels found inside the polygon.
      - KMeans cannot form the requested number of clusters.
      - Zero zones remain after size filtering.
      - No sampling points can be generated.
    """
    pass
```

### 9.2 Common Error Scenarios

**No Valid Pixels**

- **When**: During `create_mask()`, if there are zero pixels inside the polygon that also have valid, non‐NaN index values.
- **Exception**: `ProcessingError("No valid pixels found inside the polygon.")`
- **Action**: Ensure that the input GeoTIFF overlaps the polygon and contains non‐NaN values.

**Invalid Indices Dictionary**

- **When**: If `indices` passed to `run_pipeline(...)` is empty or contains inconsistent array shapes.
- **Exception**: `ValidationError("No indices initialized")` or custom validation logic.
- **Action**: Verify that `indices` is a non‐empty dict of NumPy 2D arrays of equal shape.

**Clustering Failures**

- **When**:
  - In `select_optimal_clusters()`, if silhouette calculation fails for every k, or
  - In `perform_clustering(force_k)`, if forced k is greater than n_valid_pixels.
- **Exception**: `ProcessingError("Number of labels is 1. Valid values are 2 to n_samples - 1 (inclusive)")` or similarly propagated from scikit‐learn.
- **Action**: Lower `force_k` or rely on automatic k selection. Ensure at least k distinct valid pixels exist.

**Zero Zones After Filtering**

- **When**: In `filter_small_zones()`, if every zone's computed area_ha is below `min_zone_size_ha`.
- **Exception**: `ProcessingError("No zones remain after filtering for minimum zone size.")` (thrown in subsequent logic).
- **Action**: Reduce `min_zone_size_ha` or provide larger input areas.

**Sampling Point Generation Fails**

- **When**: In `generate_sampling_points()`, if no valid pixels exist inside any zone or inhibition logic yields zero selected points.
- **Exception**: `ProcessingError("No sampling points generated in any zone.")`
- **Action**: Decrease `points_per_zone`, adjust `min_zone_size_ha`, or ensure zones are large enough.

**File I/O Errors**

- **When**: In `save_results()`, if writing GeoPackage/CSV/JSON fails due to permission or path errors.
- **Potential Exceptions**: `IOError`, `OSError` (propagated).
- **Action**: Verify `output_dir` exists and is writable. Catch `OSError` externally if needed.

### 9.3 Best Practices for Error Handling

**Catch Specific Exceptions**

```python
from pascal_zoning.zoning import (
    AgriculturalZoning,
    ValidationError,
    ProcessingError
)

try:
    zoning = AgriculturalZoning(...)
    result = zoning.run_pipeline(
        indices=indices,
        bounds=bounds_polygon,
        points_per_zone=5,
        crs="EPSG:32719"
    )
except ValidationError as ve:
    print(f"Input validation failed: {ve}")
    # Prompt user to correct inputs
except ProcessingError as pe:
    print(f"Processing error: {pe}")
    # Log details, adjust parameters, retry or abort
except Exception as e:
    print(f"Unexpected error: {e}")
    # Catch-all fallback
```

**Log Errors with Context**

The CLI and pipeline modules configure Loguru to include timestamps and module names. When catching exceptions inside a larger application, pass them to the logger:

```python
from loguru import logger

try:
    result = zoning.run_pipeline(...)
except ZonificationError as ze:
    logger.error(f"Zonification failed: {ze}")
    # Optionally re-raise or exit
```

**Validate Inputs Upfront**

Before invoking the pipeline:
- Ensure all index arrays have identical shapes.
- Check that `bounds` is a valid Shapely Polygon or MultiPolygon.
- Confirm `points_per_zone`, `min_zone_size_ha`, and `max_zones` are non‐negative and sensible.

**Use Return Codes in CLI**

The Typer-based CLI returns nonzero exit codes on uncaught exceptions. Catch `ValidationError` or `ProcessingError` in the CLI entrypoint to return a controlled exit code (e.g., `sys.exit(1)`).

### 9.4 Error Messages and Localization

All exceptions carry messages in Spanish by default (e.g., "No se encontraron píxeles válidos dentro del polígono.").

For an English‐only deployment, consider wrapping or translating exception messages at the top level:

```python
try:
    zoning.run_pipeline(...)
except ProcessingError as pe:
    raise RuntimeError(f"Pipeline failed: {str(pe)}")
```

Future releases may expose a language‐toggle or standardized error codes—currently, message strings are used for human‐readable diagnostics.

### 9.5 Integration with ISO 42001 Requirements

**Traceability:**

- All caught exceptions should be logged with Loguru, including full stack traces in debug mode.
- Maintain a record of the pipeline run in an audit log (e.g., `processing_log.txt`) that includes exception occurrences and timestamps.

**Quality Control:**

- Unit tests and integration tests assert that specific invalid inputs raise `ValidationError` or `ProcessingError` as expected.
- Example pytest snippet:

```python
import pytest
from pascal_zoning.zoning import ValidationError, ProcessingError, AgriculturalZoning

def test_invalid_indices_shape():
    with pytest.raises(ValidationError):
        zoning = AgriculturalZoning(...)
        zoning.run_pipeline(indices={"NDVI": np.ones((2,2)), "NDRE": np.ones((3,3))}, ...)
```

**Continuous Improvement:**

- Any newly encountered edge‐case errors should be added to the `techdebt.md` file or logged in the CHANGELOG with a note (ISSUE #xyz).

## 10. Logging & Configuration

The `pascal_zoning` library uses **Loguru** for logging and supports configuration via environment variables, a `config.yaml`, or programmatic overrides. This section explains how to configure logging verbosity, format, and pipeline parameters, in line with ISO 42001 traceability standards.

---

### 10.1 Loguru Setup (logging_config.py)

The `logging_config.py` module initializes a Loguru logger with a default format that includes timestamps, log levels, and module names. By default, messages at level `INFO` and above are displayed.

```python
# src/pascal_zoning/logging_config.py

from loguru import logger
import os
import sys

# Determine log level from environment or default to INFO
LOG_LEVEL = os.getenv("ZONING_LOG_LEVEL", "INFO").upper()

# Remove default handler and reconfigure
logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <7}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
```

**Environment Variable:**
- `ZONING_LOG_LEVEL` (e.g., DEBUG, INFO, WARNING, ERROR) controls verbosity.

**Format Explanation:**
- `<green>{time:YYYY-MM-DD HH:mm:ss}</green>`: Timestamp in green.
- `<level>{level: <7}</level>`: Log level padded to 7 characters.
- `<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>`: Originating module, function, and line number in cyan.
- `<level>{message}</level>`: The actual log message.

### 10.2 Pipeline Configuration (config.py)

Configuration can be provided via:
1. Environment Variables
2. `config.yaml` file
3. CLI flags or Python API parameters (highest precedence)

The `config.py` helper loads a YAML file (if present) and merges values with defaults and environment overrides.

```python
# src/pascal_zoning/config.py

import os
import yaml
from pathlib import Path
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "random_state": 42,
    "min_zone_size_ha": 0.5,
    "max_zones": 10,
    "points_per_zone": 5,
    "use_pca": False
}

def load_config(config_path: Path = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file and environment variables.
    Priority: CLI params > config.yaml > environment vars > defaults.
    """
    cfg: Dict[str, Any] = DEFAULTS.copy()

    # 1. Load from config.yaml if provided
    if config_path is not None and config_path.exists():
        with open(config_path, "r") as f:
            yaml_cfg = yaml.safe_load(f) or {}
        cfg.update(yaml_cfg.get("zoning", {}))

    # 2. Override from environment variables if set
    env_map = {
        "random_state": "ZONING_RANDOM_STATE",
        "min_zone_size_ha": "ZONING_MIN_ZONE_SIZE_HA",
        "max_zones": "ZONING_MAX_ZONES",
        "points_per_zone": "ZONING_POINTS_PER_ZONE",
        "use_pca": "ZONING_USE_PCA"
    }
    for key, env_var in env_map.items():
        val = os.getenv(env_var)
        if val is not None:
            # Cast types: booleans and numbers
            if isinstance(DEFAULTS[key], bool):
                cfg[key] = val.lower() in ("1", "true", "yes")
            elif isinstance(DEFAULTS[key], int):
                cfg[key] = int(val)
            elif isinstance(DEFAULTS[key], float):
                cfg[key] = float(val)
            else:
                cfg[key] = val

    return cfg
```

**DEFAULTS:**
- Default values for common pipeline parameters.

**Environment Overrides:**
- `ZONING_RANDOM_STATE` → `random_state` (int)
- `ZONING_MIN_ZONE_SIZE_HA` → `min_zone_size_ha` (float)
- `ZONING_MAX_ZONES` → `max_zones` (int)
- `ZONING_POINTS_PER_ZONE` → `points_per_zone` (int)
- `ZONING_USE_PCA` → `use_pca` (bool)

**Usage:**

```python
from pathlib import Path
from pascal_zoning.config import load_config

cfg = load_config(Path("config.yaml"))
zoning = AgriculturalZoning(
    random_state=cfg["random_state"],
    min_zone_size_ha=cfg["min_zone_size_ha"],
    max_zones=cfg["max_zones"]
)
```

### 10.3 CLI Integration (pipeline.py)

The CLI (`pipeline.py`) integrates `logging_config` and `config.py` so that CLI flags override `config.yaml` and environment variables. It uses Typer to define arguments and dispatch to the run command.

```python
# src/pascal_zoning/pipeline.py

import typer
from pathlib import Path
from loguru import logger
from pascal_zoning.zoning import AgriculturalZoning, ProcessingError
from pascal_zoning.config import load_config

app = typer.Typer(help="Pascal Zoning ML: Generate management zones and sampling points")

@app.command()
def run(
    raster: Path = typer.Option(..., "--raster", help="Path to clipped GeoTIFF of field"),
    indices: str = typer.Option(..., "--indices", help="Comma-separated list of indices"),
    output_dir: Path = typer.Option(..., "--output-dir", help="Directory to place outputs"),
    force_k: int = typer.Option(None, "--force-k", help="Force number of clusters (int)"),
    min_zone_size_ha: float = typer.Option(None, "--min-zone-size", help="Minimum zone area (ha)"),
    max_zones: int = typer.Option(None, "--max-zones", help="Maximum clusters to evaluate"),
    points_per_zone: int = typer.Option(None, "--points-per-zone", help="Sampling points per zone"),
    use_pca: bool = typer.Option(False, "--use-pca", help="Enable PCA before clustering"),
    config_file: Path = typer.Option(None, "--config", help="Path to config.yaml")
):
    """
    Run the full zoning pipeline: mask creation, clustering, sampling, stats, and export.
    """
    try:
        # 1. Load YAML & environment config
        cfg = load_config(config_file)

        # 2. Override with CLI flags if provided
        if force_k is not None:
            cfg["force_k"] = force_k
        if min_zone_size_ha is not None:
            cfg["min_zone_size_ha"] = min_zone_size_ha
        if max_zones is not None:
            cfg["max_zones"] = max_zones
        if points_per_zone is not None:
            cfg["points_per_zone"] = points_per_zone
        if use_pca:
            cfg["use_pca"] = True

        # 3. Parse indices argument into a dict of uppercase keys
        idx_names = [name.strip().upper() for name in indices.split(",")]

        # 4. Read raster and compute spectral indices using pascal_ndvi_block or custom code
        # (omitted for brevity; see Integration section)

        # 5. Initialize AgriculturalZoning with merged config
        zoning = AgriculturalZoning(
            random_state=cfg["random_state"],
            min_zone_size_ha=cfg["min_zone_size_ha"],
            max_zones=cfg["max_zones"],
            output_dir=output_dir
        )

        # 6. Run pipeline
        zoning.run_pipeline(
            indices=indices_dict,           # dict[str, np.ndarray]
            bounds=bounds_polygon,          # Shapely Polygon
            points_per_zone=cfg["points_per_zone"],
            crs=raster_crs,
            force_k=cfg.get("force_k", None),
            use_pca=cfg["use_pca"],
            output_dir=output_dir
        )

        logger.info("Pipeline completed successfully.")

    except ProcessingError as pe:
        logger.error(f"Processing error: {pe}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"Unexpected failure: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
```

**Priority Order:**
1. CLI flags
2. `config.yaml`
3. Environment variables
4. Defaults in `config.py`

**Error Handling:**
- Catches `ProcessingError` to print user-friendly messages and exit with code 1.
- Logs unexpected exceptions with full stack trace (diagnose mode).

### 10.4 ISO 42001 Compliance

**Traceability Requirements:**
- All pipeline steps are logged at INFO or DEBUG level, capturing timestamps and parameter values.
- Error occurrences are logged at ERROR or CRITICAL level with context.
- A `processing_log.txt` (or similar) can be generated by redirecting logs to a file in addition to stdout.

**Configuration Transparency:**
- `config.yaml` outlines every tunable parameter with default values.
- Environment variables are documented in README.md and relevant ISO 42001 artifacts.

**Reproducible Runs:**
- By freezing `random_state`, results can be reproduced.
- Log files include the exact parameter set used in each run.

**Audit Trail:**
- Each run's metadata (version, timestamp, parameters) can be stored alongside outputs (e.g., `metadata.json` within the timestamped folder).

Example `metadata.json` format:

```json
{
  "version": "0.1.0",
  "timestamp": "2025-06-05T12:34:56Z",
  "parameters": {
    "random_state": 42,
    "min_zone_size_ha": 0.5,
    "max_zones": 10,
    "points_per_zone": 5,
    "use_pca": false,
    "force_k": null
  },
  "input_raster": "inputs/field_clip.tif",
  "indices": ["NDVI", "NDWI", "NDRE", "SI"]
}
```

## 11. Testing & Continuous Integration

This section describes how to run and configure the automated test suite (unit, integration, and linting) in order to ensure ISO 42001–level quality control.

1. **Pytest**  
   - All unit tests live under `tests/unit/`  
   - All integration tests live under `tests/integration/`  
   - Run all tests with:
     ```bash
     pytest -v
     ```
   - Filter or re-run specific tests, for example:
     ```bash
     pytest tests/unit/test_zoning_core.py::test_run_pipeline_basic
     ```
   - Use `pytest.ini` to configure warnings filtering and test discovery.

2. **MyPy (Static Typing Checks)**  
   - Verify type-safety (ignoring some temporary “technical debt” codes) with:
     ```bash
     mypy src/
     ```
   - Configuration lives in `mypy.ini`. Amend `disable_error_code` entries only for temporary exceptions. Document in `TECHDEBT.md`.

3. **Linting / Formatting**  
   - **Flake8** for style and error checks:
     ```bash
     flake8 src/
     ```
   - **Black** for consistent code formatting:
     ```bash
     black --check src/
     ```
   - These tools can be enforced in CI pipelines to prevent regressions.

4. **Continuous Integration (CI)**  
   - A typical GitHub Actions workflow YAML would include jobs to:
     1. Set up Python 3.11 environment  
     2. Install dependencies (`pip install -r requirements-dev.txt`)  
     3. Run `pytest` (with coverage reporting)  
     4. Run `mypy`  
     5. Run `flake8` and `black --check`  
   - On pull requests, CI must pass all checks before merging to `main`.

5. **Coverage**  
   - We use `pytest-cov` to measure test coverage:
     ```bash
     pytest --cov=pascal_zoning --cov-report=xml
     ```
   - The CI can fail if coverage falls below a predefined threshold (e.g., 90%).

---

## 12. Appendix (Optional)

Additional reference material, such as:

- **12.1. Glossary**: Definitions of domain-specific terms (e.g., “compactness”, “spectral index”).  
- **12.2. References**: Links to ISO 42001 documentation, relevant academic papers, or external standards.  
- **12.3. Change History Guidelines**: Template for writing semantic version entries in `CHANGELOG.md`.  

```markdown
### 12.1 Glossary

- **Spectral Index**: A normalized ratio of two spectral bands (e.g., NDVI = (NIR – Red)/(NIR + Red)).  
- **Compactness**: \(4\pi \cdot \text{area} \,/\, (\text{perimeter}^2)\). A measure of how “circular” a polygon is.  
- **Zone (Cluster)**: A contiguous area of similar spectral statistics.

### 12.2 References

- ISO 42001 – Artificial Intelligence Management System.  
  https://www.iso.org/standard/77566.html  
- Khronos Group. GDAL/OGR documentation: https://gdal.org/

### 12.3 CHANGELOG.md Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1] – 2025-06-01
### Added
- Initial release of Pascal Zoning ML
- CLI and Python API respecting ISO 42001 traceability

## [1.0.2] – 2025-07-15
### Changed
- Improved sampling algorithm to allow `points_per_zone > sqrt(#pixels)`
- Updated documentation to include `Testing & CI` section

## [1.1.0] – 2025-08-10
### Added
- Support for custom config.yaml parameters
- Added `api_documentation.md` outline
- Included new `visualization_overview` function in `viz.py`

### Fixed
- Corrected `filter_small_zones` to reassign cluster IDs correctly
```