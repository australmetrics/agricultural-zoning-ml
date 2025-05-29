# PASCAL NDVI Block

© 2025 AustralMetrics SpA. All rights reserved.

A high-performance module for calculating NDVI, NDRE, and SAVI indices from Sentinel-2/Landsat imagery, focusing on simplicity and ISO 42001 compliance.

## Project Status
![Tests & Lint](https://github.com/australmetrics/pascal-ndvi-block/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/australmetrics/pascal-ndvi-block/branch/main/graph/badge.svg)](https://codecov.io/gh/australmetrics/pascal-ndvi-block)
[![ISO 42001](https://img.shields.io/badge/ISO-42001-blue.svg)](docs/compliance/iso42001_compliance.md)

- **Version**: 1.0.0
- **Compatibility**: Windows, Linux, macOS
- **Python**: 3.7+

## Features

- **Simplified Input**: Process satellite imagery without complex configuration files
- **Automatic Detection**: Smart identification of spectral bands based on image type
- **Multiple Indices**: Calculate NDVI, NDRE, and SAVI in a single pass
- **Intuitive CLI**: Simple commands for all operations
- **Automated Pipeline**: Complete processing with a single command

## Normative Dependencies

This project follows ISO 42001 compliance requirements and integrates with other PASCAL ecosystem blocks. For detailed information about normative dependencies and compliance:

- [Normative Dependencies Documentation](docs/compliance/normative_dependencies.md)
- [ISO 42001 Compliance](docs/compliance/iso42001_compliance.md)
- [Security Policy](SECURITY.md)

## Quality Control & CI/CD

This project implements robust Continuous Integration (CI) and Continuous Delivery (CD) practices:

- **Automated Testing**: Every push and pull request triggers:
  - Unit tests with pytest
  - Style verification with flake8
  - Type checking with mypy
- **Quality Control**: 
  - 100-character line limit
  - Consistent formatting
  - Mandatory documentation

## Traceability & Audit

ISO 42001-compliant logging system:

- **Location**: `results/logs/`
  - Main logs: `pascal_ndvi_YYYYMMDD_HHMMSS.log`
  - Automatic backups: `backup/pascal_ndvi_*_backup.log`
  - Integrity verification: SHA-256 hashes in `*.sha256`
- **Logged Information**:
  - Precise timestamps
  - User and process data
  - Input parameters
  - Results and errors

## Installation

```bash
# Clone repository
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### Simple Index Calculation

```bash
# Calculate all indices for an image
python -m src.main indices --image=data/my_image.tif

# Specify output directory
python -m src.main indices --image=data/my_image.tif --output=results
```

### Process with Clipping (optional)

```bash
# Clip image using shapefile
python -m src.main clip --image=data/my_image.tif --shapefile=data/area.shp

# Complete processing: clip + indices
python -m src.main auto --image=data/my_image.tif --shapefile=data/area.shp
```

### Automated Processing

```bash
# Simplest option: image only, no clipping
python -m src.main auto --image=data/my_image.tif
```

## Project Structure

```
pascal-ndvi-block/
├── data/                  # Input imagery folder
├── results/              # Generated results (default)
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point and CLI
│   ├── preprocessor.py    # Preprocessing functions (clipping)
│   └── indices.py         # Vegetation indices calculation
├── tests/
│   └── test_main.py       # Unit tests
├── README.md
└── requirements.txt
```

## Configuration

1. Copy the environment variables example file:
```powershell
Copy-Item .env.example .env
```

2. Edit the `.env` file with your settings:
   - `USERNAME`: Your username for audit logs
   - `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

The `.env` file will not be uploaded to Git for security.

## ISO 42001 Compliance

This module is designed following ISO 42001 principles for artificial intelligence management systems:

- **Simplicity**: Minimal interfaces and clear workflows
- **Documentation**: Fully documented code and APIs
- **Maintainability**: Modular structure and automated testing
- **Reproducibility**: Consistent results with the same input data
- **Traceability**: Detailed processing logs using loguru

## Requirements

- Python 3.7+
- rasterio
- geopandas
- numpy
- typer
- loguru

## Support and Contact

- **Internal Repository**: Create GitHub issue to report problems
- **Documentation**: See documentation in the `docs/` folder
- **Contact**: Contact AustralMetrics SpA development team

## License and Usage

This software is property of AustralMetrics SpA. Its use, modification, and distribution is restricted to authorized company personnel.

