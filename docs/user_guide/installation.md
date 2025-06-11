---
title: Installation
nav_order: 2
-------------

# Installation

Follow these steps to prepare your environment and install **Pascal Zoning ML**.

## Prerequisites

* Python 3.11 or higher
* GDAL 3.6+ (includes `gdal-bin` and `libgdal-dev` on Ubuntu/Debian)
* C compiler (e.g., `gcc`, `clang`)
* *(Optional)* `conda` or `pyenv` for Python version management

## Virtual Environment

Create and activate a virtual environment for project isolation:

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows use `.
```

## Install from PyPI

The easiest way to install:

```bash
pip install pascal-zoning
```

Verify the CLI is available:

```bash
pascal-zoning --help
```

## Install from Source

To install the latest development version:

```bash
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml
pip install -e .
```

Confirm the package version:

```bash
pascal-zoning --version
```

## Optional Dependencies

Install extras for extended functionality (metrics, telemetry):

```bash
pip install pascal-zoning[extras]
```

## Docker

For a containerized setup, build the provided Dockerfile:

```bash
docker build -t pascal-zoning:latest .
```

Then run:

```bash
docker run --rm -v "$(pwd)":/data pascal-zoning:latest pascal-zoning --help
```

## Uninstall

Remove the package easily:

```bash
pip uninstall pascal-zoning
```

---

For detailed dependency versions, please refer to `requirements.txt` and `requirements-dev.txt` in the repository. If you encounter any issues, open an issue on our [GitHub tracker](https://github.com/australmetrics/agricultural-zoning-ml/issues).

