"""Sistema de zonificación agronómica basado en Machine Learning."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
import rasterio
from matplotlib.colors import Normalize
from rasterio.features import geometry_mask, shapes
from rasterio.transform import Affine
from shapely.geometry import Polygon, Point, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    calinski_harabasz_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

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
    """Error durante procesamiento (p. ej. no hay píxeles válidos)."""

    pass


class AgriculturalZoning:
    """Sistema de zonificación agronómica basado en ML.

    Implementa:
      1. Preprocesamiento de índices (imputar, escalar, PCA opcional).
      2. Detección de zonas homogéneas vía KMeans.
      3. Generación de puntos de muestreo por inhibición.
      4. Cálculo de métricas de clustering y estadísticas por zona.
    """

    def __init__(
        self,
        random_state: int = 42,
        min_zone_size_ha: float = 0.5,
        max_zones: int = 10,
        output_dir: Optional[Path] = None,
    ) -> None:
        """Inicializa el sistema con parámetros de clustering y salida.

        Args:
            random_state: Semilla para reproducibilidad.
            min_zone_size_ha: Tamaño mínimo de zona en hectáreas.
            max_zones: Número máximo de zonas a evaluar.
            output_dir: Directorio opcional para resultados.
        """
        self.random_state = random_state
        self.min_zone_size_ha = min_zone_size_ha
        self.max_zones = max_zones
        self.output_dir = output_dir

        # Componentes de preprocesamiento ML
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95, svd_solver="full")
        self.imputer = SimpleImputer(strategy="median")

        # Estado interno
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

        # Propiedades geométricas
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.transform: Optional[Affine] = None
        self.crs: Optional[str] = None

        # Logger
        self.logger = logging.getLogger("AgriculturalZoning")

    def _get_bounds(self) -> tuple[float, float, float, float]:
        """Obtiene límites (left, bottom, right, top) de los bounds."""
        if self.bounds is None:
            raise ProcessingError("Bounds no inicializados.")
        return self.bounds.bounds

    def create_mask(self) -> None:
        """Crea máscara booleana que indica píxeles dentro del polígono."""
        if self.gdf_predio is None:
            raise ProcessingError("gdf_predio no inicializado.")
        if not isinstance(self.transform, Affine):
            raise ProcessingError("Transform no inicializado.")
        if self.width is None or self.height is None:
            raise ProcessingError("Dimensiones no inicializadas.")

        geom = self.gdf_predio.geometry.iloc[0]
        if not isinstance(geom, BaseGeometry):
            raise ProcessingError("La geometría debe ser un objeto Shapely.")

        if hasattr(geom, "__geo_interface__"):
            polygon_geom = [geom.__geo_interface__]
        else:
            raise ProcessingError("La geometría no implementa __geo_interface__.")

        mask_poly = geometry_mask(
            geometries=polygon_geom,
            out_shape=(self.height, self.width),
            transform=self.transform,
            invert=True,
        )

        if not self.indices:
            raise ProcessingError("No hay índices inicializados.")

        for name, array in self.indices.items():
            nan_count = int(np.sum(np.isnan(array)))
            if nan_count > 0:
                self.logger.warning(
                    f"Índice {name}: {nan_count} valores NaN detectados."  # noqa: E501
                )

        stacked = np.stack(list(self.indices.values()), axis=-1)
        valid_data_mask = np.all(~np.isnan(stacked), axis=-1)

        self.valid_mask = np.logical_and(mask_poly, valid_data_mask)
        n_valid = int(np.sum(cast(np.ndarray, self.valid_mask)))
        n_poly = int(np.sum(mask_poly))
        n_data = int(np.sum(valid_data_mask))

        self.logger.info(f"Píxeles dentro del polígono: {n_poly}.")
        self.logger.info(f"Píxeles con datos válidos: {n_data}.")
        self.logger.info(f"Píxeles válidos final: {n_valid}.")

        if n_valid == 0:
            raise ProcessingError(
                "No se encontraron píxeles válidos dentro del polígono."
            )
        if n_valid < n_poly:
            self.logger.warning(
                f"Se descartaron {n_poly - n_valid} píxeles por datos inválidos."
            )

    def prepare_feature_matrix(self) -> None:
        """Prepara la matriz de características a partir de los índices."""
        if self.valid_mask is None:
            raise ProcessingError("Máscara de validez no inicializada.")

        index_arrays = [np.asarray(arr) for arr in self.indices.values()]
        feature_stack = np.stack(index_arrays, axis=-1)
        valid_mask_array = np.asarray(self.valid_mask, dtype=bool)
        features_valid = feature_stack[valid_mask_array].reshape(-1, len(self.indices))

        X_imputed = self.imputer.fit_transform(features_valid)
        X_scaled = self.scaler.fit_transform(X_imputed)
        self.features_array = np.array(X_scaled, dtype=np.float64)

        self.logger.info(
            "Matriz de características imputada y escalada para clustering."
        )

    def select_optimal_clusters(self) -> int:
        """Evalúa k=2…max_zones y retorna k óptimo según Silhouette."""
        if self.features_array is None:
            raise ProcessingError("Matriz de características no inicializada.")

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

            self.logger.info(
                f"k={k}: Silhouette={sil_score:.4f}, " f"CH={ch_score:.2f}."
            )

            if sil_score > best_score:
                best_score = sil_score
                best_k = k

        self.logger.info(
            f"Seleccionado k óptimo = {best_k} con Silhouette = " f"{best_score:.4f}."
        )
        return best_k

    def perform_clustering(self, force_k: Optional[int] = None) -> None:
        """Ejecuta KMeans con k óptimo o forzado y guarda métricas."""
        if self.features_array is None:
            raise ProcessingError("Matriz de características no inicializada.")

        if force_k is not None:
            self.n_clusters_opt = force_k
            self.logger.info(f"Usando número forzado de clusters: k={force_k}.")
        else:
            self.n_clusters_opt = self.select_optimal_clusters()

        kmeans_final = KMeans(
            n_clusters=self.n_clusters_opt,
            random_state=self.random_state,
        )
        labels_flat = kmeans_final.fit_predict(self.features_array)

        if self.height is None or self.width is None:
            raise ProcessingError("Dimensiones no inicializadas.")

        clusters_img = np.full((self.height, self.width), -1, dtype=np.int32)

        valid_mask_array = np.asarray(self.valid_mask, dtype=bool)
        clusters_img[valid_mask_array] = labels_flat

        self.cluster_labels = clusters_img.astype(np.float64)
        total_pixels = self.height * self.width
        valid_pixels = int(np.sum(valid_mask_array))
        labeled_pixels = int(np.sum(clusters_img >= 0))

        self.logger.info(f"Total píxeles: {total_pixels}.")
        self.logger.info(f"Píxeles válidos: {valid_pixels}.")
        self.logger.info(f"Píxeles con etiqueta: {labeled_pixels}.")

        if labeled_pixels < valid_pixels:
            self.logger.warning(
                f"Hay {valid_pixels - labeled_pixels} " "píxeles válidos sin etiqueta."
            )

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
            timestamp=timestamp,
        )
        self.logger.info(
            "Clustering final completo: " f"{self.n_clusters_opt} clusters."
        )
        self.logger.info(
            f"Métricas: Silhouette={sil_score:.4f}, "
            f"CH={ch_score:.2f}, Inertia={inertia:.2f}."
        )

    def extract_zone_polygons(self) -> None:
        """Convierte el mapa de clusters a GeoDataFrame de polígonos."""
        if self.cluster_labels is None:
            raise ProcessingError("Etiquetas de clusters no inicializadas.")
        if self.transform is None:
            raise ProcessingError("Transform no inicializado.")
        if self.crs is None:
            raise ProcessingError("CRS no inicializado.")

        height, width = self.cluster_labels.shape
        left, bottom, right, top = self._get_bounds()
        x_res = (right - left) / width
        y_res = (top - bottom) / height

        records: List[Dict[str, Any]] = []
        for row in range(height):
            for col in range(width):
                label = int(self.cluster_labels[row, col])
                if label == -1:
                    continue

                x0 = left + col * x_res
                y0 = top - row * y_res
                x1 = x0 + x_res
                y1 = y0 - y_res
                poly = Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
                records.append({"cluster": label, "geometry": poly})

        if not records:
            raise ProcessingError(
                "No se generaron polígonos de zonas " "(sin píxeles con clusters)."
            )

        gdf_pixels = gpd.GeoDataFrame(records, crs=self.crs)
        self.zones_gdf = gdf_pixels.dissolve(by="cluster").reset_index()
        self.logger.info("Polígonos de zona extraídos y disueltos " "por cluster.")

    def filter_small_zones(self) -> None:
        """Filtra zonas con área menor a min_zone_size_ha."""
        if self.zones_gdf is None:
            raise ProcessingError(
                "Zonas no generadas; ejecutar extract_zone_polygons " "primero."
            )

        self.zones_gdf["area_m2"] = self.zones_gdf.geometry.area
        self.zones_gdf["area_ha"] = self.zones_gdf["area_m2"] / 10000.0
        initial_count = len(self.zones_gdf)
        self.zones_gdf = self.zones_gdf[
            self.zones_gdf["area_ha"] >= self.min_zone_size_ha
        ].copy()
        filtered_count = len(self.zones_gdf)
        self.logger.info(
            f"Zonas totales antes del filtrado: {initial_count}. "
            f"Después: {filtered_count}."
        )

        self.zones_gdf = self.zones_gdf.reset_index(drop=True)
        self.zones_gdf["cluster"] = self.zones_gdf.index.astype(int)

        if self.cluster_labels is not None:
            valid_labels = set(self.zones_gdf["cluster"].values)
            mask_unassigned = ~np.isin(self.cluster_labels, list(valid_labels))
            if np.any(mask_unassigned):
                self.logger.warning(
                    f"Reasignando {int(np.sum(mask_unassigned))} "
                    "píxeles a zonas cercanas."
                )

    def _pixel_to_world_coords(self, pixels: np.ndarray) -> np.ndarray:
        """Convierte coordenadas de píxeles a coordenadas de mundo."""
        if not isinstance(self.transform, Affine):
            raise ProcessingError("Transform no inicializado.")

        world_coords: List[tuple[float, float]] = []
        a, b, c, d, e, f = self.transform.to_gdal()
        for px, py in pixels:
            x = a * float(px) + b * float(py) + c
            y = d * float(px) + e * float(py) + f
            world_coords.append((x, y))
        return np.array(world_coords)

    def generate_sampling_points(self, points_per_zone: int) -> None:
        """Genera puntos de muestreo optimizados por inhibición para cada zona."""
        if self.zones_gdf is None:
            raise ProcessingError("No hay zonas definidas.")
        if self.cluster_labels is None:
            raise ProcessingError("No hay etiquetas de clusters.")
        if self.transform is None:
            raise ProcessingError("Transform no inicializado.")
        if self.crs is None:
            raise ProcessingError("CRS no inicializado.")

        np.random.seed(self.random_state)
        samples_list: List[Dict[str, Any]] = []

        for zone_id in self.zones_gdf["cluster"]:
            zone_mask = self.cluster_labels == int(zone_id)
            if not np.any(zone_mask):
                continue

            ys, xs = np.where(zone_mask)
            if xs.size == 0:
                continue

            pixel_coords = np.column_stack((xs, ys))
            world_coords = self._pixel_to_world_coords(pixel_coords)
            n_points = max(points_per_zone, int(np.sqrt(xs.size)))
            if n_points >= xs.size:
                selected_idxs = list(range(xs.size))
            else:
                selected_idxs: List[int] = []
                remaining_idxs = np.arange(xs.size)
                first = int(np.random.choice(remaining_idxs))
                selected_idxs.append(first)
                remaining_idxs = np.delete(
                    remaining_idxs, np.where(remaining_idxs == first)
                )

                while len(selected_idxs) < n_points and remaining_idxs.size > 0:
                    sel_coords = world_coords[selected_idxs]
                    rem_coords = world_coords[remaining_idxs]
                    min_dists = np.min(
                        np.linalg.norm(
                            rem_coords[:, None, :]  # noqa: E231
                            - sel_coords[None, :, :],  # noqa: E231
                            axis=2,
                        ),
                        axis=1,
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
                samples_list.append(
                    {"geometry": point, "cluster": int(zone_id), **values}
                )

        if not samples_list:
            raise ProcessingError("No se generaron puntos de muestreo en ninguna zona.")

        self.samples_gdf = gpd.GeoDataFrame(samples_list, crs=self.crs)
        self.logger.info(f"Generados {len(samples_list)} puntos de muestreo.")

    def compute_zone_statistics(self) -> None:
        """Calcula estadísticas por zona: área, perímetro, compacidad."""
        if self.zones_gdf is None:
            raise ProcessingError("No hay zonas definidas para estadísticas.")
        if self.cluster_labels is None:
            raise ProcessingError("Etiquetas de clusters no inicializadas.")

        self.zone_stats = []
        for idx, row in self.zones_gdf.iterrows():
            zone_id = int(row["cluster"])
            geom = row["geometry"]
            area_m2 = geom.area
            area_ha = area_m2 / 10000.0
            perimeter_m = geom.length
            compactness = (
                4 * np.pi * area_m2 / (perimeter_m**2) if perimeter_m > 0 else 0.0
            )
            mean_values: Dict[str, float] = {}
            std_values: Dict[str, float] = {}
            zone_mask = self.cluster_labels == zone_id
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
                std_values=std_values,
            )
            self.zone_stats.append(stats)

        self.logger.info(f"Calculadas estadísticas para {len(self.zone_stats)} zonas.")

    def save_results(self, output_dir: Optional[Path] = None) -> None:
        """Guarda resultados en archivos: zonas, muestras, estadísticas."""
        save_dir = output_dir or self.output_dir
        if save_dir is None:
            self.logger.warning(
                "No se especificó directorio de salida; " "no se guardarán resultados."
            )
            return

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        if self.zones_gdf is not None:
            zones_fp = save_dir / "zonificacion_agricola.gpkg"
            self.zones_gdf.to_file(zones_fp, layer="zonas", driver="GPKG")
            self.logger.info(f"Guardado archivo de zonas: {zones_fp}.")

        if self.samples_gdf is not None:
            samples_fp = save_dir / "puntos_muestreo.gpkg"
            self.samples_gdf.to_file(samples_fp, layer="muestras", driver="GPKG")
            self.logger.info(f"Guardado archivo de muestras: {samples_fp}.")

        if self.zone_stats:
            stats_data: List[Dict[str, Any]] = []
            for stat in self.zone_stats:
                row: Dict[str, Any] = {
                    "zone_id": stat.zone_id,
                    "area_ha": stat.area_ha,
                    "perimeter_m": stat.perimeter_m,
                    "compactness": stat.compactness,
                }
                for idx_name, val in stat.mean_values.items():
                    row[f"{idx_name}_mean"] = val
                for idx_name, val in stat.std_values.items():
                    row[f"{idx_name}_std"] = val
                stats_data.append(row)

            stats_df = pd.DataFrame(stats_data)
            stats_fp = save_dir / "estadisticas_zonas.csv"
            stats_df.to_csv(stats_fp, index=False)
            self.logger.info(f"Guardado archivo de estadísticas: {stats_fp}.")

        if self.metrics is not None:
            metrics_data = {
                "n_clusters": self.metrics.n_clusters,
                "silhouette": float(self.metrics.silhouette),
                "calinski_harabasz": float(self.metrics.calinski_harabasz),
                "inertia": float(self.metrics.inertia),
                "cluster_sizes": self.metrics.cluster_sizes,
                "timestamp": self.metrics.timestamp,
            }
            metrics_fp = save_dir / "metricas_clustering.json"
            with open(metrics_fp, "w") as f:
                json.dump(metrics_data, f, indent=2)
            self.logger.info(f"Guardado archivo de métricas: {metrics_fp}.")

        self.logger.info(f"Resultados guardados en: {save_dir}.")

    def visualize_results(self) -> None:
        """Genera y salva mapas de NDVI y zonificación por clusters."""
        if self.output_dir is None:
            self.logger.warning("output_dir no definido; no se generarán mapas.")
            return

        try:
            # Mapa de NDVI
            if "NDVI" not in self.indices:
                self.logger.warning("No se encontró índice NDVI; no se generará mapa.")
            else:
                ndvi = self.indices["NDVI"]
                if self.valid_mask is None:
                    raise ProcessingError("Máscara no inicializada para visualización.")
                if self.bounds is None:
                    raise ProcessingError("Bounds no inicializados para visualización.")

                ndvi_masked = np.where(self.valid_mask, ndvi, np.nan)
                left, bottom, right, top = self.bounds.bounds
                x_margin = (right - left) * 0.05
                y_margin = (top - bottom) * 0.05
                extent = (
                    left - x_margin,
                    right + x_margin,
                    bottom - y_margin,
                    top + y_margin,
                )

                fig1, ax1 = plt.subplots(figsize=(10, 10))
                cmap_ndvi = plt.get_cmap("RdYlGn").copy()
                cmap_ndvi.set_bad(color="white")
                im = ax1.imshow(
                    ndvi_masked,
                    cmap=cmap_ndvi,
                    extent=extent,
                    origin="upper",
                )
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
                plt.savefig(ndvi_fp, dpi=500, bbox_inches="tight")
                plt.close(fig1)
                self.logger.info(f"Mapa de NDVI guardado en: {ndvi_fp}.")

            # Mapa de clusters
            if self.zones_gdf is not None and not self.zones_gdf.empty:
                fig2, ax2 = plt.subplots(figsize=(10, 10))
                self.zones_gdf.plot(
                    ax=ax2,
                    column="cluster",
                    cmap="viridis",
                    edgecolor="black",
                    linewidth=0.5,
                )

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
                plt.savefig(clusters_fp, dpi=500, bbox_inches="tight")
                plt.close(fig2)
                self.logger.info(f"Mapa de clusters guardado en: {clusters_fp}.")

        except Exception as e:
            self.logger.error(f"Error generando visualizaciones: {str(e)}.")
            plt.close("all")

    def run_pipeline(
        self,
        indices: Dict[str, np.ndarray],
        bounds: BaseGeometry,
        points_per_zone: int,
        crs: str,
        force_k: Optional[int] = None,
        min_zone_size_ha: Optional[float] = None,
        output_dir: Optional[Path] = None,
    ) -> ZoningResult:
        """Ejecuta pipeline completo de zonificación agronómica.

        Args:
            indices: Diccionario con arrays numpy de índices espectrales.
            bounds: Polígono Shapely del área de interés.
            points_per_zone: Número mínimo de puntos por zona.
            crs: Sistema de referencia (ej. 'EPSG:32718').
            force_k: Forzar número de clusters (opcional).
            output_dir: Directorio opcional para guardar resultados.

        Returns:
            ZoningResult con zonas, puntos y métricas.
        """
        self.indices = indices
        self.bounds = bounds
        self.crs = crs
        array_shape = next(iter(indices.values())).shape
        self.height = int(array_shape[0])
        self.width = int(array_shape[1])

        left, bottom, right, top = bounds.bounds
        pixel_width = (right - left) / float(self.width)
        pixel_height = (top - bottom) / float(self.height)
        self.transform = Affine.from_gdal(left, pixel_width, 0, top, 0, -pixel_height)

        self.gdf_predio = gpd.GeoDataFrame({"geometry": [bounds]}, crs=crs)

        self.create_mask()
        self.prepare_feature_matrix()
        self.perform_clustering(force_k=force_k)
        self.extract_zone_polygons()
        self.filter_small_zones()
        self.compute_zone_statistics()
        self.generate_sampling_points(points_per_zone)

        if self.zones_gdf is None or self.samples_gdf is None or self.metrics is None:
            raise ProcessingError("Pipeline no generó todos los outputs requeridos.")

        self.output_dir = output_dir or self.output_dir
        if self.output_dir:
            self.save_results(output_dir=self.output_dir)
            self.visualize_results()

        return ZoningResult(
            zones=self.zones_gdf,
            samples=self.samples_gdf,
            metrics=self.metrics,
            stats=self.zone_stats,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Pipeline de Zonificación Agronómica: genera zonas y "
            "puntos de muestreo a partir de un TIFF recortado."
        )
    )
    parser.add_argument(
        "--raster",
        type=str,
        required=True,
        help="Ruta al TIFF recortado del predio (EPSG:32718).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output_zonification",
        help=(
            "Carpeta de salida para resultados " "(por defecto: output_zonification)."
        ),
    )
    parser.add_argument(
        "--max_clusters",
        type=int,
        default=10,
        help=("Número máximo de clusters a evaluar " "(por defecto: 10)."),
    )
    parser.add_argument(
        "--min_area_ha",
        type=float,
        default=0.5,
        help=(
            "Área mínima en hectáreas " "para conservar una zona (por defecto: 0.5)."
        ),
    )
    parser.add_argument(
        "--force_k",
        type=int,
        default=None,
        help="Si se especifica, fuerza ese número de clusters.",
    )

    args = parser.parse_args()
    from rasterio.features import shapes as rio_shapes  # noqa: F401
    from shapely.ops import unary_union as shapely_unary_union  # noqa: F401

    with rasterio.open(args.raster) as src:
        crs = src.crs.to_string() if src.crs is not None else ""
        img = src.read()  # [B11, B8, B5, B4, B3, B2]
    bands = {
        "swir": img[0].astype(np.float64),
        "nir": img[1].astype(np.float64),
        "red_edge": img[2].astype(np.float64),
        "red": img[3].astype(np.float64),
        "green": img[4].astype(np.float64),
    }

    def safe_divide(a: FloatArray, b: FloatArray) -> FloatArray:
        """Calcula índice normalizado de forma segura manejando división por cero."""
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.divide(
                a - b,
                a + b,
                out=np.zeros_like(a, dtype=np.float64),
                where=(a + b) != 0,
            )
            result = np.nan_to_num(result, nan=0.0)
        return result

    indices_dict: Dict[str, FloatArray] = {
        "NDVI": safe_divide(bands["nir"], bands["red"]),
        "NDWI": safe_divide(bands["green"], bands["nir"]),
        "NDRE": safe_divide(bands["nir"], bands["red_edge"]),
        "SI": safe_divide(bands["swir"], bands["nir"]),
    }

    with rasterio.open(args.raster) as src:
        transform = src.transform
        banda1 = src.read(1)
        mask_valid = (banda1 > 0).astype(np.uint8)
        geoms = []
        for geom_geojson, val in shapes(
            mask_valid, mask=mask_valid, transform=transform
        ):
            if val == 1:
                geoms.append(shape(geom_geojson))
        if not geoms:
            raise ProcessingError(
                "No se pudo derivar polígono: todos los píxeles están en 0."
            )
        poly = unary_union(geoms)

    engine = AgriculturalZoning(
        random_state=42,
        min_zone_size_ha=args.min_area_ha,
        max_zones=args.max_clusters,
        output_dir=Path(args.output),
    )

    result = engine.run_pipeline(
        indices=indices_dict,
        bounds=poly,
        points_per_zone=10,
        crs=crs,
        force_k=args.force_k,
        output_dir=Path(args.output),
    )

    engine.logger.info("=== Resumen de métricas de clustering ===")
    engine.logger.info(f"  Número de clusters: {result.metrics.n_clusters}")
    engine.logger.info(f"  Silhouette: {result.metrics.silhouette:.4f}")
    engine.logger.info(
        f"  Calinski-Harabasz: " f"{result.metrics.calinski_harabasz:.2f}"
    )
    engine.logger.info(f"  Inertia: {result.metrics.inertia:.2f}")
    engine.logger.info(f"  Tamaños de clusters: " f"{result.metrics.cluster_sizes}")

    engine.logger.info("=== Estadísticas por zona (primeras 5 zonas) ===")
    for stat in result.stats[:5]:
        engine.logger.info(
            f"  Zona {stat.zone_id}: Área={stat.area_ha:.3f} ha, "
            f"Perímetro={stat.perimeter_m:.2f} m, "
            f"Compacidad={stat.compactness:.4f}, "
            f"Media NDVI={stat.mean_values['NDVI']:.4f}, "
            f"Std NDVI={stat.std_values['NDVI']:.4f}"
        )
