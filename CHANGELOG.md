# Changelog

All notable changes to this project will be documented in this file.

The format is based on [“Keep a Changelog”](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- (Pending planned features, enhancements, or bug fixes before the next release.)

---

## [0.1.0] - 2025-06-05
### Added
- Initial public release of **Pascal Zoning (Agricultural Zoning ML)**.
  - Core clustering pipeline (`AgriculturalZoning` class) for generating management zones and sampling points.
  - CLI (`pascal_zoning.pipeline`) with `run` command:
    - `--raster`, `--indices`, `--output-dir`, `--force-k`, `--min-zone-size`, `--max-zones`, `--use-pca`.
  - Python API methods:
    - `create_mask()`
    - `prepare_feature_matrix()`
    - `perform_clustering()`
    - `extract_zone_polygons()`
    - `filter_small_zones()`
    - `generate_sampling_points()`
    - `compute_zone_statistics()`
    - `save_results()`
    - `visualize_results()`
  - Dataclasses:
    - `ClusterMetrics`
    - `ZoneStats`
    - `ZoningResult`
  - Integrated visualization routines (`viz.zoning_overview`).
  - Export formats:
    - GeoPackage: `zonificacion_agricola.gpkg`, `puntos_muestreo.gpkg`
    - CSV: `estadisticas_zonas.csv`
    - JSON: `metricas_clustering.json`
    - PNG: `mapa_ndvi.png`, `mapa_clusters.png`, `zonificacion_results.png`
  - Example usage documented in `README.md`.
  - Automated tests:
    - Unit tests for core API (`tests/unit/test_zoning_core.py`).
    - Unit tests for visualization (`tests/unit/test_viz.py`).
    - Integration workflow tests (`tests/integration/test_workflow.py`).
  - ISO 42001 compliance:
    - Detailed logging with timestamps.
    - Dependency documentation via `requirements.txt` and `requirements-dev.txt`.
    - Test suite ensures reproducibility and quality control.

### Changed
- Project renamed to **pascal-zoning-ml** to reflect alignment with existing “pascal-ndvi-block” ecosystem.
- Package metadata updated to `0.1.0-alpha` in `pyproject.toml`.

### Fixed
- Adjusted test fixtures to use uppercase index keys (`"NDVI"`, `"NDRE"`, etc.).
- Updated CLI integration test to use correct parameter names (`--max-clusters` → `--max-zones`, `--min-area-ha` → `--min-zone-size`).
- Ensured all unit tests pass on Python 3.11.

---

## [0.1.0-alpha] - 2025-05-15
### Added
- Initial alpha release (pre–public version) with basic clustering pipeline:
  - `AgriculturalZoning` class skeleton with placeholder methods for:
    - Mask creation
    - Feature preprocessing
    - Clustering
    - Polygon extraction
    - Sampling and statistics
    - Result export
- Preliminary CLI script (`zoning.py`) using `argparse`:
  - Accepts `--raster`, `--output`, `--max_clusters`, `--min_area_ha`, `--force_k`.
  - Builds footprint polygon from TIFF via `rasterio.features.shapes`.
  - Integrates spectral index calculation (`NDVI`, `NDWI`, `NDRE`, `SI`).
- Basic logging setup with Loguru.
- Prototype of visualization functions in `viz.py`.
- Early unit tests for CLI help and minimal function stubs.

---

## [0.1.0-beta] - 2025-05-25
### Added
- Switched CLI framework to **Typer** for improved argument parsing and help text:
  - Refactored `pascal_zoning.pipeline` module.
  - Commands: `run`.
  - CLI options changed to `--raster`, `--indices`, `--output-dir`, `--force-k`, `--min-zone-size`, `--max-zones`, `--use-pca`.
- Completed implementation of:
  - `create_mask()` with GeoPandas mask and NaN filtering.
  - `prepare_feature_matrix()` with `SimpleImputer`, `StandardScaler`, optional `PCA`.
  - `select_optimal_clusters()` and `perform_clustering()`.
  - `extract_zone_polygons()` and `filter_small_zones()`.
  - `generate_sampling_points()` using spatial inhibition algorithm.
  - `compute_zone_statistics()` for area, perimeter, compactness, and index stats.
  - `save_results()` exporting to GeoPackage, CSV, and JSON.
  - `visualize_results()` for NDVI and cluster maps.
- Added comprehensive unit tests for each internal method:
  - `test_preprocess_features`, `test_create_zone_polygons`, `test_generate_samples`, etc.
- Integrated `pytest.ini` to filter deprecation warnings (Shapely’s `unary_union`).
- Created integration test for end-to-end CLI workflow:
  - Uses a synthetic 6-band 2×2 TIFF to validate output files.
- Documentation updates in `README.md` to reflect new CLI and API usage.
- Example `config.yaml` support defined (no code-level enforcement yet).

### Changed
- Renamed internal helper methods (`_preprocess_features` → `prepare_feature_matrix`, etc.) for a public API approach.
- Modified data class fields to standardize naming (`cluster` → `zone_id` in returned GeoDataFrame).
- Updated visualization logic to use `zoning_overview` from `viz.py` rather than inline plotting.
- Refined `CHANGELOG.md` layout to follow “Keep a Changelog” conventions.

### Fixed
- Resolved early bugs in spatial inhibition logic for sampling points (avoided infinite loops).
- Corrected file naming inconsistencies (e.g., `metricas_clustering.json` vs. `metrics_zoning.json`).
- Handled edge case where all pixels fall outside polygon (Raised `ProcessingError`).
- Adjusted test timeouts and working directory in integration tests for Windows compatibility.

---

## [0.1.0-alpha1] - 2025-05-01
### Added
- Project scaffolding:
  - `src/pascal_zoning/` directory created.
  - Basic package structure with `__init__.py`, `zoning.py`, `viz.py`.
  - `pyproject.toml` and `setup.cfg` defining package metadata.
  - Preliminary `CHANGELOG.md` entry placeholder.
- Installed initial dependencies:
  - `numpy`, `geopandas`, `rasterio`, `scikit-learn`, `matplotlib`, `loguru`, `typer`.
- Created initial unit test files with empty test stubs.

### Changed
- None.

### Fixed
- None.

---

**Note**: Future release versions should replace `[Unreleased]` with the upcoming version number and date, and new changes appended under that section.  

