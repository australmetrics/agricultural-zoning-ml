---
title: FAQ
nav_order: 5
-------------

# Frequently Asked Questions (FAQ)

This FAQ provides concise answers to common questions about **Pascal Zoning ML**, emphasizing ISO/IEC 42001:2023 alignment and best practices.

## Table of Contents

1. [General](#general)
2. [ISO 42001 Compliance](#iso-42001-compliance)
3. [Pipeline Usage](#pipeline-usage)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Contribution & Support](#contribution--support)

---

## General

**Q1: What is Pascal Zoning ML?**
A: An AI-driven library for generating agricultural management zones and sampling points from spectral-index data, compliant with ISO 42001 traceability and auditability requirements.

**Q2: Where can I find the source code and documentation?**
A: Visit our [GitHub repository](https://github.com/australmetrics/agricultural-zoning-ml) and the full docs at `docs/` in the repo.

**Q3: Which platforms and environments are supported?**
A: Linux, macOS, Windows with Python 3.11+. GDAL 3.6+ and a C compiler are required. Docker image is also available.

---

## ISO 42001 Compliance

**Q4: How does Pascal Zoning ML ensure ISO 42001 traceability?**
A: Through versioned config files (`project_version`), comprehensive logs (`logs/*.log`), and version tags (`vMAJOR.MINOR.PATCH`) documented in `CHANGELOG.md`.

**Q5: What privacy and security measures does the library enforce?**
A: Minimal data collection (only spectral indices), secure environment variable handling for credentials, and CI-based vulnerability scans (`pip-audit`, `bandit`).

---

## Pipeline Usage

**Q6: How do I run the full zoning pipeline?**
A: See the [Quick Start](quick_start.md) guide for CLI and Python API examples.

**Q7: Can I customize clustering and validation thresholds?**
A: Yes. Use CLI flags (`--force-k`, `--min-zone-size`, `--use-pca`) or adjust `ZoningConfig` and `ValidationConfig` in your JSON config.

**Q8: How do I integrate custom models?**
A: Supply a scikit‑learn estimator implementing `fit_predict(X)` via the `model.clustering_method` config field and include its module path.

---

## Configuration

**Q9: Where is the config schema defined?**
A: In `pascal_zoning/config.py` as dataclasses (`ZoningConfig`, `ModelConfig`, `ValidationConfig`). Example schema in `schemas/manifest.schema.json`.

**Q10: How do I validate my manifest file?**
A: Run:

```bash
jsonschema -i manifest.json schemas/manifest.schema.json
```

---

## Troubleshooting

**Q11: I get "No valid pixels found." What should I do?**
A: Check your input raster's CRS and nodata values. Reproject or filter data, and adjust `--min-zone-size` if needed.

**Q12: CLI flags not recognized?**
A: Ensure you’re using the latest version (`pascal-zoning --version`) and consult `pascal-zoning zoning --help` for updated flag names.

---

## Contribution & Support

**Q13: How can I contribute?**
A: Follow our [Contributing Guide](contributing.md): fork, branch, test, and open a PR. Ensure CI passes and include test updates.

**Q14: Where can I get help or report issues?**
A: Open a GitHub issue labeled `bug` or `question`, or join our [Discussions](https://github.com/australmetrics/agricultural-zoning-ml/discussions).

**Q15: How are releases versioned?**
A: Semantic Versioning (`vMAJOR.MINOR.PATCH`), with release notes in `CHANGELOG.md` and automated via GitHub Actions workflow on tag push.

---

*Last updated: 2025-06-10 v1.0.2*
