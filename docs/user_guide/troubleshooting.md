# Troubleshooting Guide

If you encounter issues when installing or running PASCAL Agri-Zoning, this guide offers common error messages, likely causes, and suggested solutions.

---

## 1. Import / Installation Errors

### 1.1. `ModuleNotFoundError: No module named 'rasterio'`
- **Cause:** The `rasterio` dependency is not installed or its GDAL backend is missing.  
- **Solution:**  
  1. Ensure GDAL is installed on your system.  
     - Ubuntu: `sudo apt-get install gdal-bin libgdal-dev`  
     - macOS: `brew install gdal`  
  2. Reinstall `rasterio` in your environment:  
     ```bash
     pip install rasterio
     ```
  3. Verify `import rasterio` in a Python REPL:  
     ```python
     >>> import rasterio
     >>> print(rasterio.__version__)
     ```

---

### 1.2. `ModuleNotFoundError: No module named 'geopandas'` or `ImportError: GDAL version x.x.x is required`
- **Cause:** `geopandas` (and its dependencies) are missing or have mismatched GDAL versions.  
- **Solution:**  
  1. Install system GDAL (matching version) first.  
  2. Reinstall `geopandas`:  
     ```bash
     pip install geopandas
     ```
  3. If using `conda`, it can manage dependencies automatically:  
     ```bash
     conda install -c conda-forge geopandas
     ```

---

## 2. Runtime Errors in Zoning Pipeline

### 2.1. `ZonificationError: Bounds not initialized` or similar
- **Cause:** The pipeline expects a valid polygon bounding geometry (`bounds`) to be set before creating a mask.  
- **Solution:**  
  - Ensure your input TIFF is not entirely zeros (no-data).  
  - The code extracts the field polygon by reading the first band (`banda1 > 0`). If your TIFF's "inside‐field" pixels are exactly zero, adjust the threshold or mask generation logic.  
  - Confirm the TIFF has valid pixel values where the field exists (values > 0). You can inspect with:  
    ```bash
    gdalinfo -stats inputs/my_field_multiband.tif
    ```

---

### 2.2. `ProcessingError: No valid pixels found inside polygon`
- **Cause:**  
  1. The field polygon might be empty or poorly extracted.  
  2. All spectral index arrays are NaN under the field area (e.g., the TIFF contains no valid data for the requested bands).  
- **Solution:**  
  - Check that `indices` (NDVI, NDWI, etc.) contain valid (non-NaN) values.  
    ```python
    # Quick check in Python
    from pascal_zoning.interface import NDVIBlockInterface
    import numpy as np

    block = NDVIBlockInterface(data_path="inputs")
    indices = block.load_spectral_indices(Path("inputs"), ["ndvi", "ndwi"])
    for name, arr in indices.items():
        print(name, np.count_nonzero(~np.isnan(arr)), "valid pixels")
    ```
  - If fewer than `min_valid_pixels_ratio * total_pixels`, the pipeline will warn or raise an error (depending on your config).  
  - Confirm that `bounds` geometry overlaps the raster: use tools like `gdal_polygonize.py` or QGIS to visualize.

---

### 2.3. `ValueError: Shapes of spectral indices are inconsistent`
- **Cause:** The four requested index arrays (NDVI, NDWI, etc.) do not share the exact same dimensions.  
- **Solution:**  
  - Verify that your GeoTIFF bands all have identical width/height.  
  - If you generated each band separately, ensure they were resampled or clipped in a consistent manner.  
  - In Python:  
    ```python
    for name, arr in indices.items():
        print(name, arr.shape)
    ```
  - All shapes must match (e.g., `(1024, 1024)`).

---

### 2.4. `ValueError: Invalid indices: ['something']` (from `_load_indices`)
- **Cause:** You passed an unsupported index name to `--indices` or `index_names` (case‐sensitive).  
- **Solution:** Use only valid indices: `ndvi`, `ndwi`, `ndre`, or `si`. Example:  
  ```bash
  pascal-zoning run --indices ndvi,ndwi
  ```

---

## 3. Clustering and Zone Generation

### 3.1. `ProcessingError: cluster_labels not initialized` or `dimensions not initialized`
- **Cause:** The code attempted to perform clustering before preparing the feature matrix or setting up dimensions (height, width).
- **Solution:**
  - Confirm that you invoked `run_pipeline()` or `ZoningPipeline.run()` in the correct order.
  - Internally, `run_pipeline()` does:
    1. `create_mask()`
    2. `prepare_feature_matrix()`
    3. `perform_clustering()`
    4. `extract_zone_polygons()`
    5. `filter_small_zones()`
    6. `compute_zone_statistics()`
    7. `generate_sampling_points()`
  - Do not call `perform_clustering()` manually before `prepare_feature_matrix()`. Always use the high‐level `run_pipeline()` or `ZoningPipeline.run()`.

---

### 3.2. `ProcessingError: No zone polygons generated (no labeled pixels)`
- **Cause:**
  - After clustering, all pixels were assigned -1 (unassigned), so no zone polygons can be formed.
  - Possible if `valid_mask` is empty, or K selection produced too many clusters and filtered them all out.
- **Solution:**
  - Check that `valid_mask` contains True values.
  - If you forced a very large `force_k` (e.g., more clusters than valid pixels), reduce it.
  - Try a smaller `max_zones` or do not force K at all.

---

### 3.3. `ProcessingError: No sampling points generated`
- **Cause:** The inhibition sampling routine could not find any pixels in a zone (e.g., zone is too small or all pixels were filtered).
- **Solution:**
  - Ensure `points_per_zone` (default: 5) is not greater than the number of valid pixels in each zone.
  - You can reduce `min_points_per_zone` in your `ZoningConfig` or pass a smaller `points_per_zone` to the `run()` method.
  - Inspect the zone geometries in a GIS tool to confirm they cover at least `points_per_zone` pixels.

---

## 4. Configuration & Logging Issues

### 4.1. `ValueError: max_clusters must be >= 2`
- **Cause:** In your configuration JSON or code, `model.max_clusters` is set to less than 2.
- **Solution:**
  - Edit your config (`my_config.json`) to use `max_clusters: 2` or greater.
  - Example snippet:
    ```json
    "model": {
      "clustering_method": "kmeans",
      "max_clusters": 5,
      "random_state": 42
    }
    ```

---

### 4.2. Logging not appearing in `logs/`
- **Cause:** Either `setup_logging()` was not called, or you pointed `output_dir` to a non‐writable location.
- **Solution:**
  - Confirm that the pipeline was run with a valid `output_dir` (e.g., a directory you have write permission for).
  - Inside your Python code, before `run_pipeline()` or `ZoningPipeline.run()`, ensure `output_dir` is passed correctly.
  - After execution, you should see a `logs/` subfolder with a file `agri_zoning_<timestamp>.log`. If not, check file permissions.

---

## 5. Visualization Issues

### 5.1. Blank or partially blank `mapa_ndvi.png` / `mapa_clusters.png`
- **Cause:**
  - If the NDVI index was not requested or computed, `visualize_results()` skips generating the NDVI map (and issues a warning).
  - If `zones_gdf` or `samples_gdf` is empty, the cluster map may be blank.
- **Solution:**
  - Confirm you requested `ndvi` in the `--indices` list.
  - Check logs: if you see `Warning: No NDVI found`, include "ndvi" in your indices.
  - Make sure `run_pipeline()` completed successfully and produced non-empty zones and samples.

---

## 6. Unexpected Exceptions

If you encounter any other exceptions, consider the following steps:

### Enable Debug Logging:
In your `ZoningConfig`, set `"log_level": "DEBUG"` and rerun. Examine the detailed log in `logs/`.

### Inspect Input Data:
- Confirm your TIFF's band order and data type (must be float32 or convertible).
- Use a GIS tool to verify the raster's bounds and pixel values.

### Run a Minimal Test:
```python
from pascal_zoning.interface import NDVIBlockInterface
from pascal_zoning.pipeline import ZoningPipeline

# 1) Check spectral indices
block = NDVIBlockInterface(data_path="inputs")
indices = block.load_spectral_indices(Path("inputs"), ["ndvi"])
print("NDVI stats:", float(indices["ndvi"].min()), float(indices["ndvi"].max()))

# 2) Run pipeline with only NDVI
pipeline = ZoningPipeline()
pipeline.run(raster_path=Path("inputs/my_field_multiband.tif"),
             index_names=["ndvi"],
             output_dir=Path("outputs_test"))
```

### Raise an Issue / Contact Support:
If none of the above resolves your problem, please open a GitHub issue in the pascal-zoning repository with:
- A description of the error's full stack trace.
- A small sample dataset (if possible) to reproduce the issue.
- Your environment (OS, Python version, GDAL version, library versions).

**Reminder:** Always check that your input data (TIFF, polygon extraction) is valid and that any custom configuration JSON matches the schema defined in `pascal_zoning/config.py`.