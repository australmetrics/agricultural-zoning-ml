# Functions Reference - PASCAL NDVI Block

© 2025 AustralMetrics SpA. All rights reserved.

## Table of Contents

1. [Core Zoning Functions](#core-zoning-functions)
   - AgriculturalZoning Class
   - Pipeline Operations
   - Clustering Methods

2. [Vegetation Indices](#vegetation-indices)
   - NDVI Calculation
   - SAVI Implementation
   - Index Validation

3. [Data Processing](#data-processing)
   - Image Loading & Preprocessing
   - Feature Extraction
   - Data Validation

4. [Visualization](#visualization)
   - Map Generation
   - Statistical Plots
   - Export Formats

5. [Configuration & Setup](#configuration--setup)
   - Environment Setup
   - Parameter Configuration
   - Logger Configuration

6. [Utility Functions](#utility-functions)
   - File Operations
   - Type Validation
   - Helper Functions

## Core Zoning Functions

### Class: `AgriculturalZoning`

Main engine class for agricultural field zoning operations.

#### Constructor
```python
def __init__(
    self,
    input_file: Path,
    output_dir: Path,
    k_clusters: int = 3,
    min_zone_size: float = 0.5,
    **kwargs
) -> None
```

**Parameters:**
- `input_file`: Path to input raster image
- `output_dir`: Directory for results
- `k_clusters`: Number of zones (default: 3)
- `min_zone_size`: Minimum zone size in hectares (default: 0.5)
- `**kwargs`: Additional configuration options

#### Key Methods

##### `run_pipeline`
```python
def run_pipeline(
    self,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
```
Executes the complete zoning workflow.

**Parameters:**
- `progress_callback`: Optional callback for progress updates
**Returns:**
- Dictionary with processing results and metrics

##### `prepare_feature_matrix`
```python
def prepare_feature_matrix(self) -> np.ndarray:
```
Creates the feature matrix for clustering.

**Returns:**
- NumPy array with prepared features

##### `perform_clustering`
```python
def perform_clustering(
    self, 
    feature_matrix: np.ndarray
) -> Tuple[np.ndarray, Dict[str, float]]:
```
Performs K-means clustering on the feature matrix.

**Parameters:**
- `feature_matrix`: Prepared feature matrix
**Returns:**
- Tuple of (cluster labels, quality metrics)

### Vegetation Indices

#### `calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray`
Calculates the Normalized Difference Vegetation Index (NDVI).

**Parameters:**
- `red_band`: NumPy array with red band reflectance values
- `nir_band`: NumPy array with near-infrared band reflectance values

**Returns:**
- NumPy array with NDVI values in range [-1, 1]

**Validations:**
- Bands must have same dimensions
- Values cannot be all zero
- Division by zero handling

### `calculate_savi(red_band: np.ndarray, nir_band: np.ndarray, l: float = 0.5) -> np.ndarray`
Calculates the Soil Adjusted Vegetation Index (SAVI).

**Parameters:**
- `red_band`: NumPy array with red band reflectance values
- `nir_band`: NumPy array with near-infrared band reflectance values
- `l`: Soil adjustment factor (0.0 - 1.0)

**Returns:**
- NumPy array with SAVI values

**Validations:**
- L factor must be between 0 and 1
- Bands must have same dimensions
- Division by zero handling

## Preprocessing

### `clip_raster(image_path: Path, shapefile_path: Path) -> np.ndarray`
Clips a raster image using a shapefile.

**Parameters:**
- `image_path`: Path to raster file
- `shapefile_path`: Path to clipping shapefile

**Returns:**
- NumPy array with clipped image

**Validations:**
- Files must exist
- Compatible coordinate systems
- Valid clipping area

## Logging and Traceability

### `setup_logging(output_dir: Path) -> None`
Configures the logging system according to ISO 42001.

**Parameters:**
- `output_dir`: Directory for log files

**Features:**
- Precise timestamps
- Automatic backup
- SHA-256 integrity verification
- Log rotation

## Visualization Functions

### `create_zone_map`
```python
def create_zone_map(
    zones_gdf: gpd.GeoDataFrame,
    output_path: Path,
    *,
    title: str = "Agricultural Zones",
    cmap: str = "viridis"
) -> None:
```
Creates a visualization of agricultural zones.

**Parameters:**
- `zones_gdf`: GeoDataFrame with zones
- `output_path`: Save path for map
- `title`: Map title (optional)
- `cmap`: Colormap name (optional)

### `plot_zone_statistics`
```python
def plot_zone_statistics(
    stats_df: pd.DataFrame,
    output_path: Path,
    metrics: List[str]
) -> None:
```
Generates statistical plots for zones.

**Parameters:**
- `stats_df`: DataFrame with zone statistics
- `output_path`: Save path for plots
- `metrics`: Metrics to visualize

### `export_results`
```python
def export_results(
    results: Dict[str, Any],
    output_dir: Path,
    export_format: str = "all"
) -> None:
```
Exports results in various formats.

**Parameters:**
- `results`: Dictionary with results
- `output_dir`: Output directory
- `export_format`: Format to export ("gpkg", "json", "png", "all")

## Configuration

### `get_config() -> Dict[str, Any]`
Returns the current system configuration.

**Returns:**
- Dictionary with configuration values

**Configurable Parameters:**
- Working directories
- Supported indices
- Security limits
- Satellite configuration
- Visualization settings

## ISO 42001 Compliance

All functions in this reference implement:

1. **Input Validation**
   - Type checking
   - Value range verification
   - File existence verification

2. **Error Handling**
   - Descriptive error messages
   - Proper exception hierarchy
   - Error logging

3. **Logging & Traceability**
   - Function entry/exit logging
   - Parameter validation
   - Performance metrics
   - Error conditions

4. **Documentation**
   - Complete docstrings
   - Parameter descriptions
   - Return value specifications
   - Usage examples

5. **Security**
   - Path traversal prevention
   - Resource limits
   - Access control

## Implementation Notes

- All functions are thread-safe
- Memory management for large datasets
- Progress reporting for long operations
- Cancellation support where applicable
- Proper cleanup of resources

## Usage Examples

### Basic Usage
```python
from pathlib import Path
from pascal_zoning import AgriculturalZoning

# Initialize zoning engine
zoning = AgriculturalZoning(
    input_file=Path("field.tif"),
    output_dir=Path("results"),
    k_clusters=3
)

# Run complete pipeline
results = zoning.run_pipeline()
```

### Advanced Usage
```python
from pascal_zoning import AgriculturalZoning
from pascal_zoning.config import load_config
from pascal_zoning.logging_config import setup_logging

# Setup environment
config = load_config("config.yaml")
setup_logging(Path("logs"))

# Initialize with custom parameters
zoning = AgriculturalZoning(
    input_file=Path("field.tif"),
    output_dir=Path("results"),
    k_clusters=4,
    min_zone_size=0.75,
    **config
)

# Run pipeline with progress callback
def progress_callback(step: str, percent: float):
    print(f"{step}: {percent:.1f}%")

results = zoning.run_pipeline(progress_callback=progress_callback)
```