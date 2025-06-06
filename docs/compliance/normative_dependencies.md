# Normative Dependencies

This document enumerates and justifies the key dependencies (libraries, frameworks, schemas) that **Pascal Zoning ML** relies on to satisfy ISO 42001 requirements. Each dependency is classified (e.g., “mandatory,” “optional,” “test only”), its version pinned in `requirements.txt` or `requirements-dev.txt`, and a rationale provided in the context of ISO 42001 compliance.

---

## 1. Core Python Packages

| Package          | Version Constraint          | Role / Rationale                                                                                                                                                    | ISO 42001 Mapping                                                         |
|------------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `numpy`          | `>=1.24.0,<2.0.0`           | Fundamental array operations (masking, stacking spectral indices, distance computations).                                                                         | Ensures reproducible numerical operations; stable, well‐tested library.   |
| `pandas`         | `>=2.1.0,<3.0.0`            | Tabular data manipulation for zone‐statistics and CSV export.                                                                                                     | Data traceability; CSV outputs meet traceable data format requirements.  |
| `scikit-learn`   | `>=1.3.0,<2.0.0`            | Provides KMeans clustering, PCA (if enabled), and clustering metrics (Silhouette, Calinski–Harabasz).                                                             | Core AI component; must be standard, well‐documented; audit‐ready code.   |
| `matplotlib`     | `>=3.8.0,<4.0.0`            | Visualization: heatmaps (NDVI), cluster maps, bar charts for zone areas, and overview figure.                                                                     | Produces human‐readable outputs; essential for audit and reporting.       |
| `geopandas`      | `>=0.14.0,<1.0.0`           | Vector operations (dissolve zones, compute area, perimeter, export to GeoPackage).                                                                                  | GIS outputs must comply with open standards; ensures traceable geometries. |
| `shapely`        | `>=2.0.2,<3.0.0`            | Geometric computations (polygon union, area, perimeter, point‐in‐polygon).                                                                                         | Ensures accurate spatial calculations; core to zone extraction.           |
| `rasterio`       | `>=1.3.0,<2.0.0`            | Raster I/O: read bands from GeoTIFF, derive field polygon (using shapes), compute affine transform.                                                               | Reliable handling of geospatial rasters; traceable coordinate transforms. |
| `typer`          | `>=0.9.0,<1.0.0`            | CLI development (argument parsing, subcommands).                                                                                                                   | Provides consistent CLI interface; enhances reproducibility of runs.      |
| `loguru`         | `>=0.7.2,<1.0.0`            | Structured, timestamped logging throughout pipeline.                                                                                                               | Facilitates detailed audit trails; meets traceability requirement.        |
| `dataclasses`    | Python standard library     | Structured result and metric classes (`ClusterMetrics`, `ZoneStats`, `ZoningResult`).                                                                               | Promotes type safety and documentation; supports traceability of outputs. |

---

## 2. Testing & Development Dependencies

| Package            | Version Constraint      | Role / Rationale                                                                                                                | ISO 42001 Mapping                                                   |
|--------------------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `pytest`           | `>=8.0.0,<9.0.0`        | Unit and integration testing framework.                                                                                         | Ensures automated testing; quality control requirement.             |
| `pytest-cov`       | `>=4.0.0,<5.0.0`        | Test coverage measurement.                                                                                                      | Demonstrates ≥ 90 % coverage for audit; evidence of QA processes.    |
| `flake8`           | `>=6.0.0,<7.0.0`        | Linting and code style enforcement.                                                                                             | Ensures code quality and maintainability; part of coding standards. |
| `mypy`             | `>=1.7.0,<2.0.0`        | Static type checking.                                                                                                           | Type safety enhances reliability; aids in preventing runtime bugs.  |
| `numpy.typing`     | (built into `numpy`)    | MyPy plugin for better array typing.                                                                                            | Strengthens static analysis for scientific code.                    |
| `black`            | `>=23.0.0,<24.0.0`      | Code formatter.                                                                                                                 | Guarantees consistent code style across team.                        |
| `pre-commit`       | `>=4.0.0,<5.0.0`        | Git pre‐commit hooks (e.g., run `black`, `flake8`, `mypy` before each commit).                                                  | Automates compliance gates; ensures code quality in CI/CD.           |

---

## 3. Security & Schema Validation Dependencies

| Package                   | Version Constraint       | Role / Rationale                                                                                      | ISO 42001 Mapping                                                      |
|---------------------------|--------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `jsonschema`              | `>=4.0.0,<5.0.0`         | Validate manifest and output JSON against defined JSON‐Schema.                                         | Ensures interface consistency; supports traceable configurations.       |
| `check-jsonschema` (CLI)  | (system tool)            | Command‐line schema validation (used in GitHub Actions or manual checks).                              | Automates compliance of manifest.json and schema files.                  |
| `pip-audit` (CLI)         | (system tool)            | Dependency vulnerability scanner.                                                                      | Detect and remediate known CVEs; part of security risk management.       |
| `bandit` (optional)       | `>=1.7.0,<2.0.0`         | Static application security testing for Python code.                                                   | Identifies common security issues; aligns with security controls.        |

---

## 4. Schema Files (JSON Schema)

These JSON Schema files are themselves normative artifacts that formalize how inputs, outputs, and configurations must be structured.

1. **`schemas/manifest.schema.json`**  
   - Validates the pipeline’s manifest (`manifest.json`).  
   - Ensures required fields (name, version, description, interfaces).  
   - Checks correct specification of raster inputs, spectral indices, parameters, and outputs.

2. **`schemas/zoning_output.schema.json`**  
   - Validates the JSON manifest produced at the end of a CLI run.  
   - Ensures presence of version, timestamp, input_image metadata, outputs (geopackage, CSV, JSON, PNG), and metadata fields.  
   - Guarantees that output artifacts conform to expected naming conventions and formats.

3. **`schemas/ndvi_block_output.schema.json`** (included for backwards compatibility if integrating NDVI‐Block outputs)  
   - Validates any NDVI‐Block generated manifest JSON (older block).  
   - Ensures consistency when chaining Pascal Zoning ML behind an NDVI processing block.

> **Note**: All schema files conform to **JSON Schema Draft-07** and are stored under the `schemas/` directory. Automated GitHub Actions use `jsonschema` or `check-jsonschema` to validate any changes to `manifest.json` or pipeline outputs.

---

## 5. Pinned Versions & Reproducibility

- All required dependencies (core + testing) are explicitly pinned in `requirements.txt` and `requirements-dev.txt`.  
- The `pip install -r requirements.txt` command is intended to recreate an identical environment for any user, supporting reproducible pipelines (ISO 42001 clause on reproducibility).  
- The `setup.py` (or `pyproject.toml`) also includes version constraints (e.g., `install_requires` in `setup.py`) to prevent “floating” dependencies that could introduce unexpected changes.

---

## 6. Future Dependency Roadmap

1. **Monitoring & Observability** (Optional)  
   - Consider integrating `prometheus-client` for metric instrumentation (e.g., tracking pipeline runtimes, memory usage) in production deployments.  
   - Rationale: Enhanced operational traceability aligns with ISO 42001’s requirement for monitoring system performance.

2. **Data Provenance** (Optional)  
   - Evaluate adding `prov` (W3C PROV‐O Python library) to generate a detailed provenance document for each run.  
   - Rationale: Supports deeper lineage tracking for field data, algorithms used, and version history—critical in regulated environments.

3. **Advanced Security Scanning** (Optional)  
   - Integrate `Snyk` or `Trivy` in GitHub Actions for container and dependency scanning.  
   - Rationale: Strengthen security posture and meet ISO 42001’s continuous improvement clause for risk management.

---

## 7. Summary

By carefully pinning, documenting, and justifying each dependency—and validating all inputs/outputs via JSON Schema—**Pascal Zoning ML** ensures:

- **Traceable & Reproducible** pipelines (consistent numerical results, versioned artifacts).  
- **Secure & Maintained** dependencies (automated vulnerability scans).  
- **Rigorous Quality Control** (automated tests, code style enforcement, static typing).  

These measures collectively satisfy key ISO 42001 requirements for governance, documentation, quality assurance, security, and continuous improvement.

---

**End of Normative Dependencies Document**  


