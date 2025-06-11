# Agricultural Zoning ML — Deployment Guide

**Version:** 1.0.2
**Release Date:** June 2025
**ISO 42001 Compliance:** AI Management System Standard
**Organization:** AustralMetrics SpA

## Table of Contents

1. [Version Information](#version-information)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Quick Start Guide](#quick-start-guide)
4. [System Requirements](#system-requirements)
5. [Production Deployment](#production-deployment)

   * [Step 1: Environment Setup](#step-1-environment-setup)
   * [Step 2: Python Environment](#step-2-python-environment)
   * [Step 3: Configuration](#step-3-configuration)
   * [Step 4: Directory Structure](#step-4-directory-structure)
   * [Step 5: System Validation](#step-5-system-validation)
6. [Security & ISO 42001 Compliance](#security--iso-42001-compliance)
7. [Monitoring & Health Checks](#monitoring--health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Deployment Checklist](#deployment-checklist)
10. [Change Management](#change-management)
11. [Support & Maintenance](#support--maintenance)

---

## Version Information

| Version | Date     | Changes                                    | Compliance  |
| ------- | -------- | ------------------------------------------ | ----------- |
| 1.0.2   | Jun 2025 | Production deployment, ISO 42001 alignment | ✓ Compliant |
| 1.0.1   | May 2025 | Core functionality implementation          | Partial     |
| 1.0.0   | Apr 2025 | Initial release                            | Development |

---

## GitHub Repository Setup

Before deploying, ensure your GitHub repository is correctly configured:

* **Clone & Branching**: Fork and clone the `australmetrics/agricultural-zoning-ml` repo. Use feature branches named `feature/<description>` and protection rules on `main` and `develop` branches.
* **Release Tags**: Follow semantic versioning (`v1.0.2`). Create annotated Git tags (`git tag -a v1.0.2 -m "Release 1.0.2"`) and push with `git push origin --tags`.
* **CI/CD (GitHub Actions)**: Enable workflows in `.github/workflows/`:

  * **Lint & Tests**: Run `flake8`, `mypy`, and unit tests on PRs.
  * **Security Scans**: Use Dependabot and CodeQL for dependency and code vulnerability checks.
  * **Deployment**: Automate production deployment steps via a `deploy.yml` action.
* **Branch Protection**: Require status checks (build, tests, coverage) before merging into `main`.
* **Code Owners & Reviews**: Define `CODEOWNERS` to enforce peer review on critical files.
* **Wiki & Pages**: Host docs in GitHub Pages under `/docs` folder, auto-build with GitHub Actions.

---

## Quick Start Guide

```bash
# 1. Clone and setup
git clone https://github.com/australmetrics/agricultural-zoning-ml.git
cd agricultural-zoning-ml

# 2. Create environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your settings

# 5. Create directories
mkdir -p data results logs audit

# 6. Validate installation
python -m src.pascal_zoning.pipeline --version
python -m src.pascal_zoning.pipeline --validate-system
```

---

## System Requirements

### Minimum Requirements

* **OS**: Ubuntu 20.04+, Windows 10+, macOS 12+
* **Python**: 3.11+
* **RAM**: 8 GB (16 GB recommended)
* **Storage**: 10 GB free space (SSD preferred)
* **CPU**: 4+ cores
* **Network**: Internet access for dependencies

### Dependencies

```plaintext
numpy>=1.24.0
pandas>=2.0.0
geopandas>=0.14.0
rasterio>=1.3.8
scikit-learn>=1.3.0
```

### System Libraries

* GDAL 3.6.2+
* PROJ 9.0.0+
* GEOS 3.11.0+

---

## Production Deployment

### Step 1: Environment Setup

```bash
# Create application directory
sudo mkdir -p /opt/agricultural-zoning-ml
sudo useradd -m -s /bin/bash agri_zoning
sudo chown agri_zoning:agri_zoning /opt/agricultural-zoning-ml

# Clone repository
git clone https://github.com/australmetrics/agricultural-zoning-ml.git /opt/agricultural-zoning-ml
cd /opt/agricultural-zoning-ml
```

### Step 2: Python Environment

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -m src.pascal_zoning.pipeline --help
```

### Step 3: Configuration

```bash
cp .env.example .env
```

**Required **\`\`** Settings:**

```bash
ORGANIZATION=AustralMetrics_SpA
DEPLOYMENT_VERSION=1.0.2
AUDIT_LOGGING=true
DATA_RETENTION_DAYS=2555
USERNAME=production_user
DEPLOYMENT_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=structured
AUDIT_LOG_PATH=audit/
DEFAULT_OUTPUT_DIR=results
TEMP_DIR=/tmp/agri_zoning
MAX_MEMORY_MB=8192
MODEL_VALIDATION=strict
ENCRYPT_OUTPUT=true
SECURE_TEMP_FILES=true
```

### Step 4: Directory Structure

```bash
mkdir -p data results logs audit backup temp
chmod 755 data results
chmod 750 logs backup
chmod 700 audit temp
chmod 600 .env
```

### Step 5: System Validation

```bash
python -m src.pascal_zoning.pipeline --validate-system
python -m src.pascal_zoning.pipeline --input=data/sample.tif --output=results/validation_test
ls -la audit/
tail -f logs/agricultural_zoning_*.log
```

---

## Security & ISO 42001 Compliance

### Data Security

```bash
chmod 600 .env
chmod 700 audit/
chmod 755 src/
chmod 750 results/
```

### AI Governance Controls

* Automated model validation per run
* Full data lineage tracking
* Bias monitoring via metric reports
* Version-controlled model artifacts

### Audit Requirements

JSON-formatted audit log entries, e.g.:

```json
{
  "timestamp": "2025-06-11T10:30:00Z",
  "transaction_id": "uuid",
  "user": "production_user",
  "action": "zoning_analysis",
  "input_file": "field_001.tif",
  "model_version": "1.0.2",
  "validation_passed": true,
  "output_files": ["results/zones.geojson"],
  "processing_time_sec": 45.2
}
```

---

## Monitoring & Health Checks

### Health Check Script (`health_check.sh`)

```bash
#!/bin/bash
INSTALL_DIR="/opt/agricultural-zoning-ml"

python -m src.pascal_zoning.pipeline --health-check
python -m src.pascal_zoning.pipeline --validate-model

usage=$(df $INSTALL_DIR | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$usage" -gt 80 ]; then
  echo "WARNING: Disk usage ${usage}%" | tee -a audit/system_alerts.log
fi

mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$mem_usage" -gt 85 ]; then
  echo "WARNING: Memory usage ${mem_usage}%" | tee -a audit/system_alerts.log
fi
```

### Automated Monitoring

Add to `crontab`:

```
0 */4 * * * /opt/agricultural-zoning-ml/health_check.sh
0 2 * * * tar -czf backup/audit_$(date +\%Y\%m\%d).tar.gz audit/
0 3 * * 0 find temp/ -type f -mtime +7 -delete
```

---

## Troubleshooting

### Common Issues

1. **GDAL/GEOS Missing**

   ```bash
   # Ubuntu
   sudo apt install gdal-bin libgdal-dev libgeos-dev
   ```
2. **Memory Errors**

   ```bash
   MAX_MEMORY_MB=4096
   CHUNK_SIZE_MB=512
   ```
3. **Permission Denied**

   ```bash
   sudo chown -R agri_zoning:agri_zoning /opt/agricultural-zoning-ml
   chmod 600 .env
   ```
4. **Python Version Issues**

   ```bash
   python3.11 -m venv venv
   ```
5. **Model Validation Failures**

   ```bash
   python -m src.pascal_zoning.pipeline --validate-model --verbose
   ```

---

## Deployment Checklist

### Pre-Deployment (ISO 42001 Requirements)

*

### Deployment Validation

*

### Post-Deployment Compliance

*

---

## Change Management

1. **Change Request**: Document modifications
2. **Risk Assessment**: Evaluate AI impact
3. **Testing**: Validate in staging
4. **Approval**: Obtain sign-off
5. **Implementation**: Deploy with rollback
6. **Validation**: Confirm success
7. **Documentation**: Update docs

---

## Support & Maintenance

* **Daily**: Monitor health & audit logs
* **Weekly**: Review metrics & alerts
* **Monthly**: Validate model performance
* **Quarterly**: Security audit & compliance review

**Contacts:**

* [dev-team@australmetrics.com](mailto:dev-team@australmetrics.cL)
* [security@australmetrics.com](mailto:security@australmetrics.cL)
* [compliance@australmetrics.com](mailto:compliance@australmetrics.cL)

---

© 2025 AustralMetrics SpA. All rights reserved.
