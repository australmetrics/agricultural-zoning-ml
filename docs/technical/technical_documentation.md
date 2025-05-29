# PASCAL NDVI Block Technical Documentation

## Implemented Vegetation Indices

### NDVI (Normalized Difference Vegetation Index)
```python
def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    NDVI = (NIR - RED) / (NIR + RED)
    Range: -1.0 to 1.0
    """
```
- **Input**: Red and NIR bands as NumPy arrays
- **Output**: Array with NDVI values
- **Validation**: Verifies dimensions and data types

### SAVI (Soil Adjusted Vegetation Index)
```python
def calculate_savi(red_band: np.ndarray, nir_band: np.ndarray, L: float = 0.5) -> np.ndarray:
    """
    SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)
    L = soil adjustment factor (0 to 1)
    """
```
- **Input**: Red band, NIR band, and L factor
- **Output**: Array with SAVI values
- **Validation**: Verifies L range (0-1)

## Preprocessing

### Image Clipping
```python
def clip_raster(image_path: Path, shapefile_path: Path) -> Path:
    """
    Clips raster image using a shapefile
    """
```
- **Input**: Paths to image and shapefile
- **Output**: Path to clipped image
- **Validation**: Verifies CRS and extent

## Logging System

### Configuration
```python
def setup_logging(output_dir: Path) -> None:
    """
    Configures ISO 42001 compliant logging system
    """
```
- Format: Timestamp, process, user
- Backup: Automatic with SHA-256 hash
- Retention: 90 days by default

## Memory Management

### Block Processing
- Maximum image size: 10GB
- Processing in 1024x1024 chunks
- Monitored memory usage

## Limits and Validations

### Input Validations
- Supported formats: GeoTIFF
- Satellites: Sentinel-2, Landsat 8
- Cloud coverage: <50%

### Output Validations
- NDVI value range: [-1, 1]
- SAVI value range: [-1, 1]
- Preserved metadata

## APIs and Functions

### Main Function
```python
def process_image(
    image_path: Path,
    output_dir: Path,
    indices: List[str],
    savi_l: float = 0.5
) -> Dict[str, Path]:
```

### Configurable Parameters
```python
MAX_IMAGE_SIZE_GB = 10.0
DEFAULT_SAVI_L = 0.5
LOG_RETENTION_DAYS = 90
```

## Error Handling

### Controlled Errors
- ImageTooLargeError
- InvalidBandError
- ProcessingError
- ValidationError

### Error Logging
- Complete stacktrace
- Error context
- System state
