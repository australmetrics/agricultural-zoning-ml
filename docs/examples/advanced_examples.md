# Advanced Examples

This document demonstrates **advanced use‐cases** of Pascal Zoning ML, including:

1. Batch processing multiple fields  
2. Custom cluster‐metrics export  
3. Integration with downstream analytics (e.g., automated report generation)  
4. Programmatic hooks for ISO 42001–level traceability  

By the end of this guide, you'll be able to adapt the pipeline into larger workflows, export custom artifacts, and enforce quality controls.

---

This document provides advanced usage examples for PASCAL NDVI Block, designed for power users, researchers, and organizations requiring complex remote sensing workflows with full ISO 42001 compliance.

## 1. Batch Processing Multiple Fields

Often, agronomists need to run zonification on **dozens or hundreds of fields**. Instead of invoking the CLI separately, you can write a simple Python script that iterates over a list of input GeoTIFFs and processes them in parallel, while maintaining ISO 42001 traceability.

### 1.1 Directory Structure

Assume you have a folder tree like this:

```
project_root/
├── inputs/
│   ├── field_A.tif
│   ├── field_B.tif
│   └── field_C.tif
├── configs/
│   └── batch_config.yaml
├── outputs/    # Empty initially
└── scripts/
    └── batch_run.py
```

- `inputs/` holds multiple GeoTIFFs, each clipped to a separate field.  
- `configs/batch_config.yaml` contains shared parameters (e.g., `min_zone_size_ha`, `max_zones`).  
- `scripts/batch_run.py` is our batch‐processing driver.  

### 1.2 batch_config.yaml

```yaml
zoning:
  random_state: 2025
  min_zone_size_ha: 0.25
  max_zones: 6

sampling:
  points_per_zone: 8
```

### 1.3 batch_run.py

```python
#!/usr/bin/env python3
import argparse
import glob
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import geopandas as gpd
import numpy as np
from rasterio import open as rio_open

from pascal_zoning.config import ZoningConfig
from pascal_zoning.zoning import AgriculturalZoning

def compute_spectral_indices(raster_path: Path) -> dict[str, np.ndarray]:
    """
    Reads a multiband GeoTIFF and computes NDVI, NDWI, NDRE, SI.
    Assumes bands order: [SWIR, NIR, RED_EDGE, RED, GREEN].
    """
    with rio_open(raster_path) as src:
        img = src.read().astype(np.float64)  # shape: (bands, H, W)
        crs = src.crs.to_string()
        transform = src.transform

    # Bands indexing (1-based in rasterio): 
    # SWIR = img[0], NIR = img[1], RED_EDGE = img[2], RED = img[3], GREEN = img[4]
    def safe_div(a, b):
        with np.errstate(divide="ignore", invalid="ignore"):
            out = np.divide(a - b, a + b, out=np.zeros_like(a), where=(a + b) != 0)
            return np.nan_to_num(out, nan=0.0)

    indices = {
        "NDVI": safe_div(img[1], img[3]),         # (NIR - RED)/(NIR + RED)
        "NDWI": safe_div(img[4], img[1]),         # (GREEN - NIR)/(GREEN + NIR)
        "NDRE": safe_div(img[1], img[2]),         # (NIR - RED_EDGE)/(NIR + RED_EDGE)
        "SI":   safe_div(img[0], img[1]),         # (SWIR - NIR)/(SWIR + NIR)
    }
    return indices, crs, transform

def process_single_field(
    raster_path_str: str, 
    config_path: str, 
    output_base: str
) -> str:
    """
    Processes one field: computes indices, runs zoning, and returns the timestamped output folder.
    """
    raster_path = Path(raster_path_str)
    field_name = raster_path.stem  # e.g., "field_A"
    output_base_dir = Path(output_base) / field_name
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # 1) Compute spectral indices
    indices_dict, crs, transform = compute_spectral_indices(raster_path)

    # 2) Build a GeoDataFrame for the field boundary (assume mask of >0 on band 1)
    with rio_open(raster_path) as src:
        mask_band = src.read(1)
        # derive polygon(s) from nonzero pixels
        from rasterio.features import shapes
        from shapely.ops import unary_union
        from shapely.geometry import shape as shapely_shape

        geoms = []
        for geom_geojson, val in shapes(mask_band, mask=(mask_band > 0), transform=src.transform):
            geoms.append(shapely_shape(geom_geojson))
        if not geoms:
            raise RuntimeError(f"No valid pixels for field {field_name}")
        field_polygon = unary_union(geoms)

    # 3) Load shared config
    app_config = ZoningConfig.from_yaml(config_path)

    # 4) Instantiate engine from config
    zoning = AgriculturalZoning.from_config(app_config)
    zoning.output_dir = output_base_dir  # override per‐field

    # 5) Run pipeline
    result = zoning.run_pipeline(
        indices=indices_dict,
        bounds=field_polygon,
        points_per_zone=app_config.sampling.points_per_zone,
        crs=crs,
        force_k=None            # let auto‐select k
    )

    return f"{field_name}: completed → {result.metrics.n_clusters} zones"

def main():
    parser = argparse.ArgumentParser(
        description="Batch run Pascal Zoning ML on multiple fields."
    )
    parser.add_argument(
        "--inputs-dir", 
        type=str, 
        required=True,
        help="Directory containing input GeoTIFFs (one per field)."
    )
    parser.add_argument(
        "--config", 
        type=str, 
        required=True,
        help="Path to shared config.yaml"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        required=True,
        help="Base output directory for all fields."
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=2,
        help="Number of parallel workers"
    )
    args = parser.parse_args()

    rasters = glob.glob(os.path.join(args.inputs_dir, "*.tif"))
    if not rasters:
        print("No .tif files found in inputs dir.")
        return

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for r in rasters:
            futures.append(
                executor.submit(process_single_field, r, args.config, args.output_dir)
            )
        for future in as_completed(futures):
            try:
                msg = future.result()
                print(f"[OK] {msg}")
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
```

Key points:
- We use a ProcessPoolExecutor to parallelize per‐field runs.
- Each field's outputs land under `outputs/{field_name}/YYYYMMDD_HHMMSS_k{K}_mz{min_zone_size}/`.
- Field boundaries are derived via `rasterio.features.shapes()` → `shapely.geometry`.
- We read a single `config.yaml` and feed into each engine via `.from_config()`.

## Advanced Processing Workflows

### Temporal Analysis (Time Series)

#### Scenario: Crop Growth Monitoring
Monitor vegetation changes across an entire growing season using multiple satellite acquisitions.

#### Input Data Structure
```
data/
├── temporal_analysis/
│   ├── field_20240301_sentinel2.tif  # Early season
│   ├── field_20240401_sentinel2.tif  # Spring growth
│   ├── field_20240501_sentinel2.tif  # Peak growth
│   ├── field_20240601_sentinel2.tif  # Maturity
│   └── field_20240701_sentinel2.tif  # Harvest
└── boundaries/
    └── field_boundary.shp
```

#### Processing Script
```bash
#!/bin/bash
# Advanced temporal analysis workflow

# Create organized output structure
mkdir -p results/temporal_analysis/{raw_indices,clipped_indices,analysis_summary}

# Process each time step
for date in 20240301 20240401 20240501 20240601 20240701; do
    echo "Processing date: $date"
    
    # Step 1: Clip to field boundary
    python -m src.main clip \
        --image="data/temporal_analysis/field_${date}_sentinel2.tif" \
        --shapefile="data/boundaries/field_boundary.shp" \
        --output="results/temporal_analysis/clipped_indices"
    
    # Step 2: Calculate indices on clipped area
    python -m src.main indices \
        --image="results/temporal_analysis/clipped_indices/field_${date}_sentinel2_clipped.tif" \
        --output="results/temporal_analysis/raw_indices/${date}"
    
    echo "Completed processing for $date"
done

# Generate processing summary
echo "Temporal analysis completed on $(date)" > results/temporal_analysis/analysis_summary/processing_summary.txt
ls results/temporal_analysis/raw_indices/*/field_*_ndvi.tif >> results/temporal_analysis/analysis_summary/processing_summary.txt
```

#### Expected Output Structure
```
results/temporal_analysis/
├── raw_indices/
│   ├── 20240301/
│   │   ├── field_20240301_sentinel2_clipped_ndvi.tif
│   │   ├── field_20240301_sentinel2_clipped_ndre.tif
│   │   └── field_20240301_sentinel2_clipped_savi.tif
│   └── [additional dates...]
├── clipped_indices/
│   └── [clipped imagery for each date]
├── analysis_summary/
│   └── processing_summary.txt
└── logs/
    └── [comprehensive audit trail for all operations]
```

### Multi-Site Analysis

#### Scenario: Regional Agricultural Assessment
Process multiple fields across different locations with standardized methodology.

#### Data Structure
```
data/
├── sites/
│   ├── site_001/
│   │   ├── sentinel2_image.tif
│   │   └── field_boundaries.shp
│   ├── site_002/
│   │   ├── landsat8_image.tif
│   │   └── field_boundaries.shp
│   └── site_003/
│       ├── sentinel2_image.tif
│       └── field_boundaries.shp
```

#### Advanced Processing Script
```bash
#!/bin/bash
# Multi-site processing with standardized outputs

# Configuration
PROJECT_NAME="regional_assessment_2024"
OUTPUT_BASE="results/${PROJECT_NAME}"
LOG_SUMMARY="${OUTPUT_BASE}/processing_summary.log"

# Initialize project structure
mkdir -p "${OUTPUT_BASE}"/{site_results,project_logs,quality_control}

# Initialize summary log
echo "Regional Assessment Processing Started: $(date)" > "$LOG_SUMMARY"
echo "ISO 42001 Compliance: Full audit trail enabled" >> "$LOG_SUMMARY"
echo "Project: $PROJECT_NAME" >> "$LOG_SUMMARY"
echo "========================================" >> "$LOG_SUMMARY"

# Process each site
for site_dir in data/sites/site_*; do
    site_name=$(basename "$site_dir")
    echo "Processing $site_name..."
    
    # Find image file (handles both Sentinel-2 and Landsat)
    image_file=$(find "$site_dir" -name "*.tif" -type f)
    boundary_file=$(find "$site_dir" -name "*.shp" -type f)
    
    if [[ -n "$image_file" && -n "$boundary_file" ]]; then
        # Process with automated workflow
        python -m src.main auto \
            --image="$image_file" \
            --shapefile="$boundary_file" \
            --output="${OUTPUT_BASE}/site_results/${site_name}"
        
        # Log processing completion
        echo "$site_name: SUCCESS - $(date)" >> "$LOG_SUMMARY"
        
        # Quality control check
        expected_files=("*_ndvi.tif" "*_ndre.tif" "*_savi.tif")
        for pattern in "${expected_files[@]}"; do
            if ls "${OUTPUT_BASE}/site_results/${site_name}/"$pattern 1> /dev/null 2>&1; then
                echo "  ✓ $pattern files created" >> "$LOG_SUMMARY"
            else
                echo "  ✗ Missing $pattern files" >> "$LOG_SUMMARY"
            fi
        done
    else
        echo "$site_name: ERROR - Missing required files" >> "$LOG_SUMMARY"
    fi
done

# Generate final summary
echo "========================================" >> "$LOG_SUMMARY"
echo "Processing completed: $(date)" >> "$LOG_SUMMARY"
total_sites=$(ls -d "${OUTPUT_BASE}/site_results/"*/ 2>/dev/null | wc -l)
echo "Total sites processed: $total_sites" >> "$LOG_SUMMARY"
```

### Complex Multi-Sensor Fusion

#### Scenario: Combining Sentinel-2 and Landsat Data
Integrate data from multiple satellite sensors for comprehensive analysis.

#### Data Preparation
```
data/
├── fusion_analysis/
│   ├── sentinel2/
│   │   ├── S2_20240515_field1.tif
│   │   └── S2_20240530_field1.tif
│   ├── landsat8/
│   │   ├── L8_20240507_field1.tif
│   │   └── L8_20240523_field1.tif
│   └── boundaries/
│       └── study_area.shp
```

#### Advanced Fusion Workflow
```bash
#!/bin/bash
# Multi-sensor data fusion workflow

PROJECT="sensor_fusion_analysis"
mkdir -p "results/${PROJECT}"/{sentinel2,landsat8,comparative_analysis}

echo "Multi-Sensor Fusion Analysis - ISO 42001 Compliant" > "results/${PROJECT}/fusion_log.txt"
echo "Analysis started: $(date)" >> "results/${PROJECT}/fusion_log.txt"

# Process Sentinel-2 data
echo "Processing Sentinel-2 imagery..." >> "results/${PROJECT}/fusion_log.txt"
for s2_image in data/fusion_analysis/sentinel2/*.tif; do
    base_name=$(basename "$s2_image" .tif)
    python -m src.main auto \
        --image="$s2_image" \
        --shapefile="data/fusion_analysis/boundaries/study_area.shp" \
        --output="results/${PROJECT}/sentinel2/${base_name}_analysis"
    
    echo "  Completed: $base_name" >> "results/${PROJECT}/fusion_log.txt"
done

# Process Landsat data
echo "Processing Landsat-8 imagery..." >> "results/${PROJECT}/fusion_log.txt"
for l8_image in data/fusion_analysis/landsat8/*.tif; do
    base_name=$(basename "$l8_image" .tif)
    python -m src.main auto \
        --image="$l8_image" \
        --shapefile="data/fusion_analysis/boundaries/study_area.shp" \
        --output="results/${PROJECT}/landsat8/${base_name}_analysis"
    
    echo "  Completed: $base_name" >> "results/${PROJECT}/fusion_log.txt"
done

# Generate comparative analysis summary
echo "Fusion analysis completed: $(date)" >> "results/${PROJECT}/fusion_log.txt"
echo "Results available for cross-sensor validation" >> "results/${PROJECT}/fusion_log.txt"
```

## Enterprise-Level Automation

### Large-Scale Processing Pipeline

#### Configuration File Approach
Create a configuration file for standardized processing:

```yaml
# config/processing_config.yaml
project:
  name: "enterprise_vegetation_monitoring"
  version: "1.0"
  iso42001_compliance: true

input:
  base_path: "data/enterprise/"
  imagery_pattern: "*.tif"
  boundary_pattern: "*.shp"

output:
  base_path: "results/enterprise/"
  create_dated_folders: true
  preserve_structure: true

processing:
  indices: ["ndvi", "ndre", "savi"]
  clip_to_boundaries: true
  quality_control: true
  generate_reports: true

logging:
  level: "INFO"
  create_summary: true
  backup_logs: true
```

#### Enterprise Processing Script
```bash
#!/bin/bash
# Enterprise-level processing with configuration management

# Configuration
CONFIG_FILE="config/processing_config.yaml"
ENTERPRISE_LOG="results/enterprise/enterprise_processing_$(date +%Y%m%d_%H%M%S).log"

# Create enterprise directory structure
mkdir -p results/enterprise/{processed_data,quality_reports,audit_logs,backup}

# Initialize enterprise logging
echo "PASCAL NDVI Block - Enterprise Processing" > "$ENTERPRISE_LOG"
echo "ISO 42001 Compliance Level: FULL" >> "$ENTERPRISE_LOG"
echo "Processing initiated: $(date)" >> "$ENTERPRISE_LOG"
echo "Configuration: $CONFIG_FILE" >> "$ENTERPRISE_LOG"
echo "==========================================" >> "$ENTERPRISE_LOG"

# Discover all processing units
find data/enterprise -name "*.tif" -type f > /tmp/imagery_list.txt
find data/enterprise -name "*.shp" -type f > /tmp/boundary_list.txt

echo "Discovered $(wc -l < /tmp/imagery_list.txt) imagery files" >> "$ENTERPRISE_LOG"
echo "Discovered $(wc -l < /tmp/boundary_list.txt) boundary files" >> "$ENTERPRISE_LOG"

# Process each imagery-boundary pair
while IFS= read -r image_file; do
    # Extract directory and find corresponding boundary
    image_dir=$(dirname "$image_file")
    boundary_file=$(find "$image_dir" -name "*.shp" -type f | head -1)
    
    if [[ -n "$boundary_file" ]]; then
        # Generate unique output directory
        timestamp=$(date +%Y%m%d_%H%M%S)
        image_base=$(basename "$image_file" .tif)
        output_dir="results/enterprise/processed_data/${image_base}_${timestamp}"
        
        echo "Processing: $image_file with boundary: $boundary_file" >> "$ENTERPRISE_LOG"
        
        # Execute processing with full audit trail
        python -m src.main auto \
            --image="$image_file" \
            --shapefile="$boundary_file" \
            --output="$output_dir" 2>&1 | tee -a "$ENTERPRISE_LOG"
        
        # Quality control validation
        if [[ -d "$output_dir" ]]; then
            file_count=$(find "$output_dir" -name "*_ndvi.tif" -o -name "*_ndre.tif" -o -name "*_savi.tif" | wc -l)
            if [[ $file_count -eq 3 ]]; then
                echo "  ✓ Quality Control: PASSED ($file_count/3 indices generated)" >> "$ENTERPRISE_LOG"
            else
                echo "  ✗ Quality Control: FAILED ($file_count/3 indices generated)" >> "$ENTERPRISE_LOG"
            fi
        fi
    else
        echo "WARNING: No boundary file found for $image_file" >> "$ENTERPRISE_LOG"
    fi
done < /tmp/imagery_list.txt

# Generate enterprise summary report
echo "==========================================" >> "$ENTERPRISE_LOG"
echo "Enterprise processing completed: $(date)" >> "$ENTERPRISE_LOG"
total_outputs=$(find results/enterprise/processed_data -name "*_ndvi.tif" | wc -l)
echo "Total NDVI outputs generated: $total_outputs" >> "$ENTERPRISE_LOG"

# Backup logs for ISO 42001 compliance
cp "$ENTERPRISE_LOG" "results/enterprise/audit_logs/"
cp results/enterprise/processed_data/*/logs/*.log "results/enterprise/audit_logs/" 2>/dev/null

echo "Enterprise processing pipeline completed successfully"
```

## Performance Optimization Techniques

### Memory-Efficient Processing
For large datasets or limited hardware resources:

```bash
#!/bin/bash
# Memory-optimized processing for large datasets

# System resource monitoring
monitor_resources() {
    echo "Memory usage: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')"
    echo "Disk usage: $(df -h results/ | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
}

# Process with resource constraints
process_with_limits() {
    local image="$1"
    local output="$2"
    
    echo "Starting resource-monitored processing..."
    monitor_resources
    
    # Use system limits to prevent memory overflow
    ulimit -v 4000000  # Limit virtual memory to ~4GB
    
    python -m src.main indices --image="$image" --output="$output"
    
    echo "Processing completed. Final resource status:"
    monitor_resources
}

# Example usage
process_with_limits "data/large_image.tif" "results/memory_optimized"
```

### Parallel Processing for Multiple Files
```bash
#!/bin/bash
# Parallel processing with controlled concurrency

MAX_PARALLEL=4  # Adjust based on system capabilities
PROJECT="parallel_processing"

mkdir -p "results/${PROJECT}/parallel_logs"

# Function to process single image
process_single() {
    local image="$1"
    local index="$2"
    local base_name=$(basename "$image" .tif)
    
    echo "Worker $index: Starting processing of $base_name"
    
    python -m src.main indices \
        --image="$image" \
        --output="results/${PROJECT}/${base_name}_analysis" \
        > "results/${PROJECT}/parallel_logs/worker_${index}_${base_name}.log" 2>&1
    
    echo "Worker $index: Completed $base_name"
}

# Export function for parallel execution
export -f process_single
export PROJECT

# Find all images and process in parallel
find data/ -name "*.tif" -type f | \
    head -20 | \
    parallel -j $MAX_PARALLEL --line-buffer process_single {} {#}

echo "Parallel processing completed for $PROJECT"
```

## Advanced Quality Control

### Comprehensive Validation Pipeline
```bash
#!/bin/bash
# Advanced quality control and validation

QC_PROJECT="quality_control_validation"
mkdir -p "results/${QC_PROJECT}"/{validation_reports,failed_processing,statistics}

# Quality control function
validate_processing() {
    local result_dir="$1"
    local validation_log="results/${QC_PROJECT}/validation_reports/$(basename "$result_dir")_validation.txt"
    
    echo "Quality Control Validation Report" > "$validation_log"
    echo "Generated: $(date)" >> "$validation_log"
    echo "Result Directory: $result_dir" >> "$validation_log"
    echo "==============================" >> "$validation_log"
    
    # Check for required output files
    indices=("ndvi" "ndre" "savi")
    for index in "${indices[@]}"; do
        index_file=$(find "$result_dir" -name "*_${index}.tif" -type f)
        if [[ -n "$index_file" ]]; then
            # Validate file properties with GDAL
            echo "✓ $index file exists: $index_file" >> "$validation_log"
            
            # Check file size (should be > 0)
            file_size=$(stat -f%z "$index_file" 2>/dev/null || stat -c%s "$index_file" 2>/dev/null)
            echo "  File size: $file_size bytes" >> "$validation_log"
            
            # Validate with gdalinfo (if available)
            if command -v gdalinfo >/dev/null 2>&1; then
                echo "  GDAL Info:" >> "$validation_log"
                gdalinfo "$index_file" | head -10 >> "$validation_log"
            fi
        else
            echo "✗ Missing $index file" >> "$validation_log"
        fi
    done
    
    # Check processing logs
    log_files=$(find "$result_dir" -name "*.log" -type f)
    if [[ -n "$log_files" ]]; then
        echo "✓ Processing logs available" >> "$validation_log"
        error_count=$(grep -c "ERROR" $log_files 2>/dev/null || echo "0")
        warning_count=$(grep -c "WARNING" $log_files 2>/dev/null || echo "0")
        echo "  Errors found: $error_count" >> "$validation_log"
        echo "  Warnings found: $warning_count" >> "$validation_log"
    else
        echo "✗ No processing logs found" >> "$validation_log"
    fi
    
    echo "Validation completed: $(date)" >> "$validation_log"
}

# Run validation on all results
for result_dir in results/*/; do
    if [[ -d "$result_dir" && "$result_dir" != "results/${QC_PROJECT}/" ]]; then
        validate_processing "$result_dir"
    fi
done

echo "Quality control validation completed for all results"
```

## Integration with External Tools

### GDAL Integration for Advanced Processing
```bash
#!/bin/bash
# Integration with GDAL tools for advanced geospatial operations

# Function to enhance PASCAL NDVI results with GDAL processing
enhance_with_gdal() {
    local ndvi_file="$1"
    local output_dir="$(dirname "$ndvi_file")/enhanced"
    
    mkdir -p "$output_dir"
    
    # Generate overview pyramids for faster visualization
    echo "Creating overview pyramids..."
    gdaladdo -r average "$ndvi_file" 2 4 8 16 32
    
    # Create hillshade for visualization (if DEM available)
    if [[ -f "data/dem.tif" ]]; then
        echo "Creating hillshade visualization..."
        gdaldem hillshade "data/dem.tif" "$output_dir/hillshade.tif"
    fi
    
    # Convert to different formats for various applications
    echo "Converting to additional formats..."
    gdal_translate -of GTiff -co COMPRESS=LZW "$ndvi_file" "$output_dir/ndvi_compressed.tif"
    gdal_translate -of PNG "$ndvi_file" "$output_dir/ndvi_preview.png"
    
    # Generate statistics
    echo "Computing statistics..."
    gdalinfo -stats "$ndvi_file" > "$output_dir/ndvi_statistics.txt"
    
    echo "GDAL enhancement completed for $ndvi_file"
}

# Apply GDAL enhancements to all NDVI results
find results/ -name "*_ndvi.tif" -type f | while read ndvi_file; do
    enhance_with_gdal "$ndvi_file"
done
```

### Database Integration
```bash
#!/bin/bash
# Integration with PostGIS database for spatial data management

DB_CONFIG="postgresql://user:password@localhost:5432/vegetation_monitoring"

# Function to import results to PostGIS
import_to_postgis() {
    local raster_file="$1"
    local table_name="vegetation_indices"
    
    # Import raster to PostGIS
    raster2pgsql -s 4326 -I -C -M "$raster_file" "$table_name" | psql "$DB_CONFIG"
    
    echo "Imported $raster_file to PostGIS table $table_name"
}

# Import all NDVI results to database
find results/ -name "*_ndvi.tif" -type f | while read raster_file; do
    import_to_postgis "$raster_file"
done
```

## 2. Custom Cluster-Metrics Export

By default, Pascal Zoning ML writes a JSON (`metricas_clustering.json`) containing:

```jsonc
{
  "n_clusters": 4,
  "silhouette": 0.7321,
  "calinski_harabasz": 1200.5,
  "inertia": 350.2,
  "cluster_sizes": { "0": 25, "1": 30, "2": 28, "3": 32 },
  "timestamp": "2025-06-04 16:45:32"
}
```

If you need additional metrics—for example, Davies–Bouldin score, gap statistic, or a DataFrame summarizing per‐cluster centroids—you can extend the implementation:

### 2.1 Extending ClusterMetrics & adding DB score

```python
from sklearn.metrics import davies_bouldin_score

@dataclass
class ClusterMetrics:
    n_clusters: int
    silhouette: float
    calinski_harabasz: float
    inertia: float
    cluster_sizes: Dict[int, int]
    db_score: float               # NEW
    timestamp: str

class AgriculturalZoning:
    # ... existing code ...

    def perform_clustering(self, force_k: Optional[int] = None) -> None:
        # existing cluster logic...
        labels_flat = kmeans_final.labels_
        # Compute DB score (lower is better)
        db_score = float(davies_bouldin_score(self.features_array, labels_flat))
        # Extend our metrics dataclass
        self.metrics.db_score = db_score
```

In your pipeline run, after `run_pipeline()`, you can access:

```python
result = zoning.run_pipeline(...)
print(f"Davies-Bouldin score: {result.metrics.db_score:.4f}")
```

## 3. Integration with Downstream Analytics

You may want to take clustering results and auto‐generate a PDF report, populate a database, or trigger alerts. Here's an example of integrating with pandas, Matplotlib, and Jinja2 to auto‐build a PDF.

### 3.1 Generating a PDF summary

Install additional dependencies:

```bash
pip install pandas matplotlib jinja2 weasyprint
```

Structure:
```
project_root/
├── templates/
│   └── zoning_report.html.j2
├── scripts/
│   ├── batch_run.py
│   └── generate_report.py
└── ...
```

#### 3.1.1 templates/zoning_report.html.j2

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Pascal Zoning Report — {{ field_name }}</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 1cm; }
      h1, h2, h3 { color: #2c3e50; }
      table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
      th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
      th { background-color: #f2f2f2; }
      .figure { margin: 1em 0; text-align: center; }
    </style>
  </head>
  <body>
    <h1>Pascal Zoning Report</h1>
    <h2>Field: {{ field_name }}</h2>
    <p><strong>Timestamp:</strong> {{ timestamp }}</p>

    <h3>Clustering Summary</h3>
    <ul>
      <li>Number of zones: {{ metrics.n_clusters }}</li>
      <li>Silhouette score: {{ metrics.silhouette | round(4) }}</li>
      <li>Calinski-Harabasz index: {{ metrics.calinski_harabasz | round(2) }}</li>
      <li>Inertia: {{ metrics.inertia | round(2) }}</li>
      {% if metrics.db_score is defined %}
      <li>Davies-Bouldin score: {{ metrics.db_score | round(4) }}</li>
      {% endif %}
    </ul>

    <h3>Zone Statistics</h3>
    <table>
      <thead>
        <tr>
          <th>Zone ID</th>
          <th>Area (ha)</th>
          <th>Perimeter (m)</th>
          <th>Compactness</th>
          {% for idx in index_names %}
          <th>{{ idx }} Mean</th>
          <th>{{ idx }} Std</th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% for stat in stats_list %}
        <tr>
          <td>{{ stat.zone_id }}</td>
          <td>{{ stat.area_ha | round(4) }}</td>
          <td>{{ stat.perimeter_m | round(2) }}</td>
          <td>{{ stat.compactness | round(4) }}</td>
          {% for idx in index_names %}
          <td>{{ stat.mean_values[idx] | round(4) }}</td>
          <td>{{ stat.std_values[idx] | round(4) }}</td>
          {% endfor %}
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <h3>Figures</h3>
    <div class="figure">
      <h4>NDVI Map</h4>
      {% if figures.mapa_ndvi %}
      <img src="{{ figures.mapa_ndvi }}" alt="NDVI Map" width="600" />
      {% else %}
      <p><em>No NDVI provided.</em></p>
      {% endif %}
    </div>
    <div class="figure">
      <h4>Cluster Map</h4>
      <img src="{{ figures.mapa_clusters }}" alt="Cluster Map" width="600" />
    </div>
    <div class="figure">
      <h4>Overview Chart</h4>
      <img src="{{ figures.zonificacion_results }}" alt="Overview Chart" width="600" />
    </div>
  </body>
</html>
```

#### 3.1.2 generate_report.py

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def load_manifest(manifest_path: Path) -> dict:
    with open(manifest_path, "r") as f:
        return json.load(f)

def generate_pdf_report(manifest: dict, template_dir: Path, output_pdf: Path):
    # Extract field name from manifest (assume input raster path ends in <field>.tif)
    input_raster = Path(manifest["interfaces"]["input"]["raster"])
    field_name = input_raster.stem

    # Load metrics JSON
    metrics_path = Path(manifest["interfaces"]["output"]["json"])
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    # Load CSV into DataFrame
    stats_path = Path(manifest["interfaces"]["output"]["csv"])
    df_stats = pd.read_csv(stats_path)

    # Build ZoneStats list of dicts
    stats_list = []
    index_columns = [col for col in df_stats.columns if col not in ("zone_id", "area_ha", "perimeter_m", "compactness")]
    index_names = sorted({col.rsplit("_", 1)[0] for col in index_columns})

    for _, row in df_stats.iterrows():
        mean_vals = {idx: row[f"{idx}_mean"] for idx in index_names}
        std_vals = {idx: row[f"{idx}_std"] for idx in index_names}
        stats_list.append({
            "zone_id": int(row["zone_id"]),
            "area_ha": float(row["area_ha"]),
            "perimeter_m": float(row["perimeter_m"]),
            "compactness": float(row["compactness"]),
            "mean_values": mean_vals,
            "std_values": std_vals,
        })

    # Collect figure paths
    figures = {
        "mapa_ndvi": manifest["interfaces"]["output"]["png"].get("mapa_ndvi"),
        "mapa_clusters": manifest["interfaces"]["output"]["png"]["mapa_clusters"],
        "zonificacion_results": manifest["interfaces"]["output"]["png"]["zonificacion_results"],
    }

    # Jinja2 template rendering
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("zoning_report.html.j2")

    html_content = template.render(
        field_name=field_name,
        timestamp=manifest["timestamp"],
        metrics=metrics,
        stats_list=stats_list,
        index_names=index_names,
        figures=figures,
    )

    # Generate PDF
    HTML(string=html_content, base_url=str(template_dir)).write_pdf(str(output_pdf))
    print(f"[REPORT] Generated PDF: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: generate_report.py <manifest.json> <templates_dir> <output.pdf>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    template_dir = Path(sys.argv[2])
    output_pdf = Path(sys.argv[3])
    manifest = load_manifest(manifest_path)
    generate_pdf_report(manifest, template_dir, output_pdf)
```

After running Pascal Zoning ML on field_A.tif, you have:

```
outputs/field_A/20250604_170000_k4_mz0.25/
├── zonificacion_agricola.gpkg
├── puntos_muestreo.gpkg
├── mapa_ndvi.png
├── mapa_clusters.png
├── estadisticas_zonas.csv
├── metricas_clustering.json
├── zonificacion_results.png
└── manifest_zoning.json
```

Run:

```powershell
python scripts/generate_report.py `
  outputs/field_A/20250604_170000_k4_mz0.25/manifest_zoning.json `
  templates/ `
  outputs/field_A/20250604_170000_k4_mz0.25/field_A_report.pdf
```

This integration ensures ISO 42001 compliance by capturing:
- Exact file paths
- Timestamps of processing
- Version of Pascal Zoning ML used (from the manifest)
- Per‐zone metrics

## 4. ISO 42001–Level Traceability Hooks

To comply with ISO 42001, you must demonstrate:
- Traceability of each run (who, when, how)
- Version control of code & dependencies
- Audit‐ready logs & manifests

### 4.1 Extended Manifest Schema

Use `schemas/zoning_output.schema.json` to validate your output manifest:

```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PASCAL Zoning ML Output Manifest",
  "type": "object",
  "required": ["version", "timestamp", "input_image", "outputs", "metadata"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "input_image": {
      "type": "object",
      "required": ["path", "bands", "crs", "transform"]
      // ...
    },
    "outputs": {
      "type": "object",
      "required": ["geopackages", "csv", "json", "png"]
      // ...
    },
    "metadata": {
      "type": "object",
      "required": ["processing_time", "software_version"]
      // ...
    }
  }
}
```

You can validate it manually:

```powershell
check-jsonschema `
  --schemafile schemas/zoning_output.schema.json `
  outputs/field_A/20250604_170000_k4_mz0.25/manifest_zoning.json
```

### 4.2 Logging & Audit Trail

Configure Loguru to write logs to both console and a timestamped log file:

```python
from loguru import logger
import os

# In main CLI entrypoint:
timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
log_dir = Path(output_dir) / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / f"run_{timestamp}.log"

logger.remove()  # Remove default handler
logger.add(sys.stderr, level=os.getenv("ZONING_LOG_LEVEL", "INFO"))
logger.add(str(log_path), level="DEBUG", rotation="10 MB", retention="7 days")

logger.info(f"Starting Pascal Zoning ML v{__version__} at {timestamp}")
```

The final output folder contains:
```
logs/run_20250604T170000Z.log
manifest_zoning.json
zonificacion_agricola.gpkg
puntos_muestreo.gpkg
...
```

### 4.3 Git Commit & Dependency Freeze

Before running a production‐grade batch:

Record the Git commit SHA:
```powershell
$GIT_SHA = git rev-parse HEAD
$JSON = "{`"git_sha`": `"$GIT_SHA`"}"
Add-Content `
  outputs/field_A/20250604_170000_k4_mz0.25/manifest_zoning.json `
  -Value $JSON
```

Freeze Python dependencies:
```powershell
pip freeze > outputs/field_A/20250604_170000_k4_mz0.25/requirements_frozen.txt
```

Include these two files alongside your manifest to satisfy ISO 42001's requirement for "Documented dependency versions" and "Exact code version used."

## 5. Continuous Integration (CI)

To maintain ISO 42001 compliance, ensure that every code push triggers:
- Linting (flake8, black)
- Type checks (mypy, pyright)
- Unit tests (pytest tests/unit)
- Integration tests (pytest tests/integration)

### 5.1 GitHub Actions Workflow Example

```yaml
# .github/workflows/ci.yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install dev requirements
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Black Check
        run: black --check src/
      - name: Flake8
        run: flake8 src/

  typecheck:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install core requirements
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install mypy pyright
      - name: MyPy
        run: mypy src/
      - name: Pyright
        run: pyright

  test:
    runs-on: ubuntu-latest
    needs: [lint, typecheck]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install requirements
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run Unit Tests
        run: pytest tests/unit --maxfail=1 --disable-warnings -q
      - name: Run Integration Tests
        run: pytest tests/integration --maxfail=1 --disable-warnings -q
```

This ensures that every push/PR is validated, fulfilling ISO 42001's "Continuous Quality Control" requirement.

## 6. Summary

- **Batch Processing**: Leverage ProcessPoolExecutor + shared config for multiple fields.
- **Custom Metrics**: Extend ClusterMetrics for additional validation metrics.
- **Downstream Reports**: Use Jinja2 + WeasyPrint for audit‐ready, branded reports.
- **ISO 42001 Traceability**: Generate & validate JSON manifests, capture Git SHA, freeze dependencies.
- **CI/CD Practices**: Lint, type‐check, unit/integration test on every commit.

By following these advanced patterns, you can embed Pascal Zoning ML into enterprise‐grade precision‐agriculture systems, maintain regulatory compliance, and deliver reproducible zonification results at scale.