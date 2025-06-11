# Changelog

This document is based on the **Keep a Changelog** format and adheres to [Semantic Versioning](https://semver.org/), using tags like `vMAJOR.MINOR.PATCH` (e.g., `v1.0.0` for major releases, `v1.1.0` for new features, `v1.0.1` for bug fixes), clarifying the format for new contributors.

## \[1.0.2] - 2025-06-10

> Focuses on documentation consolidation and ISO 42001 alignment.

* Documentation consolidated for brevity and ISO 42001 traceability.
* Links in `README.md`, `CONTRIBUTING.md`, and other markdown files updated accordingly.
* Version bumped to `v1.0.2`.

## \[1.0.1] - 2025-06-05

> Bugfix release addressing packaging schema issue.

* Fixed JSON schema error in `manifest.json` that caused release artifacts to fail (see [#42](https://github.com/australmetrics/agricultural-zoning-ml/issues/42)).
* Re-ran `release-on-tag` workflow to regenerate the GitHub release.

## \[1.0.0] - 2025-05-30

> Initial public release introducing the core zoning pipeline.

* Initial public release of **Pascal Zoning**: end-to-end zoning pipeline with mask creation, clustering, and optimized sampling outputs (see [README.md](README.md) for full feature set and [API documentation](docs/api.md)).
* Provides both CLI and Python API for seamless integration into data workflows.

