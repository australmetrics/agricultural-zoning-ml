# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.1   | :white_check_mark: |
| 1.0.0   | :white_check_mark: |
| < 1.0   | :x:                |

## Security and Privacy Considerations

### Data Protection
- Input raster data is processed locally
- No data is transmitted externally
- Results and logs are stored in user-specified locations
- Backup logs are encrypted with SHA-256

### ISO 42001 Compliance
This project adheres to ISO 42001 standards for AI systems:
- Traceability of operations through detailed logging
- Validation of input/output data formats
- Clear documentation of parameters and their impacts
- System behavior predictability and reproducibility

## Reporting a Vulnerability

1. **DO NOT** open public issues for security vulnerabilities
2. Email security@australmetrics.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive a response within 48 hours
4. A fix will be developed and deployed as per severity:
   - Critical: Within 24 hours
   - High: Within 72 hours
   - Medium: Next release
   - Low: Scheduled as needed

## Privacy Policy
See our full privacy policy in [docs/compliance/privacy_policy.md](docs/compliance/privacy_policy.md)
