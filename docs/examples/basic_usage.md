# Basic Usage Examples

© 2025 AustralMetrics SpA. All rights reserved.

This document provides practical examples for common use cases of the PASCAL NDVI Block module, designed for users who want to understand the basic functionality through real-world scenarios.

## Overview

PASCAL NDVI Block is designed around three core operations:
- **Index Calculation**: Generate vegetation indices from satellite imagery
- **Image Clipping**: Extract specific areas of interest
- **Automated Processing**: Complete workflows with minimal commands

All examples follow ISO 42001 compliance principles with full audit trails and reproducible results.

## Example 1: Basic Vegetation Index Calculation

### Scenario
You have a Sentinel-2 image of an agricultural area and want to calculate vegetation health indices.

### Input Data
```
data/
├── farm_sentinel2_20240515.tif    # Sentinel-2 L2A image
```

### Command
```bash
python -m src.main indices --image=data/farm_sentinel2_20240515.tif
```

### Expected Output
```
results/
├── farm_sentinel2_20240515_ndvi.tif    # NDVI index (-1 to +1)
├── farm_sentinel2_20240515_ndre.tif    # NDRE index (-1 to +1)
├── farm_sentinel2_20240515_savi.tif    # SAVI index (-1 to +1)
└── logs/
    ├── pascal_ndvi_20240515_143022.log  # Processing log
    └── pascal_ndvi_20240515_143022.log.sha256  # Integrity hash
```

### Understanding Results
- **NDVI > 0.5**: Dense, healthy vegetation (mature crops)
- **NDVI 0.2-0.5**: Moderate vegetation (young crops, grassland)
- **NDVI < 0.2**: Sparse or no vegetation (bare soil, water)

### Log Content
```
2024-05-15 14:30:22 | INFO | Starting NDVI processing for farm_sentinel2_20240515.tif
2024-05-15 14:30:23 | INFO | Detected bands: B04 (Red), B08 (NIR), B05 (Red Edge)
2024-05-15 14:30:25 | INFO | NDVI calculation completed successfully
2024-05-15 14:30:26 | INFO | NDRE calculation completed successfully
2024-05-15 14:30:27 | INFO | SAVI calculation completed successfully
2024-05-15 14:30:27 | INFO | Processing complete. Results saved to results/
```

## Example 2: Processing with Area of Interest

### Scenario
You have a large Landsat image but only need to analyze a specific watershed area defined by a shapefile.

### Input Data
```
data/
├── landsat8_region.tif        # Large Landsat 8 scene
└── watershed_boundary.shp     # Study area boundary
    ├── watershed_boundary.shx
    ├── watershed_boundary.dbf
    └── watershed_boundary.prj
```

### Step-by-Step Processing

#### Step 1: Clip to Area of Interest
```bash
python -m src.main clip --image=data/landsat8_region.tif --shapefile=data/watershed_boundary.shp
```

#### Step 2: Calculate Indices on Clipped Area
```bash
python -m src.main indices --image=results/landsat8_region_clipped.tif
```

### Alternative: Single Command
```bash
python -m src.main auto --image=data/landsat8_region.tif --shapefile=data/watershed_boundary.shp
```

### Expected Output
```
results/
├── landsat8_region_clipped.tif           # Clipped image
├── landsat8_region_clipped_ndvi.tif      # NDVI for watershed only
├── landsat8_region_clipped_ndre.tif      # NDRE for watershed only
├── landsat8_region_clipped_savi.tif      # SAVI for watershed only
└── logs/
    └── pascal_ndvi_[timestamp].log       # Complete processing log
```

## Example 3: Custom Output Directory

### Scenario
You're processing multiple projects and need organized output directories.

### Command
```bash
python -m src.main indices --image=data/project_alpha.tif --output=results/project_alpha_analysis
```

### Expected Output
```
results/
└── project_alpha_analysis/
    ├── project_alpha_ndvi.tif
    ├── project_alpha_ndre.tif
    ├── project_alpha_savi.tif
    └── logs/
        └── pascal_ndvi_[timestamp].log
```

## Example 4: Batch Processing Multiple Images

### Scenario
You have multiple images from different dates and want to process them all.

### Input Data
```
data/
├── field_20240401.tif
├── field_20240501.tif
├── field_20240601.tif
└── field_20240701.tif
```

### Bash Script (Linux/macOS)
```bash
#!/bin/bash
for image in data/field_*.tif; do
    echo "Processing $image..."
    python -m src.main indices --image="$image" --output="results/$(basename "$image" .tif)_analysis"
done
```

### PowerShell Script (Windows)
```powershell
Get-ChildItem data\field_*.tif | ForEach-Object {
    Write-Host "Processing $($_.Name)..."
    python -m src.main indices --image="$($_.FullName)" --output="results\$($_.BaseName)_analysis"
}
```

### Expected Output
```
results/
├── field_20240401_analysis/
│   ├── field_20240401_ndvi.tif
│   ├── field_20240401_ndre.tif
│   └── field_20240401_savi.tif
├── field_20240501_analysis/
│   └── [similar structure]
└── [additional dates...]
```

## Example 5: Working with Different Satellite Types

### Sentinel-2 Processing
```bash
# Sentinel-2 L1C or L2A images
python -m src.main indices --image=data/S2A_MSIL2A_20240515T103031_N0510_R108_T32TQM_20240515T135516.tif
```

### Landsat 8/9 Processing
```bash
# Landsat Collection 2 images
python -m src.main indices --image=data/LC08_L2SP_123032_20240515_20240517_02_T1.tif
```

### Generic GeoTIFF Processing
```bash
# Any multi-band GeoTIFF with appropriate bands
python -m src.main indices --image=data/multispectral_image.tif
```

## Example 6: Quality Control and Verification

### Verify Processing Success
```bash
# Check if all expected outputs were created
ls results/*_ndvi.tif results/*_ndre.tif results/*_savi.tif

# Verify file integrity
sha256sum results/logs/*.sha256
```

### Review Processing Logs
```bash
# View complete processing log
cat results/logs/pascal_ndvi_*.log

# Search for any errors or warnings
grep -i "error\|warning" results/logs/*.log

# Check processing statistics
grep "Processing complete" results/logs/*.log
```

### Validate Results
```bash
# Check image properties with GDAL
gdalinfo results/my_image_ndvi.tif

# Verify coordinate system
gdalsrsinfo results/my_image_ndvi.tif
```

## Example 7: Memory-Efficient Processing

### For Large Images
```bash
# Process with memory optimization (if supported)
python -m src.main indices --image=data/large_image.tif --output=/tmp/fast_storage
```

### Monitor System Resources
```bash
# Linux/macOS: Monitor during processing
top -p $(pgrep -f "python.*src.main")

# Windows: Use Task Manager or PowerShell
Get-Process python | Select-Object ProcessName, CPU, WorkingSet
```

## Understanding Command Options

### Common Parameters

| Parameter | Required | Description | Example Values |
|-----------|----------|-------------|----------------|
| `--image` | Yes | Input satellite image | `data/image.tif` |
| `--shapefile` | No | Clipping boundary | `data/boundary.shp` |
| `--output` | No | Output directory | `results/project1` |

### Help and Documentation
```bash
# General help
python -m src.main --help

# Command-specific help
python -m src.main indices --help
python -m src.main clip --help
python -m src.main auto --help
```

## Error Handling Examples

### Common Issues and Solutions

#### Missing Input File
```bash
# Command that will fail
python -m src.main indices --image=data/nonexistent.tif

# Error message guides you to the solution
# ERROR: Input file 'data/nonexistent.tif' not found
```

#### Invalid Shapefile
```bash
# Missing shapefile components
python -m src.main clip --image=data/image.tif --shapefile=data/incomplete.shp

# Error message indicates missing files (.shx, .dbf, .prj)
```

#### Insufficient Disk Space
```bash
# Check available space before processing
df -h results/  # Linux/macOS
Get-WmiObject -Class Win32_LogicalDisk  # Windows PowerShell
```

## Best Practices

### File Organization
```
project/
├── data/
│   ├── raw_imagery/      # Original satellite images
│   └── boundaries/       # Shapefiles for clipping
├── results/
│   ├── 2024_q1/         # Organized by time period
│   ├── 2024_q2/
│   └── final_analysis/   # Processed results
└── scripts/
    └── batch_process.sh  # Automation scripts
```

### Naming Conventions
- Use descriptive filenames: `farm_field1_sentinel2_20240515.tif`
- Include dates in ISO format: `YYYYMMDD`
- Separate project phases: `preliminary_`, `final_`

### Documentation
- Keep processing logs for audit trails
- Document coordinate systems and projections
- Record processing parameters for reproducibility

---

These examples demonstrate the core functionality of PASCAL NDVI Block while maintaining full ISO 42001 compliance through comprehensive logging and audit trails. Each operation is designed to be simple, reliable, and fully traceable for professional remote sensing workflows.