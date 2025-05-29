# API Documentation

© 2025 AustralMetrics SpA. All rights reserved.

## Overview

The PASCAL NDVI Block provides a simple and robust API for calculating vegetation indices from satellite imagery. This documentation covers all available functions, parameters, and expected outputs in compliance with ISO 42001 standards.

## Core Modules

### 1. Main Module (`src.main`)

The entry point for all operations, providing CLI interface and orchestration.

#### Functions

##### `calculate_indices(image_path: str, output_dir: str = "results") -> Dict[str, Any]`

**Purpose**: Calculate NDVI, NDRE, and SAVI indices for a given image.

**Parameters**:
- `image_path` (str): Path to input satellite image (Sentinel-2 or Landsat)
- `output_dir` (str, optional): Output directory path. Default: "results"

**Returns**:
- Dictionary containing:
  - `status`: "success" or "error"
  - `output_files`: List of generated output files
  - `processing_time`: Time taken in seconds
  - `log_file`: Path to processing log

**Example**:
```python
from src.main import calculate_indices

result = calculate_indices(
    image_path="data/sentinel2_image.tif",
    output_dir="results/analysis1"
)
```

##### `clip_image(image_path: str, shapefile_path: str, output_dir: str = "results") -> Dict[str, Any]`

**Purpose**: Clip satellite image using vector boundaries.

**Parameters**:
- `image_path` (str): Path to input satellite image
- `shapefile_path` (str): Path to clipping shapefile
- `output_dir` (str, optional): Output directory path. Default: "results"

**Returns**:
- Dictionary containing clipping results and metadata

**Example**:
```python
from src.main import clip_image

result = clip_image(
    image_path="data/landsat_image.tif",
    shapefile_path="data/study_area.shp",
    output_dir="results/clipped"
)
```

##### `auto_process(image_path: str, shapefile_path: str = None, output_dir: str = "results") -> Dict[str, Any]`

**Purpose**: Automated processing pipeline combining clipping and index calculation.

**Parameters**:
- `image_path` (str): Path to input satellite image
- `shapefile_path` (str, optional): Path to clipping shapefile
- `output_dir` (str, optional): Output directory path. Default: "results"

**Returns**:
- Comprehensive processing results dictionary

### 2. Indices Module (`src.indices`)

Handles vegetation index calculations with automatic band detection.

#### Functions

##### `detect_bands(image_metadata: Dict) -> Dict[str, int]`

**Purpose**: Automatically detect spectral band positions based on image type.

**Parameters**:
- `image_metadata` (Dict): Image metadata from rasterio

**Returns**:
- Dictionary mapping band names to indices:
  - `red`: Red band index
  - `nir`: Near-infrared band index
  - `red_edge`: Red-edge band index (if available)

**Supported Imagery**:
- Sentinel-2 (Level 1C and 2A)
- Landsat 8/9 (OLI/TIRS)
- Generic multispectral imagery

##### `calculate_ndvi(red_band: numpy.ndarray, nir_band: numpy.ndarray) -> numpy.ndarray`

**Purpose**: Calculate Normalized Difference Vegetation Index.

**Formula**: `NDVI = (NIR - Red) / (NIR + Red)`

**Parameters**:
- `red_band` (numpy.ndarray): Red band pixel values
- `nir_band` (numpy.ndarray): Near-infrared band pixel values

**Returns**:
- NDVI array with values ranging from -1 to 1

##### `calculate_ndre(red_edge_band: numpy.ndarray, nir_band: numpy.ndarray) -> numpy.ndarray`

**Purpose**: Calculate Normalized Difference Red Edge Index.

**Formula**: `NDRE = (NIR - RedEdge) / (NIR + RedEdge)`

**Parameters**:
- `red_edge_band` (numpy.ndarray): Red-edge band pixel values
- `nir_band` (numpy.ndarray): Near-infrared band pixel values

**Returns**:
- NDRE array with values ranging from -1 to 1

##### `calculate_savi(red_band: numpy.ndarray, nir_band: numpy.ndarray, l_factor: float = 0.5) -> numpy.ndarray`

**Purpose**: Calculate Soil Adjusted Vegetation Index.

**Formula**: `SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)`

**Parameters**:
- `red_band` (numpy.ndarray): Red band pixel values
- `nir_band` (numpy.ndarray): Near-infrared band pixel values
- `l_factor` (float, optional): Soil brightness correction factor. Default: 0.5

**Returns**:
- SAVI array with values ranging from -1 to 1

### 3. Preprocessor Module (`src.preprocessor`)

Handles image preprocessing operations including clipping and validation.

#### Functions

##### `validate_image(image_path: str) -> Dict[str, Any]`

**Purpose**: Validate input image format and metadata.

**Parameters**:
- `image_path` (str): Path to input image

**Returns**:
- Validation results dictionary containing:
  - `valid`: Boolean validation status
  - `format`: Detected image format
  - `bands`: Number of bands
  - `crs`: Coordinate reference system
  - `errors`: List of validation errors (if any)

##### `clip_with_shapefile(image_path: str, shapefile_path: str, output_path: str) -> str`

**Purpose**: Clip raster image using vector geometry.

**Parameters**:
- `image_path` (str): Path to input raster
- `shapefile_path` (str): Path to clipping vector
- `output_path` (str): Path for output clipped raster

**Returns**:
- Path to clipped output file

## Error Handling

All API functions implement comprehensive error handling following ISO 42001 guidelines:

### Common Error Types

1. **FileNotFoundError**: Input files not accessible
2. **ValueError**: Invalid parameter values or incompatible data
3. **ProcessingError**: Internal processing failures
4. **ValidationError**: Input data validation failures

### Error Response Format

```python
{
    "status": "error",
    "error_type": "ValidationError",
    "message": "Input image does not contain required spectral bands",
    "details": {
        "required_bands": ["red", "nir"],
        "available_bands": ["blue", "green", "red"]
    },
    "timestamp": "2025-01-15T10:30:45Z",
    "log_file": "results/logs/pascal_ndvi_20250115_103045.log"
}
```

## Data Types and Formats

### Supported Input Formats

- **Raster**: GeoTIFF (.tif, .tiff), JP2 (.jp2), HDF (.hdf)
- **Vector**: Shapefile (.shp), GeoJSON (.geojson), KML (.kml)

### Output Formats

- **Indices**: GeoTIFF with float32 precision
- **Metadata**: JSON sidecar files
- **Logs**: Structured text logs with timestamps

## Performance Specifications

### Processing Times (Typical Hardware)

| Image Size | Operation | Time Range |
|------------|-----------|------------|
| 10980x10980 (Sentinel-2) | Index Calculation | 15-30 seconds |
| 7000x7000 (Landsat) | Index Calculation | 8-15 seconds |
| Any Size | Clipping | 5-20 seconds |

### Memory Requirements

- **Minimum**: 4GB RAM
- **Recommended**: 8GB RAM for large scenes
- **Storage**: ~2x input file size for temporary processing

## Logging and Audit Trail

All API operations generate detailed logs for ISO 42001 compliance:

### Log Entry Format

```
2025-01-15T10:30:45.123Z | INFO | USER:john.doe | FUNCTION:calculate_indices | 
INPUT:{"image_path": "data/scene.tif", "output_dir": "results"} | 
OUTPUT:{"status": "success", "files": 3} | DURATION:23.45s
```

### Log Levels

- **DEBUG**: Detailed internal processing steps
- **INFO**: Standard operation logging
- **WARNING**: Non-critical issues or fallbacks
- **ERROR**: Processing failures with details
- **CRITICAL**: System-level failures

## Version Compatibility

### API Stability Promise

- **Major Version** (X.0.0): Breaking changes, migration required
- **Minor Version** (1.X.0): New features, backward compatible
- **Patch Version** (1.0.X): Bug fixes, fully compatible

### Deprecation Policy

- **Notice Period**: 6 months minimum for deprecated features
- **Documentation**: Clear migration paths provided
- **Support**: Parallel support during transition period

## Usage Examples

### Basic Workflow

```python
import os
from src.main import auto_process

# Set up processing
image_path = "data/sentinel2_20250115.tif"
study_area = "data/farm_boundary.shp"
output_dir = "results/farm_analysis"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Process automatically
result = auto_process(
    image_path=image_path,
    shapefile_path=study_area,
    output_dir=output_dir
)

# Check results
if result["status"] == "success":
    print(f"Processing completed. Files: {result['output_files']}")
    print(f"Log file: {result['log_file']}")
else:
    print(f"Error: {result['message']}")
```

### Batch Processing

```python
import glob
from src.main import calculate_indices

# Process multiple images
image_pattern = "data/sentinel2_*.tif"
images = glob.glob(image_pattern)

results = []
for image in images:
    result = calculate_indices(
        image_path=image,
        output_dir=f"results/{os.path.basename(image)[:-4]}"
    )
    results.append(result)

# Summary
successful = sum(1 for r in results if r["status"] == "success")
print(f"Processed {successful}/{len(results)} images successfully")
```

## Support and Updates

### Documentation Updates

This API documentation follows the software release cycle and is updated with each version. For the latest information:

- Check version compatibility section
- Review changelog for API changes
- Consult migration guides for major updates

### Contact Information

For technical support regarding API usage:
- **Internal Issues**: GitHub repository issue tracker
- **Technical Questions**: AustralMetrics SpA development team
- **Documentation Feedback**: Include in project issues with 'documentation' label