# Advanced Examples

© 2025 AustralMetrics SpA. All rights reserved.

This document provides advanced usage examples for PASCAL NDVI Block, designed for power users, researchers, and organizations requiring complex remote sensing workflows with full ISO 42001 compliance.

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

---

These advanced examples demonstrate the full capabilities of PASCAL NDVI Block for enterprise-level remote sensing workflows, maintaining strict ISO 42001 compliance throughout all operations with comprehensive audit trails, quality control, and integration capabilities.