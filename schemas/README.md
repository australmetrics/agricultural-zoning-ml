# README.md

```markdown
# PASCAL Zoning ML Schemas

This directory contains JSON schemas for validating Pascal Zoning ML manifests, configurations, and outputs.

## Available Schemas

### manifest.schema.json  
Validates the Pascal Zoning ML manifest file (`manifest.json`), ensuring:
- Correct interface definitions (input raster, indices, parameters, output files, logging)
- Required fields presence
- Proper format specifications for file names and parameter types
- Conformance to ISO 42001 traceability requirements

### zoning_output.schema.json  
Validates the structure of the output manifest (`zoning_output_manifest.json`) produced by Pascal Zoning ML, ensuring:
- Required fields (version, timestamp, input metadata)
- Correct listing and paths for GeoPackage, CSV, JSON, and PNG artifacts
- Processing metadata (runtime, software version)

## Usage

The schema validation is automatically performed by the GitHub Actions workflow whenever changes are made to the manifest or output-manifest files. You can also validate manually using:

```bash
python - << 'EOF'
import json, sys
from jsonschema import validate, ValidationError

# Validate Pascal Zoning ML manifest
schema = json.load(open("schema/manifest.schema.json"))
instance = json.load(open("manifest.json"))
try:
    validate(instance=instance, schema=schema)
    print("✔ manifest.json is valid.")
except ValidationError as e:
    print("✘ manifest.json is invalid:", e)
    sys.exit(1)

# Validate Pascal Zoning ML output manifest
output_schema = json.load(open("schema/zoning_output.schema.json"))
output_instance = json.load(open("zoning_output_manifest.json"))
try:
    validate(instance=output_instance, schema=output_schema)
    print("✔ zoning_output_manifest.json is valid.")
except ValidationError as e:
    print("✘ zoning_output_manifest.json is invalid:", e)
    sys.exit(1)
EOF

