# Contributing Guide

## Development Process

1. **Fork the Repository**
   - Create a fork of the main repository
   - Clone your fork locally

2. **Create a Branch**
   - Create a branch for your contribution
   - Use descriptive names (e.g., `feature/new-index`)

3. **Development**
   - Follow code standards
   - Keep commits atomic and descriptive
   - Add tests for new features

4. **Testing**
   - Run `pytest` to verify tests
   - Ensure `flake8` shows no errors
   - Check types with `mypy`

5. **Documentation**
   - Update relevant documentation
   - Include docstrings in new code
   - Update `CHANGELOG.md`

6. **Pull Request**
   - Create a PR against the `main` branch
   - Describe changes made
   - Reference related issues

## Code Standards

- 100 characters line limit
- Follow PEP 8
- Use type hints
- Document functions and classes
- Include tests

## Logging & Traceability

- Use established logging system
- Include relevant information in logs
- Maintain ISO 42001 compliance

## Review Process

1. CI/CD must pass
2. Review by at least one maintainer
3. Updated documentation
4. Tests added or updated

## Release Process

When you're ready to publish a new version:

1. **Bump version**
   
   Edit `pyproject.toml` and update the version number:
   ```toml
   version = "X.Y.Z"
   ```

2. **Update Changelog**
   
   Add a new section to `CHANGELOG.md`:
   ```markdown
   ## [X.Y.Z] – YYYY-MM-DD
   ### Changed
   - Describe your changes here
   ```

3. **Commit & Tag**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore(release): vX.Y.Z"
   git tag vX.Y.Z
   ```

4. **Push & Publish**
   ```bash
   git push && git push --tags
   ```
   
   Your GitHub Actions workflow will automatically build and publish the package.

## Contact

For questions or issues, please open an issue at:
https://github.com/australmetrics/pascal-ndvi-block/issues/new

Thank you for contributing! 😊