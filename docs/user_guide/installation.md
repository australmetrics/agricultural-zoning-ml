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

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone the Repository
```bash
# Clone the repository
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block
```

#### Step 2: Create Virtual Environment
**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env  # Linux/macOS
notepad .env  # Windows
```

#### Step 5: Verify Installation
```bash
python -m src.main --help
```

### Method 2: Development Installation

For contributors or advanced users who need access to development tools:

```bash
# Clone repository
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# Create virtual environment
python -m venv venv-dev
source venv-dev/bin/activate  # Linux/macOS
# or venv-dev\Scripts\activate  # Windows

# Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks (for contributors)
pre-commit install
```

## Platform-Specific Instructions

### Windows Installation

#### Prerequisites
1. **Python Installation**: Download from [python.org](https://python.org) or use Microsoft Store
2. **Visual C++ Build Tools**: Required for some dependencies
   ```cmd
   # Install using chocolatey (if available)
   choco install visualstudio2019buildtools
   ```

#### GDAL Configuration (if needed)
Some rasterio installations may require GDAL:
```cmd
# Using conda (recommended for Windows)
conda install -c conda-forge gdal
```

### Linux Installation (Ubuntu/Debian)

#### System Dependencies
```bash
# Update package manager
sudo apt update

# Install system dependencies
sudo apt install python3-pip python3-venv
sudo apt install gdal-bin libgdal-dev
sudo apt install python3-dev build-essential

# Set GDAL environment variables
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
```

### macOS Installation

#### Using Homebrew (Recommended)
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python gdal
```

#### Using MacPorts
```bash
sudo port install gdal +python39
```

## Configuration Setup

### Environment Variables

Edit the `.env` file with your specific configuration:

```bash
# User identification (for audit logs)
USERNAME=your_username

# Logging configuration
LOG_LEVEL=INFO

# Optional: Custom paths
DATA_PATH=data/
RESULTS_PATH=results/
```

### Directory Structure Verification

After installation, verify the directory structure:
```
pascal-ndvi-block/
├── data/                 # Input imagery (create if missing)
├── results/             # Output results (auto-created)
│   └── logs/           # ISO 42001 audit logs
├── src/                # Source code
├── tests/              # Unit tests
├── .env               # Configuration (you created this)
└── requirements.txt   # Dependencies
```

## Verification Tests

### Basic Functionality Test
```bash
# Test CLI access
python -m src.main --version

# Test with help command
python -m src.main --help
```

### Sample Data Test (if available)
```bash
# Create test directories
mkdir -p data results

# Run with sample data (if provided)
python -m src.main indices --image=data/sample.tif
```

## Troubleshooting Installation

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'rasterio'"
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Issue: GDAL Installation Problems
**Windows:**
```bash
# Use conda instead of pip
conda install -c conda-forge rasterio geopandas
```

**Linux:**
```bash
# Install system GDAL first
sudo apt install gdal-bin libgdal-dev
export GDAL_VERSION=$(gdal-config --version)
pip install GDAL==$GDAL_VERSION
```

#### Issue: Permission Errors (Windows)
**Solution:**
- Run Command Prompt/PowerShell as Administrator
- Or use `--user` flag: `pip install --user -r requirements.txt`

### Environment Validation

Create a simple test script to validate your installation:

```python
# test_installation.py
try:
    import rasterio
    import geopandas
    import numpy
    import typer
    import loguru
    print("✓ All dependencies successfully imported")
    print("✓ Installation completed successfully")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
```

Run with: `python test_installation.py`

## Next Steps

After successful installation:

1. **Read Quick Start Guide**: `docs/user_guide/quick_start.md`
2. **Explore Examples**: `docs/examples/basic_usage.md`
3. **Configure Logging**: Review ISO 42001 compliance features
4. **Prepare Data**: Place satellite imagery in `data/` directory

## Support

- **Installation Issues**: Create GitHub issue with system details
- **Dependency Conflicts**: Check `requirements.txt` compatibility
- **Platform-Specific Problems**: Include OS version and Python version in reports

---

**Note**: This installation follows ISO 42001 principles by providing clear, traceable installation procedures with comprehensive logging and validation steps.