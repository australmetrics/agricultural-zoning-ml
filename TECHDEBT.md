# TECHDEBT.md

This document tracks all outstanding technical debt discovered during automated checks. It is intended to serve as a single source of truth for tasks that should be addressed over time, but which do not block the current development workflow.

---

## 1. MyPy: Temporarily Disabled Error Codes

To accelerate development and because some dependencies lack complete type stubs, the following MyPy error codes have been temporarily disabled in `mypy.ini`:

```ini
[mypy]
# ...
disable_error_code =
    return-any      # Ignore functions that return Any despite a more specific signature
    import          # Ignore imports of modules lacking type stubs (e.g., sklearn)
    attr-defined    # Ignore warnings about attributes MyPy thinks do not exist (e.g., `.append()` on a NumPy array)
    no-redef        # Ignore redefinitions of attributes (e.g., `zone_stats` defined twice)
    assignment      # Ignore type incompatibilities in complex assignments
    no-untyped-def  # Ignore functions missing an explicit return type annotation
```

**Debt Item:**
- Review each disabled error code and re-enable one at a time once the underlying compatibility or type-stub issue is resolved.
- Wherever possible, add explicit type annotations or stub files to reduce reliance on broad disabling.

---

## 2. Formatting & PEP8 (Flake8 / Black)

### 2.1. Black "would reformat" Warnings

Black reported that 13 files would be reformatted. Until Black is run in "autofix" mode, these warnings remain:

```bash
src/pascal_zoning/__init__.py
src/pascal_zoning/config.py
src/pascal_zoning/interface.py
src/pascal_zoning/logging_config.py
src/pascal_zoning/pipeline.py
src/pascal_zoning/viz.py
src/pascal_zoning/zoning.py
tests/unit/conftest.py
tests/unit/test_pipeline.py
tests/unit/test_viz.py
tests/unit/test_interface.py
tests/integration/test_workflow.py
tests/unit/test_zoning_core.py
```

**Debt Item:**
- Run `black src/ tests/` and commit the reformatted files. This will automatically correct indentation, line breaks, trailing whitespace, blank-line rules, and quote styles.
- After Black is applied, re-run flake8 to catch any leftovers.

### 2.2. Flake8 Violations Remaining After Black

Once Black is applied, some Flake8 errors still require manual attention:

#### W291 (trailing whitespace)
There are spaces at the end of multiple lines. Remove the trailing spaces so each blank or code line ends exactly at the last visible character.

#### W293 (blank line contains whitespace)
Several empty lines contain one or more spaces/tabs. Delete all whitespace on blank lines so they are truly empty.

#### W391 (blank line at end of file)
Some files have more than one blank line or trailing spaces at the very end. Leave at most one completely empty line with no spaces at the end of each file.

#### E302 / E303 / E305 / E301 (incorrect blank-line count)
- **E302, E305:** There should be exactly two blank lines between top-level class/function definitions.
- **E303:** Avoid having more than two consecutive blank lines.
- **E301:** There must be one blank line between methods inside a class.

Correct each occurrence by inserting or removing blank lines as needed.

#### F401 (imported but unused)
Remove or use these unused imports:

- `src/pascal_zoning/interface.py`: warnings, rasterio.coords.BoundingBox
- `src/pascal_zoning/pipeline.py`: shapely.geometry.Polygon, shapely.geometry.MultiPolygon
- `src/pascal_zoning/viz.py`: numpy as np
- `src/pascal_zoning/zoning.py`: typing.TypeVar, shapely.geometry.mapping, shapely.geometry.shape
- `tests/unit/test_viz.py`: numpy as np, pandas as pd, pathlib.Path
- `tests/unit/test_zoning_core.py`: pathlib.Path

#### E402 (module level import not at top of file)
In `tests/unit/test_viz.py`, move imports that appear mid-file to the top of the module (right after any module-level docstring).

#### E501 (line too long)
Split or reformat lines longer than 100 characters:

- `src/pascal_zoning/pipeline.py`: lines 96, 119, 222, 307
- `src/pascal_zoning/zoning.py`: lines 216, 336, 393, 404, 520, 552, 652, 771
- `tests/integration/test_workflow.py`: lines 92, 100

Break these into multiple lines using parentheses or implicit continuation.

#### E128 (continuation line under-indented)
Fix indentation for multi-line statements so continuations align either under the opening delimiter or are indented by 4 spaces from the previous line:

- `src/pascal_zoning/zoning.py`: lines 836–837

**Debt Item:**
- After running Black, go through each listed Flake8 violation and fix manually.
- Commit these changes so that `flake8 src/ tests/` returns no errors.

---

## 3. Docstrings & Documentation Style (pydocstyle)

Running `pydocstyle src/` uncovered the following:

### D100 (Missing docstring in public module)
- `src/pascal_zoning/pipeline.py`
- `src/pascal_zoning/zoning.py`

### D101 (Missing docstring in public class)
- `src/pascal_zoning/pipeline.py`: class ZoningPipeline
- `src/pascal_zoning/zoning.py`: classes ClusterMetrics, ZoneStats, ZoningResult, ZonificationError, ValidationError, AgriculturalZoning

### D103 (Missing docstring in public function)
- `src/pascal_zoning/pipeline.py`: functions run, main, zonify
- `src/pascal_zoning/interface.py`: methods like __init__, safe_divide, load_spectral_indices, validate_spectral_data
- `src/pascal_zoning/logging_config.py`: function setup_logging

### D200 (One-line docstring should fit on one line with quotes)
Several one-line docstrings in `src/pascal_zoning/interface.py`, `src/pascal_zoning/logging_config.py`, `src/pascal_zoning/viz.py`, `src/pascal_zoning/zoning.py` exceed length or use multiple lines unnecessarily.

### D204 (One blank line required after class docstring)
All public classes in `src/pascal_zoning/config.py`, `interface.py`, `zoning.py` need a blank line after the closing triple-quote of the docstring before any method definitions.

### D205 (One blank line required between summary line and description)
Multi-line docstrings in `src/pascal_zoning/config.py`, `interface.py`, `pipeline.py`, `zoning.py` need an extra blank line between the first summary line and subsequent description.

### D400 (First line should end with a period)
Many docstring summaries in `config.py`, `interface.py`, `viz.py`, `zoning.py` do not end with a period.

### D107 (Missing docstring in __init__ method)
Public `__init__` methods in classes from `src/pascal_zoning/pipeline.py`, `interface.py`, `zoning.py` lack docstrings.

### D301 (Use raw string if any backslashes in docstring)
If any docstring includes a Windows-style path (`\`), it must be written as a raw string `r""" ... """`.

**Debt Item:**
- For each module listed under D100, add a module-level docstring at the top.
- For each public class listed under D101, add a one-line (or multi-line) docstring describing its purpose, ending with a period.
- For each public function or method under D103, add an appropriate docstring.
- Convert docstrings flagged by D200 into single-line form if they are short enough; otherwise ensure multi-line format is correct.
- Insert a blank line after every class docstring (D204).
- Insert a blank line between summary and body in multi-line docstrings (D205).
- Ensure every docstring summary ends with a period (D400).
- Add docstrings inside each public `__init__` (D107).
- Convert any docstring containing backslashes to raw strings (D301).

---

## 4. Test Coverage (pytest + pytest-cov)

**Issue:** pytest-cov was configured to measure coverage of a module named `pascal_ndvi_block`, which does not match the actual package name (`pascal_zoning`). As a result, no coverage data was collected.

```bash
pytest tests/ --cov=pascal_ndvi_block --cov-report=xml --cov-report=term-missing:skip-covered
# CoverageWarning: Module pascal_ndvi_block was never imported.
```

**Debt Item:**
- Update the coverage flag in `run_checks.ps1` (and CI workflows) from:
  ```powershell
  --cov=pascal_ndvi_block
  ```
  to:
  ```powershell
  --cov=pascal_zoning
  ```
- Confirm that all tests import and execute code from `pascal_zoning` so that `coverage.xml` is generated properly.

---

## 5. Security Analysis (Bandit)

Bandit reported no issues in `src/pascal_zoning`. This section is for completeness; there is no open debt here, but periodic re-scanning is recommended.

**Debt Item (optional):**
- Re-run `bandit -r src/pascal_zoning -ll` after major code changes to ensure no new issues have been introduced.

---

## 6. Dependencies Vulnerability (Safety)

**Issue:** `safety check` exited with an error, indicating one or more dependencies in `requirements.txt` have known vulnerabilities.

```bash
❌ Error in dependency verification
```

**Debt Item:**
1. Run:
   ```bash
   safety check --full-report
   ```
   to identify which package(s) and version(s) are flagged.

2. Update `requirements.txt` (or `setup.py`) to bump vulnerable dependencies to a non-vulnerable version range. For example:
   ```diff
   -somepackage==1.2.3
   +somepackage>=1.2.4,<2.0.0
   ```

3. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Rerun `safety check` until no vulnerabilities remain.

---

## 7. Compliance Files (ISO 42001)

The automated compliance check expects certain files in fixed paths:

```powershell
$requiredFiles = @(
  "src/logging_config.py",
  "docs/compliance/iso42001_compliance.md",
  "README.md",
  "CHANGELOG.md",
  "CODE_OF_CONDUCT.md",
  "CONTRIBUTING.md"
)
```

### Issues Detected:
- `src/logging_config.py` does not exist at that exact path. The actual path is `src/pascal_zoning/logging_config.py`.
- Ensure `docs/compliance/iso42001_compliance.md` exists (or move it accordingly).
- Verify `README.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md` all exist in the repository root.

**Debt Item:**
1. Update the paths in the compliance check script (`run_checks.ps1`) to reflect actual file locations. For example:
   ```powershell
   $requiredFiles = @(
       "src/pascal_zoning/logging_config.py",
       "docs/iso42001/iso42001_compliance.md",
       "README.md",
       "CHANGELOG.md",
       "CODE_OF_CONDUCT.md",
       "CONTRIBUTING.md"
   )
   ```

2. Create or move any missing files into the expected directories:
   - `src/pascal_zoning/logging_config.py`
   - `docs/iso42001/iso42001_compliance.md`
   - `README.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` at project root.

---

## 8. Summary of Immediate Next Steps

### 1. Run Black
```bash
black src/ tests/
```
Commit the changes to correct most formatting issues.

### 2. Fix Flake8 Violations
- Remove unused imports (F401).
- Move any imports not at the top of the file (E402).
- Delete trailing whitespace (W291) and stray whitespace on blank lines (W293).
- Adjust blank-line counts (E301, E302, E303, E305).
- Break lines longer than 100 characters (E501) or rely on Black's 88-character limit.
- Fix continuation indent (E128).

### 3. Add Docstrings
- Write module-level docstrings for every public `.py`.
- Add one-line or multi-line docstrings for each public class (D101).
- Add docstrings for every public function/method (D103).
- Ensure D200, D204, D205, D400, D107, and D301 are addressed in each docstring.

### 4. Correct Coverage Flag
- Modify `run_checks.ps1` and CI config to use `--cov=pascal_zoning` instead of `pascal_ndvi_block`.

### 5. Resolve Dependency Vulnerabilities
- Run `safety check --full-report`.
- Bump or replace vulnerable packages in `requirements.txt`.
- Reinstall and verify with `safety check` again.

### 6. Fix Compliance File Paths
- Update `$requiredFiles` in `run_checks.ps1` to actual paths (e.g., `src/pascal_zoning/logging_config.py`).
- Ensure each required file is present in the repository.
