# Security Policy

Welcome to the Pascal Zoning ML project's security policy. The safety and trust of our users is paramount. This document outlines our guidelines for reporting, triaging, and remediating security vulnerabilities, as well as best practices for dependency management and secure development.

---

## Table of Contents

1. [Supported Versions](#supported-versions)  
2. [Reporting a Vulnerability](#reporting-a-vulnerability)  
   - [Responsible Disclosure](#responsible-disclosure)  
   - [What to Include in Your Report](#what-to-include-in-your-report)  
3. [Security Response Process](#security-response-process)  
   - [Acknowledgment & Triage](#acknowledgment--triage)  
   - [Investigation & Fix](#investigation--fix)  
   - [Public Disclosure & Release](#public-disclosure--release)  
4. [Dependency Management](#dependency-management)  
   - [Routine Audits](#routine-audits)  
   - [Pinning and Updating](#pinning-and-updating)  
5. [Secure Development Practices](#secure-development-practices)  
   - [Code Review](#code-review)  
   - [Static Analysis & Linting](#static-analysis--linting)  
   - [Continuous Integration & Security Checks](#continuous-integration--security-checks)  
6. [Data Handling & Privacy](#data-handling--privacy)  
7. [Maintainers & Contacts](#maintainers--contacts)  
8. [Legal & Licensing](#legal--licensing)

---

## Supported Versions

We maintain security support for the following major versions of Pascal Zoning ML:

| Version | Release Date | Security Status            |
|---------|--------------|----------------------------|
| `v0.1.x`| 2025-06-05   | Supported until 2025-12-05 |
| `v0.2.x`| 2025-07-01   | Supported                  |
| `main`  | Ongoing      | Active development branch  |

- **Active Development (`main`)**: All new features, patches, and security fixes target the `main` branch. It is considered a "bleeding edge" release.
- **Stable Releases (`v0.x.y`)**: We backport critical security fixes and patches to the latest `v0.x.y` release series for at least six months after initial publication. After that, they enter "maintenance-only" mode and users are strongly encouraged to upgrade to the next major version.

---

## Reporting a Vulnerability

If you discover a security vulnerability in Pascal Zoning ML, please **do not create a public issue** on GitHub. Instead, follow our Responsible Disclosure guidelines below.

### Responsible Disclosure

1. **Email our security mailing list** at `security@australmetrics.com`.  
2. Use **PGP/GPG encryption** if possible. Our public key is available at:  
   `https://australmetrics.com/pgp-keys/security.asc`
3. Mark your email subject line as:  
   `[Pascal Zoning ML] Security Vulnerability Report`
4. Allow our maintainers up to **7 calendar days** to acknowledge your report.  
5. We will coordinate publicly to release a patch or mitigation, ideally within **30 days** of the first report (or sooner, depending on severity).

### What to Include in Your Report

- **Project & Version**: Specify `pascal-zoning-ml` and the exact version or commit SHA.  
- **Environment**: OS version, Python version, installation method (pip, conda, editable install).  
- **Description**: Clear, concise summary of the vulnerability (e.g., "Improper input validation in clustering routine allows code injection").  
- **Steps to Reproduce**: Minimal working example or proof-of-concept code, including inputs and expected vs. actual behavior.  
- **Impact Assessment**: How an attacker might exploit this issue (remote/local, data compromise, arbitrary code execution, denial of service, etc.).  
- **Suggested Fix** (optional): If you have an idea or patch, attach a diff or patch file.  
- **Contact Information**: Your name, email, and preferred method of contact for follow-up questions.

---

## Security Response Process

Once a valid security report is received, our response process follows these stages:

### Acknowledgment & Triage

- **Within 7 days** of receiving a report, we will send you an acknowledgment email.  
- We assign a **severity level** (Low, Medium, High, Critical) to the reported issue based on CVSS guidelines and context.  
- We engage any relevant maintainers or third-party experts (e.g., upstream library contacts) if the vulnerability involves external dependencies.

### Investigation & Fix

- We will create a **private GitHub issue** (labeled `security`) in the `pascal-zoning-ml` repository with restricted visibility.  
- Assign responsible maintainers to reproduce and patch the vulnerability.  
- If the vulnerability impacts external libraries (e.g., `scikit-learn` or `rasterio`), we coordinate upstream remediation as necessary.  
- Develop a patch branch (e.g., `security/patch-<shortid>`), including unit tests or integration tests covering the fix.  
- Perform **static code analysis** (MyPy, Flake8, Bandit) and **regression testing** before merging.

### Public Disclosure & Release

- **Release a patched version** under a new patch-level tag (e.g., `v0.2.1`), including a detailed changelog entry under **"Security Fixes."**  
- Publish a **security advisory** on GitHub (via the repository's "Security" tab) and on our website, summarizing:  
  - Affected versions  
  - Severity rating  
  - CVE assignment (if applicable)  
  - Description of the vulnerability  
  - Steps to upgrade or patch  
- Notify any third parties or downstream projects that might be affected (e.g., via PyPI, Conda channels).  
- After the CVE is assigned, update the `security/` folder with a `CVE-<year>-<number>.md` file describing the issue and resolution timeline.

---

## Dependency Management

### Routine Audits

- We run **monthly automated vulnerability scans** using tools like `pip-audit` and `safety` to detect known CVEs in our dependencies (e.g., `geopandas`, `scikit-learn`, `rasterio`, `numpy`).  
- Our CI pipeline includes a step (`ci/security-check.yml`) that fails if high-severity vulnerabilities are discovered in production dependencies.

### Pinning and Updating

- In `requirements.txt`, dependencies are pinned to **minimum required versions** plus a maximum safe version where feasible:  

```text
numpy>=1.24.0,<2.0.0
geopandas>=0.14.0,<1.0.0
scikit-learn>=1.3.0,<1.4.0
rasterio>=1.3.0,<2.0.0
typer>=0.9.0,<0.10.0
loguru>=0.7.2,<0.8.0
matplotlib>=3.8.0,<4.0.0
pandas>=2.1.0,<3.0.0
```

- We review major version upgrades quarterly and test them against our test suite before bumping requirements.
- Security patches to dependencies are applied within one week of release. We then bump the pinned version accordingly and update `requirements.txt` (and `requirements-dev.txt`) with an appropriate commit message, e.g.,

```
chore: bump geopandas to 0.14.2 (security patch CVE-2025-1234)
```

---

## Secure Development Practices

### Code Review

- All changes must go through a Pull Request (PR) on GitHub.
- At least two maintainers (or one maintainer + one security-savvy collaborator) must review the PR for correctness, potential security flaws, and adherence to project guidelines.
- Sensitive code paths—especially input validation, file I/O, and external library usage—receive extra scrutiny.

### Static Analysis & Linting

- We enforce MyPy for type checking (strict mode, except for temporarily disabled error codes).
- We run Flake8 for style and potential code smells.
- We use Bandit to catch common Python security issues (e.g., use of eval, insecure file permissions).
- A GitHub Actions workflow (`ci/lint-and-security.yml`) runs these tools on each PR. The PR must pass all checks before merging.

### Continuous Integration & Security Checks

Our CI pipeline includes:

1. Unit tests (pytest) with coverage checks.
2. Integration tests, including the `test_cli_workflow_creates_outputs` suite.
3. Static analysis (MyPy, Flake8).
4. Dependency vulnerability scan (pip-audit, safety).
5. Bandit for Python-specific security checks.

Any failure in steps 1–5 blocks merging until resolved.

---

## Data Handling & Privacy

Pascal Zoning ML does not collect or transmit any personally identifiable information (PII). However, users should be aware:

- The tool processes geospatial raster data (GeoTIFF). Ensure that any input raster files do not contain sensitive location metadata or embedded credentials.
- When exporting GeoPackage layers or CSV files, any embedded attribute tables may include custom user data—be mindful of file permissions.
- We do not include analytics or telemetry in the code. All processing is strictly local to the user's machine.

---

## Maintainers & Contacts

If you need to reach our security team or maintainers regarding a vulnerability or security question, please use:

**Security mailing list:**
```
security@australmetrics.com
```
(We monitor this address 24×7. Expect initial acknowledgment within 7 days.)

**PGP Key for encryption:**
```
https://australmetrics.com/pgp-keys/security.asc
```

**Public GitHub Issues:**
Create issues only for non-security-related bugs or feature requests. For security issues, use the private email above.

**Maintainers:**
- Alice Smith <alice.smith@australmetrics.com>
- Bob Martínez <bob.martinez@australmetrics.com>

---

## Legal & Licensing

Pascal Zoning ML is licensed under the MIT License. There is no warranty, express or implied, regarding security, performance, or fitness for a particular purpose. By using this software, you acknowledge that any vulnerabilities discovered should be responsibly disclosed to our security team.

---

*Last updated: 2025-06-05*