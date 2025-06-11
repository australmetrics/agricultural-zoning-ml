# Pascal Zoning

[![PyPI version](https://img.shields.io/pypi/v/pascal-zoning)](https://pypi.org/project/pascal-zoning/) 
[![License](https://img.shields.io/github/license/australmetrics/agricultural-zoning-ml)](https://github.com/australmetrics/agricultural-zoning-ml/blob/main/LICENSE) 
[![Build Status](https://img.shields.io/github/actions/workflow/status/australmetrics/agricultural-zoning-ml/validate-manifest.yml)](https://github.com/australmetrics/agricultural-zoning-ml/actions/workflows/validate-manifest.yml)
[![Codecov](https://img.shields.io/codecov/c/github/australmetrics/agricultural-zoning-ml?logo=codecov)](https://codecov.io/gh/australmetrics/agricultural-zoning-ml)
[![ISO 42001 Quality Check](https://img.shields.io/badge/ISO-42001-compliant-brightgreen)](https://australmetrics.cl/compliance/iso42001)


## Overview

Pascal Zoning is an AI‑driven agricultural zoning library, fully compliant with ISO 42001. It automates field mask creation, spectral-index preprocessing, clustering for management zones, and optimal sampling point generation, delivering traceable vector and tabular outputs for precision agriculture.

## Features

* **Modular CLI & Python API**: flexible integration into pipelines.
* **Automated Preprocessing**: mask creation, imputation, scaling, optional PCA.
* **Smart Clustering**: automatic *k* selection (Silhouette & Calinski‑Harabasz).
* **Optimal Sampling**: spatial‑inhibition algorithm for evenly spaced points.
* **Rich Exports**: GeoPackage, CSV, JSON, and PNG outputs.
* **ISO 42001 Traceability**: comprehensive logs, metadata, and version control.

*For a detailed breakdown of all options, see* **docs/features.md**.

## Quick Start

```bash
# Clone and install
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml
pip install -e .

# Run with default settings
pascal-zoning --input path/to/image.tif --output path/to/outdir
```

*More usage examples in* **docs/quick\_start.md**.

## System Requirements

* **Python** 3.11+
* **GDAL**, **rasterio**, **geopandas**
* Install other dependencies via `requirements.txt` and `requirements-dev.txt`.

## Contributing

1. Fork the repository and create a branch.
2. Implement changes and add tests.
3. Run `pytest && flake8` to verify.
4. Submit a pull request.

*Full guidelines in* **CONTRIBUTING.md**.

## License

This project is licensed under the **MIT License**. See **LICENSE** for details.

---

*For troubleshooting, advanced algorithm explanations, and output details, refer to the documentation in the `docs/` folder.*

