# Troubleshooting Guide

© 2025 AustralMetrics SpA. All rights reserved.

This guide provides solutions to common issues encountered when using the PASCAL NDVI Block module, following ISO 42001 traceability and documentation standards.

## Before You Start

### Check System Requirements
- Python 3.7 or higher
- Required dependencies installed (`pip install -r requirements.txt`)
- Sufficient disk space for input/output files
- Valid input imagery (Sentinel-2 or Landsat format)

### Enable Debug Logging
For detailed troubleshooting information, set debug logging in your `.env` file:
```
LOG_LEVEL=DEBUG
```

All debugging information will be saved to `results/logs/pascal_ndvi_YYYYMMDD_HHMMSS.log`.

## Installation Issues

### Problem: ImportError or ModuleNotFoundError
**Symptoms:**
```
ImportError: No module named 'rasterio'
ModuleNotFoundError: No module named 'geopandas'
```

**Solutions:**
1. **Verify virtual environment activation:**
   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **For GDAL/rasterio issues on Windows:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install GDAL
   pip install rasterio
   ```

### Problem: Permission Denied Errors
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. **Run with appropriate permissions:**
   - Windows: Run Command Prompt as Administrator
   - Linux/Mac: Use `sudo` if necessary, or change file permissions

2. **Check output directory permissions:**
   ```bash
   # Create results directory with proper permissions
   mkdir -p results/logs
   chmod 755 results
   ```

## Input Data Issues

### Problem: Image File Not Found
**Symptoms:**
```
FileNotFoundError: Image file not found: data/my_image.tif
```

**Solutions:**
1. **Verify file path:**
   ```bash
   ls -la data/  # Linux/Mac
   dir data\     # Windows
   ```

2. **Use absolute paths:**
   ```bash
   python -m src.main indices --image=/full/path/to/image.tif
   ```

3. **Check file permissions:**
   ```bash
   chmod 644 data/my_image.tif  # Linux/Mac
   ```

### Problem: Unsupported Image Format
**Symptoms:**
```
Error: Unable to read image bands
rasterio.errors.RasterioIOError
```

**Solutions:**
1. **Supported formats:**
   - GeoTIFF (.tif, .tiff)
   - Sentinel-2 JP2 files (.jp2)
   - Landsat GeoTIFF files

2. **Convert unsupported formats:**
   ```bash
   # Using GDAL
   gdal_translate input.jpg output.tif
   ```

3. **Verify image integrity:**
   ```bash
   gdalinfo data/my_image.tif
   ```

### Problem: Missing Spectral Bands
**Symptoms:**
```
Error: Required bands not found in image
KeyError: 'Band X not available'
```

**Solutions:**
1. **For Sentinel-2 imagery:**
   - Required bands: B4 (Red), B8 (NIR), B5 (Red Edge), B8A (NIR Narrow)
   - Ensure all bands are present in the image file

2. **For Landsat imagery:**
   - Required bands: Band 4 (Red), Band 5 (NIR)
   - Check band naming convention

3. **Verify band structure:**
   ```bash
   gdalinfo -checksum data/my_image.tif
   ```

## Processing Errors

### Problem: Memory Errors
**Symptoms:**
```
MemoryError: Unable to allocate array
numpy.core._exceptions.MemoryError
```

**Solutions:**
1. **Reduce image size:**
   - Use clipping functionality to process smaller areas
   - Resample image to lower resolution

2. **Increase system memory:**
   - Close unnecessary applications
   - Use a machine with more RAM

3. **Process in tiles:**
   ```bash
   # Process smaller sections of large images
   python -m src.main clip --image=large_image.tif --shapefile=small_area.shp
   ```

### Problem: Invalid Pixel Values
**Symptoms:**
```
RuntimeWarning: invalid value encountered in divide
All NDVI values are NaN
```

**Solutions:**
1. **Check for valid pixel ranges:**
   - Ensure pixel values are within expected ranges (0-10000 for Sentinel-2)
   - Verify no-data values are properly masked

2. **Inspect input data:**
   ```python
   import rasterio
   with rasterio.open('data/my_image.tif') as src:
       data = src.read(1)
       print(f"Min: {data.min()}, Max: {data.max()}")
   ```

3. **Apply proper scaling:**
   - Sentinel-2: Values typically range 0-10000
   - Landsat: Values typically range 0-65535

## Output Issues

### Problem: Empty Results Directory
**Symptoms:**
- No output files generated
- Missing NDVI/NDRE/SAVI results

**Solutions:**
1. **Check log files:**
   ```bash
   # View latest log
   ls -lt results/logs/
   cat results/logs/pascal_ndvi_*.log
   ```

2. **Verify write permissions:**
   ```bash
   ls -la results/
   mkdir -p results/indices
   ```

3. **Run with verbose output:**
   ```bash
   python -m src.main indices --image=data/my_image.tif --verbose
   ```

### Problem: Corrupted Output Files
**Symptoms:**
- Cannot open result files
- Garbled or incomplete data

**Solutions:**
1. **Verify output integrity:**
   ```bash
   gdalinfo results/indices/ndvi_result.tif
   ```

2. **Check disk space:**
   ```bash
   df -h  # Linux/Mac
   dir   # Windows
   ```

3. **Re-run processing:**
   ```bash
   # Clear previous results and re-run
   rm -rf results/indices/*
   python -m src.main indices --image=data/my_image.tif
   ```

## CLI Command Issues

### Problem: Command Not Recognized
**Symptoms:**
```
python: No module named src.main
Command 'pascal-ndvi' not found
```

**Solutions:**
1. **Use proper module syntax:**
   ```bash
   python -m src.main [command] [options]
   ```

2. **Verify current directory:**
   ```bash
   pwd  # Should be in pascal-ndvi-block/
   ls   # Should see src/ directory
   ```

3. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### Problem: Invalid Command Arguments
**Symptoms:**
```
Error: Invalid value for '--image'
Usage: python -m src.main [OPTIONS] COMMAND [ARGS]
```

**Solutions:**
1. **Check command syntax:**
   ```bash
   python -m src.main --help
   python -m src.main indices --help
   ```

2. **Use proper flag format:**
   ```bash
   # Correct
   python -m src.main indices --image=data/file.tif
   
   # Also correct
   python -m src.main indices --image data/file.tif
   ```

## Performance Issues

### Problem: Slow Processing
**Symptoms:**
- Long processing times
- System becoming unresponsive

**Solutions:**
1. **Monitor system resources:**
   ```bash
   # Linux/Mac
   top
   htop
   
   # Windows
   Task Manager
   ```

2. **Optimize processing:**
   - Use smaller input images
   - Process during off-peak hours
   - Close unnecessary applications

3. **Enable progress monitoring:**
   ```bash
   # Check log files for progress
   tail -f results/logs/pascal_ndvi_*.log
   ```

## Logging and Audit Issues

### Problem: Missing Log Files
**Symptoms:**
- No logs in `results/logs/`
- Cannot track processing history

**Solutions:**
1. **Verify log directory permissions:**
   ```bash
   mkdir -p results/logs
   chmod 755 results/logs
   ```

2. **Check environment configuration:**
   ```bash
   # Verify .env file exists and contains:
   cat .env
   # USERNAME=your_username
   # LOG_LEVEL=INFO
   ```

3. **Force log creation:**
   ```bash
   touch results/logs/test.log
   ls -la results/logs/
   ```

### Problem: Log Files Too Large
**Symptoms:**
- Disk space issues
- Slow log file access

**Solutions:**
1. **Enable log rotation:**
   - Logs are automatically backed up in `results/logs/backup/`
   - Old logs are compressed and archived

2. **Clean old logs:**
   ```bash
   # Remove logs older than 30 days
   find results/logs/ -name "*.log" -mtime +30 -delete
   ```

3. **Adjust log level:**
   ```bash
   # In .env file, set:
   LOG_LEVEL=WARNING  # Reduces log verbosity
   ```

## ISO 42001 Compliance Issues

### Problem: Audit Trail Incomplete
**Symptoms:**
- Missing processing timestamps
- Insufficient traceability information

**Solutions:**
1. **Verify logging configuration:**
   - Ensure `USERNAME` is set in `.env` file
   - Check log level is appropriate (INFO or DEBUG)

2. **Validate log integrity:**
   ```bash
   # Check SHA-256 hashes
   ls results/logs/*.sha256
   sha256sum -c results/logs/pascal_ndvi_*.sha256
   ```

3. **Ensure complete audit trail:**
   - All commands generate logs
   - User information is recorded
   - Processing parameters are saved

## Getting Additional Help

### Collecting Diagnostic Information
When reporting issues, please provide:

1. **System Information:**
   ```bash
   python --version
   pip list | grep -E "(rasterio|geopandas|numpy|typer|loguru)"
   ```

2. **Error Logs:**
   ```bash
   # Latest log file
   cat results/logs/pascal_ndvi_*.log | tail -100
   ```

3. **Input Data Information:**
   ```bash
   gdalinfo data/your_image.tif
   ```

### Contact Information
- **Internal Issues**: Create GitHub issue in the internal repository
- **Urgent Support**: Contact AustralMetrics SpA development team
- **Documentation**: Refer to `docs/` folder for additional guides

### ISO 42001 Compliance
All troubleshooting activities are logged for compliance purposes. Ensure proper documentation of:
- Issue description and timestamps
- Steps taken to resolve
- Final resolution and verification
- User information and system state

This ensures full traceability and audit compliance as required by ISO 42001 standards.