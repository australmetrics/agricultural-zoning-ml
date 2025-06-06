# Especificación de Interfaz con PASCAL NDVI Block

## Visión General

Este documento especifica la interfaz entre el PASCAL NDVI Block y el PASCAL Zoning ML Block, siguiendo las especificaciones ISO 42001 para interoperabilidad entre bloques de software.

## Estructura de Archivos

### Directorio de Outputs

```
outputs/
├── manifest.json       # Metadatos y configuración
├── ndvi.tif           # Índice NDVI (requerido)
├── ndre.tif           # Índice NDRE (opcional)
├── savi.tif           # Índice SAVI (opcional)
└── {otros}.tif        # Otros índices adicionales
```

### Manifest Schema

El archivo `manifest.json` debe seguir el schema definido en `schemas/ndvi_block_output.schema.json`. Ejemplo:

```json
{
    "version": "1.0.3",
    "timestamp": "2025-05-29T10:30:00Z",
    "input_image": {
        "path": "/path/to/original.tif",
        "bands": {
            "RED": 1,
            "NIR": 2
        },
        "crs": "EPSG:4326",
        "transform": [0.0001, 0.0, -70.0, 0.0, -0.0001, -33.0]
    },
    "indices": {
        "ndvi": "outputs/ndvi.tif",
        "ndre": "outputs/ndre.tif",
        "savi": "outputs/savi.tif"
    },
    "metadata": {
        "processing_time": 12.5,
        "software_version": "1.0.3"
    }
}
```

## Formatos y Requerimientos

### GeoTIFF Índices

- **Formato**: GeoTIFF
- **Tipo de Datos**: Float32
- **Rango de Valores**: [-1.0, 1.0]
- **NoData**: -9999
- **Compresión**: LZW (recomendado)
- **CRS**: Debe coincidir con la imagen original

### manifest.json

- **Versión**: Debe ser ≥1.0.3
- **Timestamp**: ISO 8601 UTC
- **CRS**: Debe ser un código EPSG válido
- **Transform**: Matriz de 6 elementos (affine transform)

## Validación

El PASCAL Zoning ML Block incluye validación automática de:

1. Existencia y estructura del manifest.json
2. Validación contra schema JSON
3. Existencia de archivos de índices referenciados
4. Consistencia de CRS entre índices
5. Rangos de valores válidos

## Manejo de Errores

El bloque generará errores descriptivos cuando:

1. No encuentre manifest.json
2. El manifest.json no valide contra el schema
3. Falten índices requeridos (NDVI)
4. Los índices tengan CRS inconsistentes
5. Los valores estén fuera de rango

## Logging y Trazabilidad

Siguiendo ISO 42001, se registran:

1. Timestamp de inicio/fin
2. Versiones de software
3. Validaciones realizadas
4. Errores encontrados
5. Métricas de procesamiento

## Soporte de Versiones

- **PASCAL NDVI Block**: ≥1.0.3
- **Schemas**: 2025.1
- **manifest.json**: v1

## Referencias

- [PASCAL NDVI Block Documentation](https://github.com/australmetrics/pascal-ndvi-block)
- [ISO 42001 Compliance](../compliance/iso42001_compliance.md)
- [API Documentation](api_documentation.md)
