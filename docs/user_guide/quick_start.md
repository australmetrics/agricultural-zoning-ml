---
title: Quick Start
nav_order: 2
---

# Guía Rápida

## Instalación

```bash
pip install pascal-zoning-ml
```

## Uso con PASCAL NDVI Block

### 1. Generar Índices con PASCAL NDVI Block

Primero, ejecuta el PASCAL NDVI Block para generar los índices espectrales:

```bash
pascal-ndvi process imagen.tif --output indices/
```

Esto generará:
- ndvi.tif
- ndre.tif (opcional)
- savi.tif (opcional)
- manifest.json

© 2025 AustralMetrics SpA. All rights reserved.

Get started with PASCAL NDVI Block in 5 minutes. This guide assumes you have already completed the installation process.

## Prerequisites

- ✅ PASCAL NDVI Block installed and configured
- ✅ Virtual environment activated
- ✅ Sample satellite imagery (Sentinel-2 or Landsat format)

## Your First Analysis

### Step 1: Prepare Your Data

Place your satellite imagery in the `data/` directory:
```bash
# Create data directory if it doesn't exist
mkdir -p data

# Copy your satellite image
cp /path/to/your/image.tif data/
```

**Supported Formats:**
- GeoTIFF (.tif, .tiff)
- Sentinel-2 imagery (L1C/L2A)
- Landsat imagery (Collection 1/2)

### Step 2: Basic Index Calculation

Calculate all vegetation indices with a single command:

```bash
python -m src.main indices --image=data/your_image.tif
```

**What happens:**
- ✅ Automatic band detection
- ✅ NDVI, NDRE, and SAVI calculation
- ✅ Results saved to `results/` directory
- ✅ Processing logs created for ISO 42001 compliance

### Step 3: View Your Results

Results are automatically organized:
```
results/
├── your_image_ndvi.tif    # Normalized Difference Vegetation Index
├── your_image_ndre.tif    # Normalized Difference Red Edge
├── your_image_savi.tif    # Soil Adjusted Vegetation Index
└── logs/
    └── pascal_ndvi_[timestamp].log  # Audit trail
```

## 5-Minute Workflow Examples

### Example 1: Simple Processing

```bash
# Process a Sentinel-2 image
python -m src.main indices --image=data/sentinel2_image.tif

# Check logs for processing details
cat results/logs/pascal_ndvi_*.log | tail -20
```

### Example 2: Processing with Area of Interest

```bash
# Clip image to specific area first
python -m src.main clip --image=data/large_image.tif --shapefile=data/study_area.shp

# Then calculate indices on clipped area
python -m src.main indices --image=results/large_image_clipped.tif
```

### Example 3: Complete Automated Workflow

```bash
# One command for everything: clip + indices
python -m src.main auto --image=data/satellite_image.tif --shapefile=data/boundary.shp --output=results/my_analysis
```

## Understanding the Commands

### Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `indices` | Calculate vegetation indices | `python -m src.main indices --image=data/img.tif` |
| `clip` | Clip imagery to boundary | `python -m src.main clip --image=data/img.tif --shapefile=data/area.shp` |
| `auto` | Complete automated pipeline | `python -m src.main auto --image=data/img.tif` |

### Essential Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--image` | Yes | Input satellite image path | `--image=data/sentinel.tif` |
| `--shapefile` | No | Clipping boundary (optional) | `--shapefile=data/boundary.shp` |
| `--output` | No | Custom output directory | `--output=results/project1` |

## Quick Verification

### Verify Installation
```bash
# Check if module loads correctly
python -m src.main --help

# Should display available commands and options
```

### Test with Sample Data
```bash
# If you have sample data
python -m src.main indices --image=data/sample.tif

# Check if results were created
ls results/
```

## Understanding Output Files

### Vegetation Indices Explained

**NDVI (Normalized Difference Vegetation Index)**
- Range: -1 to +1
- Values > 0.3: Healthy vegetation
- Values < 0.1: No vegetation (water, urban, bare soil)

**NDRE (Normalized Difference Red Edge)**
- Range: -1 to +1
- More sensitive for dense vegetation
- Useful for crop health monitoring

**SAVI (Soil Adjusted Vegetation Index)**
- Range: -1 to +1
- Reduces soil background influence
- Better for sparse vegetation areas

### File Naming Convention
```
[original_filename]_[index].tif
```
Examples:
- `sentinel2_20240515_ndvi.tif`
- `landsat8_field1_ndre.tif`
- `my_image_savi.tif`

## Common Use Cases

### Agricultural Monitoring
```bash
# Process field imagery
python -m src.main auto --image=data/field_sentinel2.tif --shapefile=data/field_boundary.shp

# Results show crop health across the field
```

### Forest Health Assessment
```bash
# Large area processing
python -m src.main indices --image=data/forest_landsat.tif --output=results/forest_analysis

# NDVI values indicate forest density and health
```

### Urban Green Space Analysis
```bash
# City-wide analysis
python -m src.main clip --image=data/city_image.tif --shapefile=data/city_limits.shp
python -m src.main indices --image=results/city_image_clipped.tif
```

## Quality Control Features

### Automatic Logging
Every operation creates detailed logs:
```bash
# View recent processing logs
tail -50 results/logs/pascal_ndvi_*.log
```

### Integrity Verification
```bash
# Check file integrity (SHA-256 hashes)
cat results/logs/*.sha256
```

### Error Handling
The system automatically handles common issues:
- Missing bands
- Projection mismatches
- Invalid pixel values
- Memory limitations

## Next Steps

Now that you've completed your first analysis:

1. **Explore Advanced Features**: See `docs/examples/advanced_examples.md`
2. **Understand the Architecture**: Review `docs/technical/architecture_overview.md`
3. **Customize Processing**: Check `docs/technical/api_documentation.md`
4. **Troubleshoot Issues**: Refer to `docs/user_guide/troubleshooting.md`

## Performance Tips

### For Large Files
```bash
# Process in smaller chunks or use specific output location
python -m src.main indices --image=data/large_image.tif --output=/fast_drive/results
```

### For Multiple Images
```bash
# Use shell loops for batch processing
for img in data/*.tif; do
    python -m src.main indices --image="$img"
done
```

### Memory Optimization
- Process one image at a time
- Use clipping for large scenes
- Monitor system resources during processing

## Getting Help

### Built-in Help
```bash
# General help
python -m src.main --help

# Command-specific help
python -m src.main indices --help
python -m src.main clip --help
python -m src.main auto --help
```

### Log Analysis
```bash
# Search for errors in logs
grep "ERROR" results/logs/*.log

# View processing summary
grep "Processing complete" results/logs/*.log
```

---

**Congratulations!** You've successfully processed your first satellite imagery with PASCAL NDVI Block. The system has automatically documented your analysis in compliance with ISO 42001 standards for full traceability and audit capability.

## Uso con PASCAL Zoning

### 1. Ejecutar Zonificación

Usando Python:

```python
from pascal_zoning import AgriculturalZoning
from pathlib import Path

# Configurar rutas
ndvi_dir = Path("indices")  # Directorio con outputs del NDVI Block
output_dir = Path("zonificacion")

# Ejecutar zonificación
zoning = AgriculturalZoning()
results = zoning.run_pipeline(
    ndvi_block_output_dir=ndvi_dir,
    output_dir=output_dir,
    points_per_zone=10,  # Puntos de muestreo por zona
    min_distance=50.0    # Distancia mínima entre puntos (metros)
)
```

O usando la línea de comandos:

```bash
pascal-zoning zonificar indices/ --output zonificacion/ --puntos-por-zona 10 --distancia-min 50
```

### 2. Resultados

El proceso generará:

1. **zonificacion_agricola.gpkg**: Polígonos de zonas de manejo
   - Incluye: ID de zona, área en hectáreas, geometría

2. **puntos_muestreo.gpkg**: Puntos de muestreo estratificados
   - Incluye: ID de zona, coordenadas

3. **zonificacion_results.png**: Visualización de resultados
   - Mapa de zonas
   - Gráfico de áreas

### 3. Verificación de Resultados

```python
import geopandas as gpd

# Cargar resultados
zones = gpd.read_file("zonificacion/zonificacion_agricola.gpkg")
samples = gpd.read_file("zonificacion/puntos_muestreo.gpkg")

# Imprimir estadísticas
print(f"Número de zonas: {len(zones)}")
print(f"Área total: {zones.area_ha.sum():.1f} ha")
print(f"Puntos de muestreo: {len(samples)}")
```

## Siguientes Pasos

- [Documentación Técnica Detallada](../technical/technical_documentation.md)
- [Ejemplos Avanzados](../examples/advanced_examples.md)
- [Guía de Usuario Completa](user_guide.md)