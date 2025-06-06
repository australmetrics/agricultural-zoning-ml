# Contributing to Agricultural Zoning System

We welcome contributions to the Agricultural Zoning System! This document provides guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [ISO 42001 Compliance](#iso-42001-compliance)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Environment

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup

```bash
# Clone the repository
git clone https://github.com/australmetrics/agricultural-zoning-system.git
cd agricultural-zoning-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Dependencies

This project depends on:
- `pascal-ndvi-block` for spectral indices calculation
- Machine learning libraries (scikit-learn)
- Geospatial libraries (geopandas, rasterio, shapely)
- Standard scientific computing stack (numpy, matplotlib)

## Submitting Changes

### Pull Request Process

1. **Create a descriptive branch name**:
   ```bash
   git checkout -b feature/new-clustering-algorithm
   git checkout -b bugfix/zone-validation-issue
   git checkout -b docs/improve-api-documentation
   ```

2. **Make your changes**:
   - Follow coding standards
   - Add appropriate tests
   - Update documentation
   - Maintain ISO 42001 compliance

3. **Test thoroughly**:
   ```bash
   pytest tests/
   python -m pytest --cov=src/
   ```

4. **Update documentation**:
   - Update docstrings
   - Update README if needed
   - Update CHANGELOG.md

5. **Submit pull request**:
   - Provide clear description
   - Reference related issues
   - Include testing results
   - Ensure CI passes

### Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(zoning): add support for custom clustering algorithms
fix(validation): resolve issue with spectral index validation
docs(api): update clustering algorithm documentation
```

## Coding Standards

### Python Style Guide

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable and function names

### Code Quality Tools

We use the following tools to maintain code quality:

```bash
# Code formatting
black src/ tests/

# Import sorting
isort src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Documentation Style

- Use Google-style docstrings
- Include type information
- Provide examples for complex functions
- Document all public APIs

Example:
```python
def generate_sampling_points(
    zones: gpd.GeoDataFrame,
    points_per_zone: int = 10,
    min_distance: float = 50.0
) -> gpd.GeoDataFrame:
    """
    Generate stratified sampling points within management zones.
    
    Args:
        zones: GeoDataFrame containing management zones
        points_per_zone: Number of points to generate per zone
        min_distance: Minimum distance between points in meters
        
    Returns:
        GeoDataFrame containing sampling points with zone assignments
        
    Example:
        >>> zones = load_zones('zones.gpkg')
        >>> points = generate_sampling_points(zones, points_per_zone=15)
        >>> print(f"Generated {len(points)} sampling points")
    """
```

## Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_zoning.py
│   ├── test_validation.py
│   └── test_sampling.py
├── integration/
│   ├── test_pipeline.py
│   └── test_ndvi_integration.py
└── fixtures/
    ├── sample_data/
    └── conftest.py
```

### Writing Tests

- Write unit tests for individual functions
- Write integration tests for workflows
- Use pytest fixtures for test data
- Aim for >90% code coverage
- Include edge cases and error conditions

Example test:
```python
def test_zone_validation_valid_input():
    """Test zone validation with valid spectral indices."""
    features = {
        'ndvi': np.random.uniform(-1, 1, (100, 100)),
        'evi': np.random.uniform(-1, 1, (100, 100))
    }
    zoning = AgriculturalZoning()
    # Should not raise exception
    zoning._validate_inputs(features)

def test_zone_validation_invalid_range():
    """Test zone validation with out-of-range values."""
    features = {
        'ndvi': np.random.uniform(-2, 2, (100, 100))  # Invalid range
    }
    zoning = AgriculturalZoning()
    with pytest.raises(ValidationError):
        zoning._validate_inputs(features)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ --cov-report=html

# Run specific test file
pytest tests/unit/test_zoning.py

# Run with verbose output
pytest -v
```

## Documentation

### API Documentation

- Use Sphinx for API documentation
- Include examples in docstrings
- Document all public interfaces
- Keep documentation up to date

### User Documentation

- Update README.md for user-facing changes
- Include usage examples
- Document configuration options
- Provide troubleshooting guides

## ISO 42001 Compliance

This project follows ISO 42001 standards for AI management systems. When contributing:

### Data Management
- Document data sources and transformations
- Ensure reproducibility
- Validate input data thoroughly
- Log all processing steps

### Model Documentation
- Document algorithm choices and parameters
- Record model performance metrics
- Maintain version control for models
- Document known limitations

### Risk Management
- Consider potential failure modes
- Implement appropriate validation
- Document assumptions and constraints
- Include uncertainty quantification

### Traceability
- Maintain clear audit trails
- Document decision rationale
- Version all components
- Link requirements to implementation

## Questions?

If you have questions about contributing, please:

1. Check existing issues and documentation
2. Open a new issue for discussion
3. Contact the maintainers

Thank you for contributing to the Agricultural Zoning System!