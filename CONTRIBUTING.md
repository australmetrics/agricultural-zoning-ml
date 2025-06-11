# Contributing to Pascal Zoning

Please read our Code of Conduct in [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md).

## Getting Started

* Fork the repository and create a feature branch named `feat/issue-{number}`.
* Clone your fork locally:

  ```bash
  git clone https://github.com/your-username/agricultural-zoning-ml.git
  cd agricultural-zoning-ml
  ```
* Install development prerequisites (see [Environment Setup](docs/user_guide/installation.md)).

## Submitting Changes

1. Open an issue to propose your change or fix.
2. Implement your code on a descriptive branch and add or update tests.
3. Follow Conventional Commits for your commit messages (see [commit template](docs/technical/commit-template.md)).
4. Ensure tests pass with `pytest --cov` and adhere to coverage targets (>90%).
5. Submit a pull request referencing the issue and include a brief description of your changes.

## Development Environment

See the detailed setup in \[docs/user\_guide/quick\_start.md] and \[docs/user\_guide/troubleshooting.md].

## Coding Standards

* Follow PEP 8 and use type hints.
* Format code with Black and isort; lint with Flake8 and MyPy (see [coding standards](docs/technical/coding-standards.md)).

## Testing

Run:

```bash
pytest --cov
```

See \[docs/user\_guide/troubleshooting.md] for common issues and \[docs/technical/testing.md] for test structure.

## Documentation

* Use Google-style docstrings for all public functions and classes.
* Update Sphinx or MkDocs sources in `docs/technical/api_documentation.md`.

## ISO 42001 Compliance

This project complies with ISO 42001:2023. All changes must include updated documentation, dependency records, and traceable test results (see [compliance guide](docs/compliance/iso42001_compliance.md)).

## Questions or Feedback

If you have any questions or need guidance, please:

* Search existing issues or file a new one.
* Contact maintainers via the issue tracker or email at `code-of-conduct@australmetrics.com`.

Thank you for helping improve Pascal Zoning!
