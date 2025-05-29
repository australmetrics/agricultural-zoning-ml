# Frequently Asked Questions (FAQ)

© 2025 AustralMetrics SpA. All rights reserved.

Common questions and answers about the PASCAL NDVI Block module, designed for ISO 42001 compliance and ease of use.

## General Questions

### Q: What is the PASCAL NDVI Block?
**A:** PASCAL NDVI Block is a high-performance Python module designed to calculate vegetation indices (NDVI, NDRE, SAVI) from Sentinel-2 and Landsat satellite imagery. It focuses on simplicity, automation, and ISO 42001 compliance for artificial intelligence management systems.

### Q: Which satellite imagery formats are supported?
**A:** The module supports:
- **Sentinel-2**: GeoTIFF and JP2 formats with bands B4 (Red), B8 (NIR), B5 (Red Edge), B8A (NIR Narrow)
- **Landsat**: GeoTIFF format with bands 4 (Red) and 5 (NIR)
- **General**: Any GeoTIFF file with appropriate spectral bands

### Q: What vegetation indices can I calculate?
**A:** Three vegetation indices are supported:
- **NDVI** (Normalized Difference Vegetation Index): (NIR - Red) / (NIR + Red)
- **NDRE** (Normalized Difference Red Edge): (NIR - RedEdge) / (NIR + RedEdge)
- **SAVI** (Soil Adjusted Vegetation Index): ((NIR - Red) / (NIR + Red + L)) × (1 + L), where L = 0.5

### Q: What are the system requirements?
**A:** 
- **Python**: 3.7 or higher
- **Operating Systems**: Windows, Linux, macOS
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large images)
- **Disk Space**: At least 2x the size of your input imagery
- **Dependencies**: Automatically installed via `requirements.txt`

## Installation and Setup

### Q: How do I install the module?
**A:** Follow these steps:
```bash
# 1. Clone the repository
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Q: Do I need to install GDAL separately?
**A:** No, GDAL is included as a dependency through rasterio. However, if you encounter installation issues on Windows, you may need to install GDAL manually:
```bash
pip install GDAL
pip install rasterio
```

### Q: What should I put in the .env file?
**A:** The `.env` file should contain:
```
USERNAME=your_username_here
LOG_LEVEL=INFO
```
- `USERNAME`: Used for audit logging (ISO 42001 compliance)
- `LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Q: Can I run this without a virtual environment?
**A:** While possible, it's strongly recommended to use a virtual environment to avoid dependency conflicts and maintain a clean Python installation.

## Usage Questions

### Q: What's the simplest way to process an image?
**A:** Use the automated processing command:
```bash
python -m src.main auto --image=data/my_image.tif
```
This will automatically detect bands and calculate all three indices (NDVI, NDRE, SAVI).

### Q: How do I process only a specific area of my image?
**A:** Use the clipping functionality with a shapefile:
```bash
# Clip and process in one command
python -m src.main auto --image=data/my_image.tif --shapefile=data/area.shp

# Or clip first, then process
python -m src.main clip --image=data/my_image.tif --shapefile=data/area.shp
python -m src.main indices --image=results/clipped_image.tif
```

### Q: Can I calculate only specific indices?
**A:** Currently, the module calculates all three indices (NDVI, NDRE, SAVI) together for efficiency. Individual index calculation is not supported in this version.

### Q: Where are the results saved?
**A:** Results are saved in the `results/` directory by default:
- **Indices**: `results/indices/ndvi_result.tif`, `results/indices/ndre_result.tif`, `results/indices/savi_result.tif`
- **Clipped images**: `results/clipped/`
- **Logs**: `results/logs/pascal_ndvi_YYYYMMDD_HHMMSS.log`

### Q: Can I specify a different output directory?
**A:** Yes, use the `--output` parameter:
```bash
python -m src.main indices --image=data/my_image.tif --output=my_custom_results
```

## Data and Processing

### Q: What image sizes can the module handle?
**A:** The module can process various image sizes:
- **Small images** (< 100 MB): Process directly
- **Medium images** (100 MB - 1 GB): Ensure sufficient RAM
- **Large images** (> 1 GB): Consider using clipping to process smaller areas, or ensure adequate system resources

### Q: How long does processing take?
**A:** Processing time depends on:
- **Image size**: Larger images take longer
- **System specs**: More RAM and CPU cores improve speed
- **Typical times**:
  - Small image (50 MB): 1-2 minutes
  - Medium image (500 MB): 5-10 minutes
  - Large image (2 GB): 30-60+ minutes

### Q: What coordinate systems are supported?
**A:** The module preserves the coordinate system of the input image. Common supported systems include:
- UTM zones
- Geographic (WGS84)
- Any projection supported by GDAL/PROJ

### Q: Can I process multiple images at once?
**A:** Currently, the module processes one image at a time. For batch processing, you can create a script that calls the module multiple times:
```bash
for image in data/*.tif; do
    python -m src.main auto --image="$image"
done
```

### Q: What happens if my image has clouds or no-data areas?
**A:** The module automatically handles:
- **No-data values**: Properly masked and excluded from calculations
- **Invalid pixels**: Filtered out during index calculation
- **Result**: Output indices will have appropriate no-data values in these areas

## Output and Results

### Q: What format are the output files?
**A:** All output files are saved as GeoTIFF (.tif) format with:
- Same coordinate system as input
- Same pixel size and extent (unless clipped)
- Single band containing the calculated index values
- Proper no-data value handling

### Q: What do the index values mean?
**A:** Index value ranges and interpretation:
- **NDVI**: -1 to +1
  - < 0: Water, snow, clouds
  - 0 to 0.3: Bare soil, rocks
  - 0.3 to 0.7: Vegetation (higher = healthier/denser)
- **NDRE**: -1 to +1 (similar to NDVI but using red edge)
- **SAVI**: Similar to NDVI but adjusted for soil background

### Q: Can I open the results in GIS software?
**A:** Yes, the GeoTIFF output files can be opened in:
- QGIS (free, open-source)
- ArcGIS
- Google Earth Engine
- Any GIS software supporting GeoTIFF format

### Q: How do I visualize the results?
**A:** You can:
1. **Use GIS software** for interactive visualization
2. **Python visualization**:
   ```python
   import rasterio
   import matplotlib.pyplot as plt
   
   with rasterio.open('results/indices/ndvi_result.tif') as src:
       ndvi = src.read(1)
   
   plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
   plt.colorbar(label='NDVI')
   plt.show()
   ```

## Logging and Compliance

### Q: Why does the module create log files?
**A:** Log files are required for ISO 42001 compliance and provide:
- **Audit trail**: Complete record of processing activities
- **Troubleshooting**: Detailed information for problem diagnosis
- **Compliance**: Meeting artificial intelligence management system standards
- **Quality assurance**: Verification of processing parameters and results

### Q: Where are log files stored?
**A:** Logs are stored in `results/logs/`:
- **Main logs**: `pascal_ndvi_YYYYMMDD_HHMMSS.log`
- **Backups**: `backup/pascal_ndvi_*_backup.log`
- **Integrity checks**: `*.sha256` files for verification

### Q: What information is logged?
**A:** Each log entry includes:
- Precise timestamp
- User information (from .env file)
- Processing parameters
- Input/output file paths
- Error messages (if any)
- Processing duration
- System information

### Q: How long are logs kept?
**A:** Logs are automatically managed:
- **Current logs**: Kept indefinitely
- **Backup logs**: Compressed and archived
- **Cleanup**: Manual cleanup of old logs may be needed for disk space management

### Q: Can I disable logging?
**A:** No, logging cannot be disabled as it's required for ISO 42001 compliance. However, you can adjust the verbosity level in the `.env` file:
- `LOG_LEVEL=ERROR`: Only errors
- `LOG_LEVEL=WARNING`: Warnings and errors
- `LOG_LEVEL=INFO`: General information (recommended)
- `LOG_LEVEL=DEBUG`: Detailed debugging information

## Troubleshooting

### Q: What should I do if I get a "file not found" error?
**A:** Check these common issues:
1. Verify the file path is correct
2. Ensure the file exists and is readable
3. Use absolute paths if relative paths don't work
4. Check file permissions

### Q: Why am I getting memory errors?
**A:** Memory errors typically occur with large images:
1. **Close other applications** to free RAM
2. **Use clipping** to process smaller areas
3. **Upgrade system memory** if possible
4. **Process during off-peak hours** when more memory is available

### Q: The processing seems stuck. What should I do?
**A:** If processing appears to hang:
1. **Check log files** for the latest activity
2. **Monitor system resources** (CPU, memory usage)
3. **Wait longer** - large images can take considerable time
4. **Restart if necessary** and try with a smaller image or clipped area

### Q: Where can I get help?
**A:** Support resources:
1. **Documentation**: Check the `docs/` folder
2. **Troubleshooting guide**: `docs/user_guide/troubleshooting.md`
3. **GitHub issues**: For internal users, create an issue in the repository
4. **Development team**: Contact AustralMetrics SpA development team for urgent issues

## Advanced Usage

### Q: Can I integrate this module into my own Python scripts?
**A:** Yes, you can import and use the module components:
```python
from src.indices import calculate_indices
from src.preprocessor import clip_image

# Your custom processing logic here
```

### Q: Is there an API or web service version?
**A:** Currently, only the command-line interface is available. API development may be considered for future versions.

### Q: Can I modify the index calculation formulas?
**A:** The current version uses standard formulas for vegetation indices. Modifications would require editing the source code in `src/indices.py`, but this may affect ISO 42001 compliance and validation.

### Q: How do I update to newer versions?
**A:** To update:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```
Check the changelog for any breaking changes or new requirements.

## Compliance and Quality

### Q: What does ISO 42001 compliance mean for users?
**A:** ISO 42001 compliance ensures:
- **Reliability**: Consistent and reproducible results
- **Traceability**: Complete audit trail of all operations
- **Quality**: Rigorous testing and documentation standards
- **Transparency**: Clear documentation of methods and limitations

### Q: How do I verify the integrity of results?
**A:** Verification methods include:
1. **Log file review**: Check processing logs for errors or warnings
2. **Visual inspection**: Review output images for expected patterns
3. **Statistical analysis**: Check index value distributions
4. **Hash verification**: Use SHA-256 hashes for log file integrity

### Q: Can I use this for commercial projects?
**A:** This software is proprietary to AustralMetrics SpA. Usage rights depend on your relationship with the company and applicable licensing agreements. Contact the development team for licensing questions.

## Performance and Optimization

### Q: How can I speed up processing?
**A:** Optimization strategies:
1. **Use SSD storage** for input/output files
2. **Ensure adequate RAM** (8GB+ recommended)
3. **Close unnecessary applications** during processing
4. **Use clipping** to process only areas of interest
5. **Process during off-peak hours** for better system performance

### Q: Does the module support parallel processing?
**A:** The current version processes images sequentially. Parallel processing may be added in future versions based on user feedback and requirements.

### Q: What's the maximum image size I can process?
**A:** Maximum size depends on available system resources:
- **RAM**: At least 4x the uncompressed image size
- **Disk space**: At least 3x the input image size for temporary files and outputs
- **Practical limits**: Successfully tested with images up to 10GB on appropriate hardware

For additional questions not covered here, please refer to the troubleshooting guide or contact the development team.