# PASCAL NDVI Block Schemas

This directory contains JSON schemas for validating block interfaces and configurations.

## Available Schemas

### manifest.schema.json
Validates the block's manifest file (`manifest.json`) ensuring:
- Correct interface definitions (input/output)
- Valid parameter ranges and types
- Required fields presence
- Proper format specifications

## Future Extensions
The schema system is designed to be extensible. Future versions may include:
- Validation for new indices (e.g., NDRE)
- Additional input data formats
- Extended output configurations
- Integration with other PASCAL blocks

## Usage
The schema validation is automatically performed by the GitHub Actions workflow
whenever changes are made to the manifest file. You can also validate manually using:

```bash
check-jsonschema --schemafile schemas/manifest.schema.json manifest.json
```
