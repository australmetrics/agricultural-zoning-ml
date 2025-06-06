# Frequently Asked Questions (FAQ)

This FAQ provides concise answers to common questions about PASCAL Agri-Zoning, with emphasis on alignment to **ISO/IEC 42001:2023**—the AI Management System standard. Wherever applicable, references to ISO 42001 practices are noted.

---

## 1. How does PASCAL Agri-Zoning align with ISO 42001's AI governance requirements?

**Answer:**  
PASCAL Agri-Zoning implements a governance framework that follows core ISO 42001 clauses on AI accountability and oversight. Key points include:

- **Roles & Responsibilities (Clause 5.3):**  
  - The package assumes a designated "AI Manager" role who oversees configuration (`ZoningConfig`), reviews log outputs, and signs off on model outputs before deployment.
  - Logging (via `logging_config.py`) captures audit trails—timestamps, user actions, configuration parameters—aligned to Clause 7.5 (Traceability & Transparency).

- **Policy & Documentation (Clause 5.2):**  
  - Every run produces a versioned `ClusterMetrics` JSON output that includes `project_name`, `project_version`, and `random_state` fields. This ensures that each zoning execution is documented for compliance and reproducibility.
  - A `config.json` schema embeds metadata fields matching ISO 42001 metadata requirements (e.g., "project_name," "ai_manager," "creation_date").

---

## 2. What AI risk-management measures are embedded in the pipeline?

**Answer:**  
Per ISO 42001 Clause 6 (Risk Management), PASCAL incorporates multiple layers of validation and checks to mitigate AI-specific risks:

1. **Data Quality Validation (Clause 6.4):**  
   - The `NDVIBlockInterface` checks that each spectral index array lies within `[-1.0, 1.0]` (`ValidationConfig.spectral_index_range`).  
   - If more than `ValidationConfig.max_nan_ratio` (default 30%) of pixels are invalid (NaN), the pipeline raises a `ProcessingError`, preventing unreliable outputs.

2. **Bias & Representativeness (Clause 6.5):**  
   - A minimum percent of valid pixels (`ValidationConfig.min_valid_pixels_ratio`, default 70%) ensures geographical representativeness.  
   - The selection of sampling points uses a Poisson-disk–like algorithm to avoid spatial clustering bias.

3. **Model Validation (Clause 6.6):**  
   - `AgriculturalZoning.select_optimal_clusters()` computes Silhouette and Calinski-Harabasz scores for k = 2…`max_clusters`. The "best K" is chosen to avoid under- or over-segmentation (mitigating model performance risk).

4. **Continuous Monitoring (Clause 9.2):**  
   - Upon each run, `ClusterMetrics.timestamp` is recorded. Users can track performance drift over time by comparing metric JSON outputs.

---

## 3. How can I demonstrate traceability and auditability for ISO 42001 compliance?

**Answer:**  
Traceability is achieved via:

- **Comprehensive Logging (Clause 7.5):**  
  - Each execution writes a log file (`logs/agri_zoning_<timestamp>.log`) capturing:  
    - User-provided parameters (`index_names`, `force_k`, `min_zone_size`)  
    - Config checksum (SHA256 of the loaded JSON)  
    - Warnings/errors with stack traces  

- **Versioned Configuration Files (Clause 7.4):**  
  - The pipeline accepts a JSON config with `"project_version"` and other metadata. For example:
    ```json
    {
      "project_name": "Cherry_Orchard_Zoning",
      "project_version": "1.2.0",
      "ai_manager": "robinson@example.com",
      "creation_date": "2025-06-10T14:30:00Z",
      "random_state": 42,
      "min_zone_size_ha": 0.5,
      "max_zones": 15,
      "model": {
        "clustering_method": "kmeans",
        "max_clusters": 10
      },
      "validation": {
        "spectral_index_range": [-1.0, 1.0],
        "min_valid_pixels_ratio": 0.7,
        "max_nan_ratio": 0.3
      }
    }
    ```
  - Embedding `creation_date` and `ai_manager` ensures that each run is traceable to a responsible individual and timestamp.

- **Result Artifacts (Clause 8.3 & 8.4):**  
  - GeoPackages (`zonificacion_agricola.gpkg`, `puntos_muestreo.gpkg`) include feature attributes indicating the clustering label and pixel coordinate provenance.
  - `metricas_clustering.json` captures performance metrics. Retaining these artifacts aligns with ISO's requirement to preserve AI decision records.

---

## 4. What privacy and security controls are integrated?

**Answer:**  
Aligned to ISO 42001 Clause 8 (Privacy & Security Controls), PASCAL enforces:

- **Minimal Data Collection:**  
  - Only four spectral indices (NDVI, NDWI, NDRE, SI) are computed and stored. No personally identifiable information (PII) or sensitive farmer data is ever written to logs or outputs.

- **Secure Logging (Clause 8.3):**  
  - Logs do not record file paths outside the project directory.  
  - If running in multi-user environments, file permissions on `logs/` and output directories should be set to prevent unauthorized access (e.g., `chmod 750 logs/`).

- **Configuration Hygiene (Clause 8.4):**  
  - Sensitive fields (e.g., credentials for cloud storage, if used) are **not** stored in plain text. Instead, the pipeline expects environment variables (`AWS_S3_KEY`, `AWS_S3_SECRET`) to be set and references them indirectly.

---

## 5. Where can I find the configuration schema and how is it ISO-aligned?

**Answer:**  
The configuration schema lives in `pascal_zoning/config.py` as three dataclasses: `ZoningConfig`, `ModelConfig`, and `ValidationConfig`. Each field maps to ISO 42001 clauses. A minimal example:

```json
{
  "project_name": "Biobio_Cherries",
  "project_version": "0.9.1",
  "ai_manager": "ai.manager@australmetrics.cl",
  "random_state": 2025,
  "min_zone_size_ha": 0.5,
  "max_zones": 12,
  "min_points_per_zone": 5,
  "model": {
    "clustering_method": "kmeans",
    "max_clusters": 12,
    "random_state": 2025
  },
  "validation": {
    "spectral_index_range": [-1.0, 1.0],
    "min_valid_pixels_ratio": 0.75,
    "max_nan_ratio": 0.25
  },
  "parallel_processing": true,
  "n_jobs": 4,
  "output_formats": ["gpkg", "geojson"],
  "create_visualizations": true,
  "log_level": "INFO"
}
```

Fields like "project_name" and "project_version" address Clause 5.2 (AI Policy and Objectives).

"ai_manager" references the person responsible (Clause 7.1).

Validation thresholds echo Clause 6.4 (Data Quality).

Logging level ("log_level") and parallel processing controls support Clause 9.1 (Operational Controls).

---

## 6. How is model performance evaluated and documented?

**Answer:**  
Aligned to ISO 42001 Clause 6 (Performance Evaluation):

**Automatic K Selection (Clause 6.6):**

The method `select_optimal_clusters()` computes Silhouette and Calinski-Harabasz scores for k = 2…max_clusters. The optimal K is chosen based on maximum silhouette.

**Cluster Metrics Output (Clause 7.5):**

A JSON file `metricas_clustering.json` is created with:

```json
{
  "n_clusters": 5,
  "silhouette": 0.62,
  "calinski_harabasz": 350.5,
  "inertia": 10245.3,
  "cluster_sizes": [1200, 900, 800, 600, 500],
  "timestamp": "2025-06-10T14:32:45Z"
}
```

Storing these metrics alongside timestamps provides an audit trail for performance validation.

**Zone Statistics (Clause 7.4):**

`estadisticas_zonas.csv` contains area, perimeter, compactness, and spectral mean/std for each zone. Continuous monitoring of these statistics over multiple runs can detect dataset drift or model degradation.

---

## 7. What steps ensure data integrity and reproducibility?

**Answer:**  
Per ISO 42001 Clause 7 (Documented Information & Control):

**Version-Controlled Code:**

The repository should tag each release (e.g., v1.0.0) in GitHub.

The `__init__.py` version string is synchronized with Git tags.

**Checksum Verification (Clause 7.3):**

Upon loading a JSON config, the pipeline computes a SHA256 checksum and logs it as `config_checksum`.

Example log line:

```
[INFO] 2025-06-10 14:30:00 | Loaded config.json (SHA256: 3f2e47ab9c1d...)
```

**Seeded Randomness (Clause 7.1):**

All randomness (cluster initialization, sampling point selection) uses a single `random_state` seed defined in the config to guarantee reproducibility.

**Result Packaging (Clause 8.5):**

Each run exports a zipped archive (`<project_name>_<timestamp>.zip`) containing:

- `zonificacion_agricola.gpkg`
- `puntos_muestreo.gpkg`
- `estadisticas_zonas.csv`
- `metricas_clustering.json`
- All log files generated under `logs/`

---

## 8. Can I customize or extend the pipeline while remaining ISO 42001-compliant?

**Answer:**  
Yes. Key extension points:

**Custom Clustering (Clause 6.6):**

The `model.clustering_method` parameter can accept "kmeans," "agglomerative," or a user-supplied scikit-learn estimator that implements `fit_predict(X)`.

When you plug in a custom estimator, update the config to include `"custom_model": "sklearn.cluster.DBSCAN"` and supply parameters like `eps` and `min_samples`. Maintain metadata about this custom model in the config for traceability.

**Alternate Validation Rules (Clause 6.4):**

You can override `ValidationConfig` thresholds. For example, if using an image with higher noise, set:

```json
"validation": {
  "spectral_index_range": [-0.8, 0.8],
  "min_valid_pixels_ratio": 0.6,
  "max_nan_ratio": 0.4
}
```

Document these changes in the config's `change_log` field to comply with documented information control (Clause 7.2).

**Integration with Downstream Systems (Clause 8.2):**

If you integrate PASCAL outputs into an ERP or farm-management system, ensure API calls to external services are secured (HTTPS only) and that access controls (OAuth tokens) are stored in environment variables, not hardcoded.

---

## 9. How do I handle updates and continuous improvement per ISO 42001?

**Answer:**  
ISO 42001 Clause 9 (Monitoring, Measurement, Analysis & Improvement) recommends a Plan-Do-Check-Act (PDCA) cycle:

**Monitor:**

After each run, collect metrics from `metricas_clustering.json`.

Use a simple script to aggregate silhouette over time:

```python
import json, glob
metrics_files = glob.glob("outputs/*/metricas_clustering.json")
for f in metrics_files:
    data = json.load(open(f))
    print(f"{data['timestamp']}: silhouette = {data['silhouette']}")
```

**Analyze:**

Plot trends (e.g., silhouette vs. date) using matplotlib or business intelligence tools.

Look for downward trends indicating model drift.

**Improve:**

If performance degrades, update:

- `max_zones` range
- Preprocessing steps (e.g., apply histogram equalization in `NDVIBlockInterface`)
- Parameterize new spectral indices (e.g., adding SAVI or EVI)

**Document:**

Record each improvement in a `changelog.md` alongside version tags.

Example changelog entry:

```markdown
## v1.1.0 (2025-07-01)
- Added Savitzky–Golay smoothing in spectral preprocessing (Clause 6.4).
- Updated clustering method to use DBSCAN for small vineyards (Clause 6.6).
- Enhanced logging detail to include `memory_usage` metrics (Clause 9.3).
```

---

## 10. How do I report non-conformance or file an issue?

**Answer:**  
Following ISO 42001 Clause 10 (Nonconformity & Corrective Action):

**Identify Nonconformance:**

If you detect unexpected patterns (e.g., zones not matching known field boundaries), treat it as a nonconformance.

Record the issue in an internal log:

```bash
echo "Nonconformance: Unexpected zone shape on 2025-06-10" >> nonconformance.log
```

**Corrective Action:**

Re-run the pipeline with debug logging (`"log_level": "DEBUG"`) to gather more information.

Compare GeoPackage zone polygons against ground truth in GIS (Clause 9.2).

**Preventive Action:**

Adjust validation thresholds or introduce additional data checks in `interface.py` to catch edge cases earlier.

**Issue Reporting:**

Open a GitHub issue:

**Title:** "Nonconformance: Zone polygons do not match field boundary for Raster X"

**Include:**

- Full stack trace from log
- Sample raster and expected output polygons
- Config JSON used

---

## 11. What is the recommended way to integrate PASCAL into a larger ISO 42001–compliant AI ecosystem?

**Answer:**  
Integrating PASCAL into a broader AI Management System (ISO 42001 Clause 4) involves:

**Aligning Organization's AI Policy (Clause 4.2):**

Ensure that PASCAL's objectives (e.g., "improve yield predictions through zoning") match your organization's AI policy.

**Mapping Processes (Clause 4.3):**

Define how data flows from satellite ingestion → spectral index computation → clustering → GIS ingestion. Document each step in a flowchart (e.g., BPMN diagram) and assign process owners.

**Internal Audits (Clause 9.5):**

Periodically audit PASCAL configurations, logs, and outputs.

Check that `ai_manager` email remains current, and that obsolete configuration files are archived (per Documented Information Control).

**Training & Competency (Clause 7.1):**

Ensure personnel running PASCAL have:

- Basic GIS knowledge (QGIS, coordinate reference systems)
- Understanding of KMeans clustering and spectral indices
- Awareness of ISO 42001 requirements for data quality and privacy

---

## 12. Where can I find additional resources on ISO 42001 and best practices?

**Answer:**

**Official ISO/IEC 42001:2023 Standard Document**

Purchase or access via your institutional library to read full clauses and requirements.

**ISO Guidance Material (ISO 42001 Guidance Annex):**

Contains explanatory material on implementing AI management systems, including templates for risk assessment and audit checklists.

**AI Ethics & Governance Whitepapers:**

Many organizations publish guidelines for aligning AI solutions to ISO 42001.

For example, the "AI Governance Framework" by the Open Data Institute (ODI) offers practical templates that can be adapted for PASCAL.

**Open-Source Audit Tools:**

Tools like IBM AI Fairness 360 and Google's What-If Tool can be used alongside PASCAL to validate clustering fairness and distribution (useful for Clause 6.5 bias mitigation).