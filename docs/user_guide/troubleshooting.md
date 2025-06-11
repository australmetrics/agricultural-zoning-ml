---
title: Troubleshooting
nav_order: 4
-------------

# Troubleshooting

This guide addresses common issues encountered when using **Pascal Zoning ML**. Each section outlines symptoms, potential causes, and step-by-step resolutions.

## Table of Contents

* [Installation Errors](#installation-errors)
* [Configuration Issues](#configuration-issues)
* [Runtime Errors](#runtime-errors)
* [Data Input Issues](#data-input-issues)
* [CLI Usage Problems](#cli-usage-problems)
* [Performance & Resource Issues](#performance--resource-issues)
* [Visualization Issues](#visualization-issues)
* [General Tips](#general-tips)

---

## Installation Errors

### 1. Missing GDAL Headers

**Symptom:** Importing `rasterio` raises `OSError: GDAL not found`.

**Cause:** System GDAL library or development headers are not installed.

**Resolution:**

1. Install GDAL and headers on your OS:

   ```bash
   sudo apt-get update && \
     sudo apt-get install -y gdal-bin libgdal-dev
   ```
2. Recreate virtual environment and reinstall dependencies:

   ```bash
   deactivate && rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

### 2. Incompatible Python Version

**Symptom:** Syntax or import errors referencing `dataclasses` or `typing`.

**Cause:** Running on unsupported Python (<3.11).

**Resolution:**

* Ensure Python 3.11+ is used:

  ```bash
  python --version
  ```
* Use a version manager (`pyenv`, `conda`) to install and switch:

  ```bash
  pyenv install 3.11.2
  pyenv local 3.11.2
  ```

---

## Configuration Issues

### 1. JSON Schema Validation Failure

**Symptom:** `jsonschema.ValidationError` when running with a manifest.

**Cause:** `manifest.json` fields do not match `schemas/manifest.schema.json`.

**Resolution:**

1. Validate locally:

   ```bash
   jsonschema -i path/to/manifest.json schemas/manifest.schema.json
   ```
2. Correct field names or types based on the error message. Refer to the schema docs in `schemas/manifest.schema.json`.

### 2. Incorrect CLI Parameters

**Symptom:** CLI flags unrecognized (e.g., `--max-clusters` vs `--max-zones`).

**Cause:** Outdated or incorrect flag names.

**Resolution:**

* Run:

  ```bash
  pascal-zoning --help
  ```
* Verify the correct flags under the `run` command. Update scripts or documentation accordingly.

---

## Runtime Errors

### 1. No Valid Pixels Found

**Symptom:** Processing aborts with `ProcessingError: No valid pixels found.`

**Cause:** Input raster contains only nodata values or incorrect CRS alignment.

**Resolution:**

1. Inspect raster bounds and CRS:

   ```bash
   gdalinfo path/to/image.tif
   ```
2. Ensure input file uses the same CRS as your study area. Reproject if necessary:

   ```bash
   gdalwarp -t_srs EPSG:4326 input.tif output_reproj.tif
   ```
3. Check nodata threshold and adjust via CLI:

   ```bash
   pascal-zoning --input output_reproj.tif --min-zone-size 0.01
   ```

### 2. Cluster Computation Timeout

**Symptom:** Long delays or timeouts during clustering stage.

**Cause:** Very high resolution or large raster size.

**Resolution:**

* Run in subsets or downsample:

  ```bash
  pascal-zoning --input large.tif --tile-size 1024 --force-k 5
  ```
* Increase available memory or execute on a machine with more resources.

---

## Data Input Issues

### 1. Unsupported File Format

**Symptom:** `GDALOpen` fails on file formats like JPEG.

**Cause:** Only GeoTIFF and standard raster formats supported.

**Resolution:**

* Convert non-supported files to GeoTIFF:

  ```bash
  gdal_translate -of GTiff input.jpg output.tif
  ```

### 2. Missing Spectral Indices

**Symptom:** Error when selecting indices, e.g., `KeyError: 'NDVI'`.

**Cause:** Metadata indices not specified or mismatched.

**Resolution:**

* Use `--indices` flag to explicitly list:

  ```bash
  pascal-zoning --input image.tif --indices NDVI,NDRE,NDWI
  ```

---

## CLI Usage Problems

### 1. Permission Denied

**Symptom:** `PermissionError` saving output files.

**Cause:** Insufficient write permissions on output directory.

**Resolution:**

* Ensure directory exists and is writable:

  ```bash
  mkdir -p output_dir && chmod u+w output_dir
  ```

### 2. Help Text Too Verbose

**Symptom:** CLI help scrolls past too quickly.

**Cause:** Terminal pager not configured.

**Resolution:**

* Pipe help to `less`:

  ```bash
  pascal-zoning --help | less
  ```

---

## Performance & Resource Issues

### 1. High Memory Usage

**Symptom:** Process killed due to OOM.

**Cause:** Large raster size or many indices.

**Resolution:**

* Reduce in-memory data by disabling PCA: `--no-pca`.
* Increase swap or memory allocation.

### 2. Slow IO

**Symptom:** Long load times for large GeoTIFFs.

**Cause:** Disk IO bottleneck.

**Resolution:**

* Use SSD or local scratch space.
* Crop raster to area of interest before processing:

  ```bash
  gdal_translate -projwin xmin ymax xmax ymin input.tif cropped.tif
  ```

---

## Visualization Issues

### 1. Blank or Misaligned Maps

**Symptom:** Maps show no clusters or wrong georeference.

**Cause:** CRS mismatch between raster and vector overlay.

**Resolution:**

* Confirm output GPKG CRS matches input.
* Reproject vector layer:

  ```bash
  ogr2ogr -t_srs EPSG:4326 output_reproj.gpkg output.gpkg
  ```

### 2. Low-Resolution PNGs

**Symptom:** Output images appear blurry.

**Cause:** Default DPI too low.

**Resolution:**

* Increase DPI with `--dpi` flag:

  ```bash
  pascal-zoning --input image.tif --output out --dpi 300
  ```

---

## General Tips

* Always check CLI version: `pascal-zoning --version`.
* Consult example manifests in `examples/` for correct formats.
* Open an issue or discussion if your problem is not covered here.
