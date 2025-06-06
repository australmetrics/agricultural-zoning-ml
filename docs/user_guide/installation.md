# Installation Guide

© 2025 AustralMetrics SpA. All rights reserved.

This guide provides detailed installation instructions for the PASCAL NDVI Block module across different operating systems.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB available space
- **CPU**: Dual-core processor (quad-core recommended for large imagery)

### Python Dependencies
The module requires the following core libraries:
- `rasterio` >= 1.2.0 (geospatial raster I/O)
- `geopandas` >= 0.9.0 (vector data processing)
- `numpy` >= 1.19.0 (numerical computations)
- `typer` >= 0.4.0 (CLI interface)
- `loguru` >= 0.5.0 (ISO 42001 compliant logging)

## Installation Methods

# Installation

This section explains how to install PASCAL Agri-Zoning (`pascal_zoning`), including all required dependencies.

## 1. Prerequisites

Before installing, ensure you have:
- **Python 3.8+**  
- A working **geospatial environment** capable of building and running:
  - [rasterio](https://pypi.org/project/rasterio/)  
  - [geopandas](https://pypi.org/project/geopandas/)  
  - [shapely](https://pypi.org/project/Shapely/)  
- **GDAL** installed on your system (required by `rasterio` and `geopandas`). Confirm that `gdalinfo --version` prints a valid version.

Example (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev
```

Example (macOS with Homebrew):
```bash
brew install gdal
```

## 2. Create or Activate a Virtual Environment (Highly Recommended)

```bash
python3 -m venv pascal-env
source pascal-env/bin/activate
```

## 3. Install via pip (PyPI)

If PASCAL Agri-Zoning is available on PyPI:
```bash
pip install pascal-zoning
```

This will pull in the latest release from PyPI, including all required dependencies.

**Tip:** If you encounter any errors related to `rasterio` or `geopandas`, double-check that GDAL is installed and that your environment's PATH or LD_LIBRARY_PATH includes the GDAL libraries.

### 3.1. Verifying Installation

After installation, verify that you can import the library in Python:
```python
>>> import pascal_zoning
>>> pascal_zoning.__version__
'1.0.0'   # or the version you installed
```

If the import succeeds without errors, you're good to proceed.

## 4. Install from Source (GitHub)

If you prefer to install the latest development version or contribute to the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/pascal-zoning.git
   cd pascal-zoning
   ```

2. Build and install:
   ```bash
   pip install .
   ```
   
   or, to install in "editable" (development) mode:
   ```bash
   pip install --editable .
   ```

3. Verify import as above:
   ```bash
   python -c "import pascal_zoning; print(pascal_zoning.__version__)"
   ```

## 5. Optional: Install Visualization Dependencies

To generate advanced plots (e.g., using matplotlib), confirm you have:
```bash
pip install matplotlib
```

The viz module uses matplotlib, geopandas, and shapely. If you plan to run the zoning_overview routine, ensure these are installed.