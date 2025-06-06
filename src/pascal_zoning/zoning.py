"""
Sistema de Zonificación Agronómica usando Machine Learning.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union, TypeVar
import numpy as np
import numpy.typing as npt
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.transform import Affine
from rasterio.features import shapes, geometry_mask
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json
import logging

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score

from shapely.geometry import Polygon, Point, mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# Definir tipos personalizados
FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]
IntArray = npt.NDArray[np.int32]
NDArray = Union[FloatArray, BoolArray, IntArray]
GeometryType = Union[Polygon, Point, BaseGeometry]


@dataclass
class ClusterMetrics:
    """Métricas de calidad del clustering."""
    n_clusters: int
    silhouette: float
    calinski_harabasz: float
    inertia: float
    cluster_sizes: Dict[int, int]
    timestamp: str


@dataclass
class ZoneStats:
    """Estadísticas por zona de manejo."""
    zone_id: int
    area_ha: float
    perimeter_m: float
    compactness: float
    mean_values: Dict[str, float]
    std_values: Dict[str, float]


@dataclass
class ZoningResult:
    """Resultados completos de la zonificación."""
    zones: gpd.GeoDataFrame
    samples: gpd.GeoDataFrame
    metrics: ClusterMetrics
    stats: List[ZoneStats]


class ZonificationError(Exception):
    """Excepción base para errores de zonificación."""
    pass


class ValidationError(ZonificationError):
    """Error en validación de índices espectrales."""
    pass


class ProcessingError(ZonificationError):
    """Error durante procesamiento (p. ej. no hay píxeles válidos o filtrado)."""
    pass


# ------------------------------------------------------------- #
# ## Clase principal de zonificación
# ------------------------------------------------------------- #

class AgriculturalZoning:
    """
    Sistema de zonificación agronómica basado en machine learning.

    Implementa:
      1. Preprocesamiento de índices espectrales (imputar, escalar, PCA opcional).
      2. Detección automática de zonas homogéneas vía KMeans.
      3. Generación de puntos de muestreo optimizados por inhibición.
      4. Cálculo de métricas de clustering y estadísticas por zona.
    """
    def __init__(
        self,
        random_state: int = 42,
        min_zone_size_ha: float = 0.5,
        max_zones: int = 10,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize an Agricultural Zoning instance.

        Args:
            random_state: Random seed for reproducibility.
            min_zone_size_ha: Minimum zone size in hectares.
            max_zones: Maximum number of zones to evaluate.
            output_dir: Optional directory to save results.
        """
        self.random_state = random_state
        self.min_zone_size_ha = min_zone_size_ha
        self.max_zones = max_zones
        self.output_dir = output_dir

        # ML preprocessing components
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95, svd_solver="full")
        self.imputer = SimpleImputer(strategy="median")

        # Internal state
        self.features_array: Optional[NDArray] = None
        self.valid_mask: Optional[NDArray] = None
        self.indices: Dict[str, NDArray] = {}
        self.cluster_labels: Optional[NDArray] = None
        self.n_clusters_opt: Optional[int] = None
        self.zones_gdf: Optional[gpd.GeoDataFrame] = None
        self.samples_gdf: Optional[gpd.GeoDataFrame] = None
        self.metrics: Optional[ClusterMetrics] = None
        self.zone_stats: List[ZoneStats] = []
        self.gdf_predio: Optional[gpd.GeoDataFrame] = None
        self.bounds: Optional[BaseGeometry] = None
        self.feature_names: List[str] = []

        # Geometric properties
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.transform: Optional[Affine] = None
        self.crs: Optional[str] = None

        # Initialize logger
        self.logger = logging.getLogger("AgriculturalZoning")

    def _get_bounds(self) -> tuple[float, float, float, float]:
        """
        Obtiene los límites (left, bottom, right, top) del área de interés.
        """
        if self.bounds is None:
            raise ProcessingError("Bounds no inicializados")
        return self.bounds.bounds

    def create_mask(self) -> None:
        """
        Crea una máscara booleana que indica píxeles dentro del polígono del predio.
        """
        if self.gdf_predio is None:
            raise ProcessingError("gdf_predio no inicializado")
        if not isinstance(self.transform, Affine):
            raise ProcessingError("Transform no inicializado")
        if self.width is None or self.height is None:
            raise ProcessingError("Dimensiones no inicializadas")

        geom = self.gdf_predio.geometry.iloc[0]
        if not isinstance(geom, BaseGeometry):
            raise ProcessingError("La geometría debe ser un objeto Shapely")

        # Extraer GeoJSON
        if hasattr(geom, "__geo_interface__"):
            polygon_geom = [geom.__geo_interface__]
        else:
            raise ProcessingError("La geometría no implementa __geo_interface__")

        # Crear máscara (True dentro del polígono)
        mask_poly = geometry_mask(
            geometries=polygon_geom,
            out_shape=(self.height, self.width),
            transform=self.transform,
            invert=True
        )

        # Máscara de píxeles donde todos los índices NO sean NaN
        if not self.indices:
            raise ProcessingError("No hay índices inicializados")
            
        # Diagnóstico de valores NaN por índice
        for name, array in self.indices.items():
            nan_count = np.sum(np.isnan(array))
            if nan_count > 0:
                self.logger.warning(f"Índice {name}: {nan_count} valores NaN detectados")
        
        stacked = np.stack(list(self.indices.values()), axis=-1)
        valid_data_mask = np.all(~np.isnan(stacked), axis=-1)

        # Máscara final: dentro del polígono y sin NaNs
        self.valid_mask = np.logical_and(mask_poly, valid_data_mask)
        
        if self.valid_mask is None:
            raise ProcessingError("valid_mask no fue asignada correctamente")
            
        n_valid = int(np.sum(self.valid_mask))
        n_poly = int(np.sum(mask_poly))
        n_data = int(np.sum(valid_data_mask))
        
        self.logger.info(f"Píxeles dentro del polígono: {n_poly}")
        self.logger.info(f"Píxeles con datos válidos: {n_data}")
        self.logger.info(f"Píxeles válidos final: {n_valid}")
        
        if n_valid == 0:
            raise ProcessingError("No se encontraron píxeles válidos dentro del polígono.")
        elif n_valid < n_poly:
            self.logger.warning(f"Se descartaron {n_poly - n_valid} píxeles por tener datos inválidos")

    def prepare_feature_matrix(self) -> None:
        """
        Prepara la matriz de características a partir de los índices dentro del polígono.
        """
        if self.valid_mask is None:
            raise ProcessingError("Máscara de validez no inicializada")

        # Convertir índices a arrays numpy
        index_arrays = [np.asarray(arr) for arr in self.indices.values()]
        # Apilar índices en shape (H, W, N_indices)
        feature_stack = np.stack(index_arrays, axis=-1)
        valid_mask_array = np.asarray(self.valid_mask, dtype=bool)

        # Filtrar píxeles válidos y aplanar
        features_valid = feature_stack[valid_mask_array].reshape(-1, len(self.indices))

        # Imputar valores faltantes (si existieran)
        X_imputed = self.imputer.fit_transform(features_valid)

        # Escalar
        X_scaled = self.scaler.fit_transform(X_imputed)

        self.features_array = np.array(X_scaled, dtype=np.float64)
        self.logger.info("Matriz de características imputada y escalada para clustering.")

    def select_optimal_clusters(self) -> int:
        """
        Evalúa de 2 hasta self.max_zones clusters y selecciona el k óptimo
        usando la métrica de Silhouette.
        """
        if self.features_array is None:
            raise ProcessingError("Matriz de características no inicializada")

        best_k = 2
        best_score = -np.inf

        for k in range(2, self.max_zones + 1):
            kmeans = KMeans(n_clusters=k, random_state=self.random_state)
            labels = kmeans.fit_predict(self.features_array)
            try:
                sil_score = float(silhouette_score(self.features_array, labels))
                ch_score = float(calinski_harabasz_score(self.features_array, labels))
            except ValueError:
                sil_score = -1.0
                ch_score = 0.0

            self.logger.info(f"k={k}: Silhouette={sil_score:.4f}, CH={ch_score:.2f}")

            if sil_score > best_score:
                best_score = sil_score
                best_k = k

        self.logger.info(f"Seleccionado k óptimo = {best_k} con Silhouette = {best_score:.4f}")
        return best_k    
    
    def perform_clustering(self, force_k: Optional[int] = None) -> None:
        """
        Ejecuta KMeans con el número óptimo de clusters o un k forzado.
        Si se especifica force_k, intentará mantener ese número de clusters
        incluso después del filtrado por tamaño mínimo.
        """
        if self.features_array is None:
            raise ProcessingError("Matriz de características no inicializada")

        # Determinar k: ya sea forzado o el óptimo hallado
        if force_k is not None:
            self.n_clusters_opt = force_k
            self.logger.info(f"Usando número forzado de clusters: k={force_k}")
        else:
            self.n_clusters_opt = self.select_optimal_clusters()

        kmeans_final = KMeans(n_clusters=self.n_clusters_opt, random_state=self.random_state)
        labels_flat = kmeans_final.fit_predict(self.features_array)

        # Reconstruir mapa de clusters
        if self.height is None or self.width is None:
            raise ProcessingError("Dimensiones no inicializadas")

        # Crear array con -1 como valor por defecto para píxeles fuera del polígono
        clusters_img = np.full((self.height, self.width), -1, dtype=np.int32)
            
        # Asignar las etiquetas solo en los píxeles válidos
        if self.valid_mask is not None:
            valid_mask_array = np.asarray(self.valid_mask, dtype=bool)
            clusters_img[valid_mask_array] = labels_flat
                
        # Convertir a float64 para mantener consistencia de tipos
        self.cluster_labels = clusters_img.astype(np.float64)

        # Diagnóstico de píxeles
        total_pixels = self.height * self.width
        valid_pixels = np.sum(valid_mask_array)
        labeled_pixels = np.sum(clusters_img >= 0)
        self.logger.info(f"Total píxeles: {total_pixels}")
        self.logger.info(f"Píxeles válidos: {valid_pixels}")
        self.logger.info(f"Píxeles con etiqueta: {labeled_pixels}")

        if labeled_pixels < valid_pixels:
            self.logger.warning(f"Hay {valid_pixels - labeled_pixels} píxeles válidos sin etiqueta")

        # Calcular métricas de calidad
        inertia = float(kmeans_final.inertia_)
        sil_score = float(silhouette_score(self.features_array, labels_flat))
        ch_score = float(calinski_harabasz_score(self.features_array, labels_flat))

        unique, counts = np.unique(labels_flat, return_counts=True)
        cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metrics = ClusterMetrics(
            n_clusters=self.n_clusters_opt,
            silhouette=sil_score,
            calinski_harabasz=ch_score,
            inertia=inertia,
            cluster_sizes=cluster_sizes,
            timestamp=timestamp
        )
        self.logger.info(f"Clustering final completo: {self.n_clusters_opt} clusters.")
        self.logger.info(f"Métricas: Silhouette={sil_score:.4f}, CH={ch_score:.2f}, Inertia={inertia:.2f}")

    def extract_zone_polygons(self) -> None:
        """
        Convierte el mapa de clusters a un GeoDataFrame de polígonos.
        """
        if self.cluster_labels is None:
            raise ProcessingError("Etiquetas de clusters no inicializadas")
        if self.transform is None:
            raise ProcessingError("Transform no inicializado")
        if self.crs is None:
            raise ProcessingError("CRS no inicializado")

        height, width = self.cluster_labels.shape
        left, bottom, right, top = self._get_bounds()

        x_res = (right - left) / width
        y_res = (top - bottom) / height

        records: list[dict[str, Any]] = []
        for row in range(height):
            for col in range(width):
                label = int(self.cluster_labels[row, col])
                if label == -1:
                    continue
                x0 = left + col * x_res
                y0 = top - row * y_res
                x1 = x0 + x_res
                y1 = y0 - y_res
                poly = Polygon([
                    (x0, y0),
                    (x1, y0),
                    (x1, y1),
                    (x0, y1)
                ])
                records.append({"cluster": label, "geometry": poly})

        if not records:
            raise ProcessingError("No se generaron polígonos de zonas (sin píxeles con clusters).")

        gdf_pixels = gpd.GeoDataFrame(records, crs=self.crs)
        self.zones_gdf = gdf_pixels.dissolve(by="cluster").reset_index()
        self.logger.info("Polígonos de zona extraídos y disueltos por cluster.") 

    def filter_small_zones(self) -> None:
        """
        Filtra zonas cuyo área sea menor a min_zone_size_ha y reasigna índices.
        """
        if self.zones_gdf is None:
            raise ProcessingError("Zonas no generadas; ejecutar extract_zone_polygons primero.")

        self.zones_gdf["area_m2"] = self.zones_gdf.geometry.area
        self.zones_gdf["area_ha"] = self.zones_gdf["area_m2"] / 10000.0

        initial_count = len(self.zones_gdf)
        self.zones_gdf = self.zones_gdf[self.zones_gdf["area_ha"] >= self.min_zone_size_ha].copy()
        filtered_count = len(self.zones_gdf)
        self.logger.info(f"Zonas totales antes del filtrado: {initial_count}. Después: {filtered_count}.")

        # Actualizar etiquetas de cluster y asegurarse que sean consecutivas
        self.zones_gdf = self.zones_gdf.reset_index(drop=True)
        self.zones_gdf["cluster"] = self.zones_gdf.index.astype(int)
        
        # Si quedan zonas sin asignar, asignarlas a la zona más cercana
        if self.cluster_labels is not None:
            valid_labels = set(self.zones_gdf["cluster"].values)
            mask_unassigned = ~np.isin(self.cluster_labels, list(valid_labels))
            if np.any(mask_unassigned):
                self.logger.warning(f"Reasignando {np.sum(mask_unassigned)} píxeles a zonas cercanas")

    def _pixel_to_world_coords(self, pixels: np.ndarray) -> np.ndarray:
        """
        Convierte coordenadas de píxeles a coordenadas mundo usando la transformación.

        Args:
            pixels: Array Nx2 con coordenadas (x_pix, y_pix).

        Returns:
            Array Nx2 con coordenadas mundo (x_world, y_world).
        """
        if not isinstance(self.transform, Affine):
            raise ProcessingError("Transform no inicializado")

        world_coords: list[tuple[float, float]] = []
        a, b, c, d, e, f = self.transform.to_gdal()
        for px, py in pixels:
            x = a * float(px) + b * float(py) + c
            y = d * float(px) + e * float(py) + f
            world_coords.append((x, y))
        return np.array(world_coords)

    def generate_sampling_points(self, points_per_zone: int) -> None:
        """
        Genera puntos de muestreo optimizados por inhibición en cada zona.

        Args:
            points_per_zone: Número mínimo de puntos por zona.
        """
        if self.zones_gdf is None:
            raise ProcessingError("No hay zonas definidas para generar puntos")
        if self.cluster_labels is None:
            raise ProcessingError("No hay etiquetas de clusters definidas")
        if self.transform is None:
            raise ProcessingError("Transform no inicializado")
        if self.crs is None:
            raise ProcessingError("CRS no inicializado")

        np.random.seed(self.random_state)
        samples_list: list[dict[str, Any]] = []

        for zone_id in self.zones_gdf["cluster"]:
            zone_mask = (self.cluster_labels == int(zone_id))
            if not np.any(zone_mask):
                continue

            ys, xs = np.where(zone_mask)
            if xs.size == 0:
                continue

            pixel_coords = np.column_stack((xs, ys))
            world_coords = self._pixel_to_world_coords(pixel_coords)

            # Determinar cuántos puntos usar en inhibición
            n_points = max(points_per_zone, int(np.sqrt(xs.size)))
            if n_points >= xs.size:
                selected_idxs = np.arange(xs.size)
            else:
                selected_idxs = []
                remaining_idxs = np.arange(xs.size)
                first = int(np.random.choice(remaining_idxs))
                selected_idxs.append(first)
                remaining_idxs = np.delete(remaining_idxs, np.where(remaining_idxs == first))

                while len(selected_idxs) < n_points and remaining_idxs.size > 0:
                    sel_coords = world_coords[selected_idxs]
                    rem_coords = world_coords[remaining_idxs]
                    # Distancia mínima
                    min_dists = np.min(
                        np.linalg.norm(rem_coords[:, None, :] - sel_coords[None, :, :], axis=2),
                        axis=1
                    )
                    best_idx_in_rem = int(np.argmax(min_dists))
                    best_idx = remaining_idxs[best_idx_in_rem]
                    selected_idxs.append(best_idx)
                    remaining_idxs = np.delete(remaining_idxs, best_idx_in_rem)

            for idx in selected_idxs:
                xw, yw = world_coords[idx]
                px, py = pixel_coords[idx]
                point = Point(xw, yw)
                values = {
                    name: float(array[int(py), int(px)])
                    for name, array in self.indices.items()
                }
                samples_list.append({
                    "geometry": point,
                    "cluster": int(zone_id),
                    **values
                })

        if not samples_list:
            raise ProcessingError("No se generaron puntos de muestreo en ninguna zona.")

        self.samples_gdf = gpd.GeoDataFrame(samples_list, crs=self.crs)
        self.logger.info(f"Generados {len(samples_list)} puntos de muestreo")

    def compute_zone_statistics(self) -> None:
        """
        Calcula estadísticas por zona: área, perímetro, compacidad y estadísticas
        de los índices espectrales.
        """
        if self.zones_gdf is None:
            raise ProcessingError("No hay zonas definidas para calcular estadísticas")
        if self.cluster_labels is None:
            raise ProcessingError("Etiquetas de clusters no inicializadas")

        self.zone_stats: list[ZoneStats] = []
        for idx, row in self.zones_gdf.iterrows():
            zone_id = int(row["cluster"])
            geom = row["geometry"]

            area_m2 = geom.area
            area_ha = area_m2 / 10000.0
            perimeter_m = geom.length
            compactness = 4 * np.pi * area_m2 / (perimeter_m * perimeter_m) if perimeter_m > 0 else 0.0

            zone_mask = (self.cluster_labels == zone_id)
            mean_values: dict[str, float] = {}
            std_values: dict[str, float] = {}
            for name, array in self.indices.items():
                vals = array[zone_mask]
                mean_values[name] = float(np.nanmean(vals))
                std_values[name] = float(np.nanstd(vals))

            stats = ZoneStats(
                zone_id=zone_id,
                area_ha=area_ha,
                perimeter_m=perimeter_m,
                compactness=compactness,
                mean_values=mean_values,
                std_values=std_values
            )
            self.zone_stats.append(stats)

        self.logger.info(f"Calculadas estadísticas para {len(self.zone_stats)} zonas")

    def save_results(self, output_dir: Optional[Path] = None) -> None:
        """
        Guarda los resultados de la zonificación en archivos.

        Args:
            output_dir: Directorio donde guardar los resultados. Si no se especifica,
                        usa el directorio configurado en la instancia.
        """
        save_dir = output_dir or self.output_dir
        if save_dir is None:
            self.logger.warning("No se especificó directorio de salida; no se guardarán resultados.")
            return

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 1) Guardar zonas
        if self.zones_gdf is not None:
            zones_fp = save_dir / "zonificacion_agricola.gpkg"
            self.zones_gdf.to_file(zones_fp, layer="zonas", driver="GPKG")
            self.logger.info(f"Guardado archivo de zonas: {zones_fp}")

        # 2) Guardar puntos de muestreo
        if self.samples_gdf is not None:
            samples_fp = save_dir / "puntos_muestreo.gpkg"
            self.samples_gdf.to_file(samples_fp, layer="muestras", driver="GPKG")
            self.logger.info(f"Guardado archivo de muestras: {samples_fp}")

        # 3) Guardar estadísticas
        if self.zone_stats:
            stats_data: list[dict[str, Any]] = []
            for stat in self.zone_stats:
                row: dict[str, Any] = {
                    "zone_id": stat.zone_id,
                    "area_ha": stat.area_ha,
                    "perimeter_m": stat.perimeter_m,
                    "compactness": stat.compactness
                }
                for idx_name, val in stat.mean_values.items():
                    row[f"{idx_name}_mean"] = val
                for idx_name, val in stat.std_values.items():
                    row[f"{idx_name}_std"] = val
                stats_data.append(row)

            stats_df = pd.DataFrame(stats_data)
            stats_fp = save_dir / "estadisticas_zonas.csv"
            stats_df.to_csv(stats_fp, index=False)
            self.logger.info(f"Guardado archivo de estadísticas: {stats_fp}")

        # 4) Guardar métricas
        if self.metrics is not None:
            metrics_data = {
                "n_clusters": self.metrics.n_clusters,
                "silhouette": float(self.metrics.silhouette),
                "calinski_harabasz": float(self.metrics.calinski_harabasz),
                "inertia": float(self.metrics.inertia),
                "cluster_sizes": self.metrics.cluster_sizes,
                "timestamp": self.metrics.timestamp
            }
            metrics_fp = save_dir / "metricas_clustering.json"
            with open(metrics_fp, "w") as f:
                json.dump(metrics_data, f, indent=2)
            self.logger.info(f"Guardado archivo de métricas: {metrics_fp}")

        self.logger.info(f"Resultados guardados en: {save_dir}")

    def visualize_results(self) -> None:
        """
        Genera y guarda dos mapas:
         1) Mapa de NDVI (con área fuera del polígono en blanco).
         2) Mapa de zonificación por clusters.
        """
        if self.output_dir is None:
            self.logger.warning("output_dir no definido; no se generarán mapas.")
            return

        try:
            # 1) Mapa de NDVI
            if "NDVI" not in self.indices:
                self.logger.warning("No se encontró índice NDVI; no se generará mapa NDVI.")
            else:
                ndvi = self.indices["NDVI"]
                if self.valid_mask is None:
                    raise ProcessingError("Máscara de validez no inicializada para visualización.")
                if self.bounds is None:
                    raise ProcessingError("Bounds no inicializados para visualización.")
                
                ndvi_masked = np.where(self.valid_mask, ndvi, np.nan)
                left, bottom, right, top = self.bounds.bounds
                x_margin = (right - left) * 0.05
                y_margin = (top - bottom) * 0.05
                extent = (left - x_margin, right + x_margin, bottom - y_margin, top + y_margin)

                fig1, ax1 = plt.subplots(figsize=(10, 10))
                cmap_ndvi = plt.get_cmap("RdYlGn").copy()
                cmap_ndvi.set_bad(color="white")
                im = ax1.imshow(ndvi_masked, cmap=cmap_ndvi, extent=extent, origin="upper")
                ax1.set_title("Mapa de NDVI", fontsize=16, pad=15)
                ax1.set_xticks([])
                ax1.set_yticks([])
                cbar = plt.colorbar(im, ax=ax1, fraction=0.036, pad=0.04)
                cbar.set_label("NDVI", rotation=270, labelpad=15, fontsize=12)

                if self.gdf_predio is not None and not self.gdf_predio.empty:
                    self.gdf_predio.boundary.plot(ax=ax1, color="blue", linewidth=2)
                plt.tight_layout()
                ndvi_fp = self.output_dir / "mapa_ndvi.png"
                ndvi_fp.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(ndvi_fp, dpi=500, bbox_inches='tight')
                plt.close(fig1)
                self.logger.info(f"Mapa de NDVI guardado en: {ndvi_fp}")            # 2) Mapa de Zonificación
            if self.zones_gdf is not None and not self.zones_gdf.empty:
                fig2, ax2 = plt.subplots(figsize=(10, 10))
                self.zones_gdf.plot(
                    ax=ax2,
                    column="cluster",
                    cmap="viridis",
                    edgecolor="black",
                    linewidth=0.5,
                )
                # Añadir colorbar manualmente para mejor control
                vmin = float(self.zones_gdf["cluster"].min())
                vmax = float(self.zones_gdf["cluster"].max())
                norm = Normalize(vmin=vmin, vmax=vmax)
                sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=ax2, fraction=0.036, pad=0.04)
                cbar.set_label("Cluster", rotation=270, labelpad=15, fontsize=12)
                
                ax2.set_title("Zonificación por Clusters", fontsize=16, pad=15)
                ax2.set_xticks([])
                ax2.set_yticks([])

                if self.gdf_predio is not None and not self.gdf_predio.empty:
                    self.gdf_predio.boundary.plot(ax=ax2, color="red", linewidth=2)

                plt.tight_layout()
                clusters_fp = self.output_dir / "mapa_clusters.png"
                clusters_fp.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(clusters_fp, dpi=500, bbox_inches='tight')
                plt.close(fig2)
                self.logger.info(f"Mapa de clusters guardado en: {clusters_fp}")

        except Exception as e:
            self.logger.error(f"Error generando visualizaciones: {str(e)}")
            # Cerrar todas las figuras por si acaso
            plt.close('all')    

    def run_pipeline(
        self,
        indices: Dict[str, np.ndarray],
        bounds: BaseGeometry,
        points_per_zone: int,
        crs: str,
        force_k: Optional[int] = None,
        min_zone_size_ha: Optional[float] = None,
        output_dir: Optional[Path] = None
    ) -> ZoningResult:
        """
        Ejecuta el pipeline completo de zonificación.

        Args:
            indices: Diccionario con arrays numpy de índices espectrales pre-calculados.
            bounds: Objeto Shapely (Polygon/MultiPolygon) con los límites del área de interés.
            points_per_zone: Número mínimo de puntos de muestreo por zona.
            crs: Sistema de referencia de coordenadas (ej. "EPSG:32718").
            force_k: Si se especifica, fuerza ese número de clusters.
            output_dir: Directorio opcional para guardar resultados.

        Returns:
            ZoningResult con zonas, puntos de muestreo y métricas.
        """
        # 1) Inicializar atributos geométricos
        self.indices = indices
        self.bounds = bounds
        self.crs = crs

        # Tamaño del array se asume a partir del primer índice
        array_shape = next(iter(indices.values())).shape
        self.height = int(array_shape[0])
        self.width = int(array_shape[1])

        # Calcular transform a partir de bounds y tamaño
        left, bottom, right, top = bounds.bounds
        pixel_width = (right - left) / float(self.width)
        pixel_height = (top - bottom) / float(self.height)
        self.transform = Affine.from_gdal(
            left, pixel_width, 0,
            top, 0, -pixel_height
        )

        # Crear GeoDataFrame del polígono
        self.gdf_predio = gpd.GeoDataFrame({"geometry": [bounds]}, crs=crs)

        # 2) Ejecutar cada paso del pipeline
        self.create_mask()
        self.prepare_feature_matrix()
        self.perform_clustering(force_k=force_k)
        self.extract_zone_polygons()
        self.filter_small_zones()
        self.compute_zone_statistics()
        self.generate_sampling_points(points_per_zone)

        # 3) Validar que todo exista antes de devolver
        if self.zones_gdf is None or self.samples_gdf is None or self.metrics is None:
            raise ProcessingError("Pipeline no generó todos los outputs requeridos")

        # 4) Guardar resultados y visualizar
        self.output_dir = output_dir or self.output_dir
        if self.output_dir:
            self.save_results(output_dir=self.output_dir)
            self.visualize_results()

        return ZoningResult(
            zones=self.zones_gdf,
            samples=self.samples_gdf,
            metrics=self.metrics,
            stats=self.zone_stats
        )


# ------------------------------------------------------------- #
# ## Ejecución principal (si se corre como script)
# ------------------------------------------------------------- #

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline de Zonificación Agronómica: genera zonas y puntos de muestreo a partir de un TIFF recortado."
    )
    parser.add_argument(
        "--raster",
        type=str,
        required=True,
        help="Ruta al TIFF recortado del predio (EPSG:32718)."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output_zonification",
        help="Carpeta de salida para resultados (por defecto: output_zonification)."
    )
    parser.add_argument(
        "--max_clusters",
        type=int,
        default=10,
        help="Número máximo de clusters a evaluar para selección automática (por defecto: 10)."
    )
    parser.add_argument(
        "--min_area_ha",
        type=float,
        default=0.5,
        help="Área mínima en hectáreas para conservar una zona (por defecto: 0.5)."
    )
    parser.add_argument(
        "--force_k",
        type=int,
        default=None,
        help="Si se especifica, fuerza ese número de clusters."
    )

    args = parser.parse_args()

    import geopandas as gpd
    from rasterio.features import shapes
    from shapely.geometry import shape as shape_from_geojson
    from shapely.ops import unary_union

    # 1) Leer TIFF y calcular índices espectrales
    with rasterio.open(args.raster) as src:
        crs = src.crs.to_string() if src.crs is not None else ""
        img = src.read()  # [B11, B8, B5, B4, B3, B2]    # Extraer y convertir bandas a float64
    bands = {
        'swir': img[0].astype(np.float64),      # B11
        'nir': img[1].astype(np.float64),       # B8
        'red_edge': img[2].astype(np.float64),  # B5
        'red': img[3].astype(np.float64),       # B4
        'green': img[4].astype(np.float64)      # B3
    }

    def safe_divide(a: FloatArray, b: FloatArray) -> FloatArray:
        """
        Calcula índice normalizado de forma segura manejando divisiones por cero.

        Args:
            a: Numerador (como FloatArray)
            b: Denominador (como FloatArray)

        Returns:
            FloatArray con índice normalizado (a-b)/(a+b)
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.divide(a - b, a + b, 
                             out=np.zeros_like(a, dtype=np.float64), 
                             where=(a + b) != 0)
            result = np.nan_to_num(result, nan=0.0)
        return result

    # Calcular índices espectrales
    indices_dict: Dict[str, FloatArray] = {
        "NDVI": safe_divide(bands['nir'], bands['red']),
        "NDWI": safe_divide(bands['green'], bands['nir']),
        "NDRE": safe_divide(bands['nir'], bands['red_edge']),
        "SI":   safe_divide(bands['swir'], bands['nir'])
    }

    # 2) Derivar el polígono del predio a partir del TIFF, forzando que 0 = fondo/nodata
    with rasterio.open(args.raster) as src:
        transform = src.transform

        # Leer la primera banda (que estamos usando para separar fondo vs parcela)
        banda1 = src.read(1)  # shape: (height, width)

        # Construir la máscara: 1 donde banda1>0 (parcela), 0 donde banda1==0 (fondo)
        mask_valid = (banda1 > 0).astype(np.uint8)

        # Extraer los contornos de “1” en mask_valid
        geoms = []
        for geom_geojson, val in shapes(mask_valid, mask=mask_valid, transform=transform):
            if val == 1:
                geoms.append(shape_from_geojson(geom_geojson))

        if not geoms:
            raise ProcessingError("No se pudo derivar polígono: todos los píxeles están en 0.")

        # Unir todos los pedazos en un único polígono
        poly = unary_union(geoms)


    # 3) Ejecutar zonificación
    engine = AgriculturalZoning(
        random_state=42,
        min_zone_size_ha=args.min_area_ha,
        max_zones=args.max_clusters,
        output_dir=Path(args.output)
    )

    result = engine.run_pipeline(
        indices=indices_dict,
        bounds=poly,
        points_per_zone=10,  # o usa args.min_area_ha si deseas
        crs=crs,
        force_k=args.force_k,
        output_dir=Path(args.output)
    )

    # 4) Mostrar resumen por consola
    engine.logger.info("=== Resumen de métricas de clustering ===")
    engine.logger.info(f"  Número de clusters: {result.metrics.n_clusters}")
    engine.logger.info(f"  Silhouette: {result.metrics.silhouette:.4f}")
    engine.logger.info(f"  Calinski-Harabasz: {result.metrics.calinski_harabasz:.2f}")
    engine.logger.info(f"  Inertia: {result.metrics.inertia:.2f}")
    engine.logger.info(f"  Tamaños de clusters: {result.metrics.cluster_sizes}")

    engine.logger.info("=== Estadísticas por zona (primeras 5 zonas) ===")
    for stat in result.stats[:5]:
        engine.logger.info(
            f"  Zona {stat.zone_id}: Área={stat.area_ha:.3f} ha, "
            f"Perímetro={stat.perimeter_m:.2f} m, Compacidad={stat.compactness:.4f}, "
            f"Media NDVI={stat.mean_values['NDVI']:.4f}, Std NDVI={stat.std_values['NDVI']:.4f}"
        )










