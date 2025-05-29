# Functions Reference - PASCAL NDVI Block

## Index
1. [Main Functions](#main-functions)
2. [Preprocessing](#preprocessing)
3. [Logging & Traceability](#logging-traceability)
4. [Configuration](#configuration)

## Main Functions

### `calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray`
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

## Error Handling

All functions implement:
- Input validation
- Descriptive error messages
- Error logging
- Traceability according to ISO 42001

## Usage Examples

```python
from pathlib import Path
from src.indices import calculate_ndvi
from src.preprocessor import clip_raster
from src.logging_config import setup_logging

# Configurar logging
setup_logging(Path("results"))

# Procesar imagen
red = clip_raster("imagen.tif", "area.shp")
nir = clip_raster("imagen_nir.tif", "area.shp")
ndvi = calculate_ndvi(red, nir)
```

## Implementation Notes

- All functions are thread-safe
- Optimized for large datasets
- Implement efficient memory management
- Comply with static typing