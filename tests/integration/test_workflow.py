import subprocess
import sys
import shutil
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin


# ------------------------------------------------------------------ #
# Generar un TIFF sintético 6-bandas de 2×2 píxeles                 #
# ------------------------------------------------------------------ #
def create_multiband_tif_for_workflow(path: Path) -> None:
    """
    Crea un TIFF de 6 bandas, 2×2 píxeles, con valores distintos
    en cada píxel para asegurar que K-Means pueda generar ≥2 clusters.
    """
    # Construimos un arreglo 6×2×2 con valores 0…23
    data = np.arange(6 * 2 * 2, dtype=np.float32).reshape(6, 2, 2)

    transform = from_origin(0, 2, 1, 1)  # (west, north, xsize, ysize)
    meta = {
        "driver": "GTiff",
        "height": 2,
        "width": 2,
        "count": 6,
        "dtype": "float32",
        "crs": "EPSG:32719",
        "transform": transform,
    }

    # Pasamos la ruta como str() y mode="w" para evitar advertencias de stub
    with rasterio.open(str(path), mode="w", **meta) as dst:
        for i in range(6):
            dst.write(data[i], i + 1)


# ------------------------------------------------------------------ #
# Repo temporal con setup.py mínimo                                  #
# ------------------------------------------------------------------ #
@pytest.fixture
def git_root(tmp_path):
    """
    Replica la estructura mínima necesaria para que
    `python -m pascal_zoning.pipeline run …` funcione aislado.
    """
    project_dir = tmp_path / "integration_proj"
    project_dir.mkdir()

    # Copiamos src/pascal_zoning a integration_proj/src/pascal_zoning
    src_original = Path(__file__).parents[2] / "src" / "pascal_zoning"
    dst_src = project_dir / "src" / "pascal_zoning"
    dst_src.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_original, dst_src)

    # Creamos un setup.py mínimo para que `python -m pascal_zoning.pipeline` funcione
    (project_dir / "setup.py").write_text(
        "from setuptools import setup, find_packages\n"
        "setup(\n"
        "    name='pascal_zoning',\n"
        "    version='0.1',\n"
        "    packages=find_packages('src'),\n"
        "    package_dir={'': 'src'},\n"
        ")\n"
    )

    return project_dir


# ------------------------------------------------------------------ #
# TEST de flujo completo                                               #
# ------------------------------------------------------------------ #
def test_cli_workflow_creates_outputs(git_root, tmp_path):
    """
    Invoca la CLI real (`python -m pascal_zoning.pipeline run …`) con un TIFF pequeño.
    Comprueba que el proceso termine sin error y que aparezcan los archivos esperados.
    """
    # 1) Crear carpeta `inputs` y el TIFF sintético
    inputs_dir = git_root / "inputs"
    inputs_dir.mkdir()
    tif_path = inputs_dir / "predio_recortado_multiband.tif"
    create_multiband_tif_for_workflow(tif_path)

    # 2) Definir directorio de salida
    outputs_dir = tmp_path / "integration_outputs"

    # 3) Construir el comando CLI con la firma actual:
    # pascal_zoning.pipeline run \
    #   --raster … --indices … \
    #   --output-dir … --force-k … --min-zone-size …
    cmd = [
        sys.executable,
        "-m",
        "pascal_zoning.pipeline",
        "run",
        "--raster",
        str(tif_path),
        "--output-dir",
        str(outputs_dir),
        "--indices",
        "NDVI,NDWI,NDRE,SI",
        "--force-k",
        "2",
        "--min-zone-size",
        "0.00005",
    ]

    proc = subprocess.run(
        cmd,
        cwd=str(git_root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Si el código de retorno no es 0, mostramos stderr para depurar
    assert proc.returncode == 0, f"CLI devolvió error:\n{proc.stderr}"

    # 4) “outputs_dir” contendrá subdirectorios timestamped como:
    #    outputs/20250604_193139_k2_mz0.00005/
    # Capturamos el primer (y único) directorio creado allí:
    timestamped_dirs = [d for d in outputs_dir.iterdir() if d.is_dir()]
    assert timestamped_dirs, "No se creó ningún subdirectorio dentro de outputs_dir"
    exec_dir = timestamped_dirs[0]

    # 5) Comprobamos los nombres reales de los archivos dentro de ese subdir
    expected = {
        "zonificacion_agricola.gpkg",
        "puntos_muestreo.gpkg",
        "mapa_clusters.png",
        "estadisticas_zonas.csv",
        "metricas_clustering.json",
        "zonificacion_results.png",
    }
    produced = {p.name for p in exec_dir.iterdir() if p.is_file()}
    missing = expected - produced
    assert not missing, f"Faltan archivos en {exec_dir}: {missing}"
