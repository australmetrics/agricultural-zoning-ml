# Normative Dependencies

> **Executive Summary**: This document lists and justifies the core, testing, and security dependencies of **Pascal Zoning ML**, detailing each package’s role, version constraints, classification (mandatory, optional, test-only), and alignment with ISO 42001 requirements. Pinning versions in `requirements.txt` and validating schemas ensures reproducible, auditable, and secure AI workflows.

## Table of Contents

1. [Core Python Packages](#core-python-packages)
2. [Testing & Development Packages](#testing--development-packages)
3. [Security & Schema Validation](#security--schema-validation)
4. [JSON Schema Artifacts](#json-schema-artifacts)
5. [Pinning & Reproducibility](#pinning--reproducibility)
6. [Future Roadmap](#future-roadmap)

---

## Core Python Packages

| Package        | Version Constraint | Classification | Role & ISO 42001 Rationale                                                                       |
| -------------- | ------------------ | -------------- | ------------------------------------------------------------------------------------------------ |
| `numpy`        | `>=1.24.0,<2.0.0`  | Mandatory      | Array ops for masks, spectral stacking; ensures numerical consistency and reproducibility.       |
| `pandas`       | `>=2.1.0,<3.0.0`   | Mandatory      | Tabular data handling for zone metrics and CSV export; satisfies data traceability requirements. |
| `scikit-learn` | `>=1.3.0,<2.0.0`   | Mandatory      | Clustering, PCA, and metrics; provides audit-ready, well-documented algorithms.                  |
| `matplotlib`   | `>=3.8.0,<4.0.0`   | Mandatory      | Generates visual reports (maps, charts) essential for audit and stakeholder communication.       |
| `geopandas`    | `>=0.14.0,<1.0.0`  | Mandatory      | Spatial vector operations (dissolve, export); ensures GIS outputs follow open standards.         |
| `shapely`      | `>=2.0.2,<3.0.0`   | Mandatory      | Accurate geometric computations for zone extraction; core to spatial integrity.                  |
| `rasterio`     | `>=1.3.0,<2.0.0`   | Mandatory      | GeoTIFF I/O and affine transforms; enables traceable coordinate handling.                        |
| `typer`        | `>=0.9.0,<1.0.0`   | Mandatory      | CLI parsing; guarantees consistent, reproducible command-line runs.                              |
| `loguru`       | `>=0.7.2,<1.0.0`   | Mandatory      | Structured logging; fulfills detailed audit trail requirements.                                  |
| `dataclasses`  | Python stdlib      | Mandatory      | Structured result classes; supports traceability and type safety.                                |

## Testing & Development Packages

| Package      | Version Constraint | Classification | Role & ISO 42001 Rationale                                                   |
| ------------ | ------------------ | -------------- | ---------------------------------------------------------------------------- |
| `pytest`     | `>=8.0.0,<9.0.0`   | Test-only      | Unit/integration tests; mandatory for QA and reproducibility evidence.       |
| `pytest-cov` | `>=4.0.0,<5.0.0`   | Test-only      | Coverage measurement; ensures ≥90 % code coverage for audit readiness.       |
| `flake8`     | `>=6.0.0,<7.0.0`   | Dev-only       | Linting and style enforcement; upholds code quality standards.               |
| `mypy`       | `>=1.7.0,<2.0.0`   | Dev-only       | Static type checking; prevents runtime errors, boosting reliability.         |
| `black`      | `>=23.0.0,<24.0.0` | Dev-only       | Code formatter; ensures consistent code style across contributors.           |
| `isort`      | Latest             | Dev-only       | Imports sorting; maintains import order consistency.                         |
| `pre-commit` | `>=4.0.0,<5.0.0`   | Dev-only       | Git hooks for lint, format, type-check before commits; automates compliance. |

## Security & Schema Validation

| Package            | Version Constraint | Classification | Role & ISO 42001 Rationale                                               |
| ------------------ | ------------------ | -------------- | ------------------------------------------------------------------------ |
| `jsonschema`       | `>=4.0.0,<5.0.0`   | Mandatory      | Validates `manifest.json` and output JSON; enforces config consistency.  |
| `check-jsonschema` | System tool        | Dev-only       | CLI schema checks in GitHub Actions; automates compliance validation.    |
| `pip-audit`        | System tool        | Dev-only       | Scans for vulnerable dependencies; integral to security risk management. |
| `bandit`           | `>=1.7.0,<2.0.0`   | Optional       | Static security analysis; identifies common code security issues.        |

## JSON Schema Artifacts

* `schemas/manifest.schema.json`: validates pipeline manifest fields (name, version, interfaces).
* `schemas/zoning_output.schema.json`: validates run outputs (version, timestamp, input metadata, geo/CSV/JSON/PNG artifacts).
* `schemas/ndvi_block_output.schema.json`: supports legacy NDVI-Block integration.

> **Note**: All schemas conform to **JSON Schema Draft-07** and are automatically checked in CI via `jsonschema` or `check-jsonschema`.

## Pinning & Reproducibility

* **Pin versions** in `requirements.txt`/`requirements-dev.txt` to recreate identical environments.
* **`setup.py`/`pyproject.toml`** also enforce version bounds.
* Supports ISO 42001 clause on reproducible AI processes.

## Future Roadmap

1. **Metrics & Monitoring**: integrate `prometheus-client` for runtime metrics; enhances operational traceability.
2. **Data Provenance**: explore `prov` library for detailed lineage documentation.
3. **Advanced Scanning**: add `Trivy` or `Snyk` for container and dependency security checks.

*End of Normative Dependencies Document*
  


