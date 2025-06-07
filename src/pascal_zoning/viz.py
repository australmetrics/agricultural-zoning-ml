"""Rutinas de visualización centralizadas para zonificación agronómica."""

# Importaciones de la librería estándar
from pathlib import Path
import typing
import collections.abc

# Importaciones de terceros
import matplotlib.pyplot as plt
import matplotlib
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, LinearRing
from loguru import logger

# Configurar backend no interactivo antes de crear figuras
matplotlib.use("Agg")


def zoning_overview(
    zones: gpd.GeoDataFrame,
    samples: gpd.GeoDataFrame,
    out_png: Path,
) -> None:
    """Dibuja dos paneles: mapa de zonas con muestras superpuestas y área por zona.

    Asegura que cada barra del gráfico de áreas use el mismo color de la zona
    correspondiente en el mapa de polígonos. Guarda la imagen resultante en
    `out_png`.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Fondo blanco para la figura y cada eje
    fig.patch.set_facecolor("white")
    for ax in axes:
        ax.set_facecolor("white")

    # PANEL 1: Mapa de zonas + muestras
    if not zones.empty:
        bounds = zones.total_bounds  # [xmin, ymin, xmax, ymax]
        margin = 0.05
        dx = bounds[2] - bounds[0]
        dy = bounds[3] - bounds[1]

        # Eliminar bordes y recuadros del eje
        for spine in ["top", "right", "bottom", "left"]:
            axes[0].spines[spine].set_visible(False)

        # Número de zonas (clusters)
        n_zonas = len(zones)

        # Paleta discreta "tab10"
        base_cmap = plt.get_cmap("tab10")
        colores = [base_cmap(i) for i in range(n_zonas)]

        # Dibujar cada zona manualmente usando esos colores
        for idx, row in zones.iterrows():
            cluster_id = int(row["cluster"])
            color_poly = colores[cluster_id]

            poly = row.geometry
            if isinstance(poly, MultiPolygon):
                for parte in typing.cast(collections.abc.Iterable[Polygon], poly.geoms):
                    exterior_geom: LinearRing = parte.exterior
                    x_poly, y_poly = exterior_geom.xy
                    axes[0].fill(
                        x_poly,
                        y_poly,
                        facecolor=color_poly,
                        edgecolor="black",
                        linewidth=0.5,
                    )
                    # Dibujar agujeros si hubiera
                    for hole in parte.interiors:
                        x_h, y_h = hole.xy
                        axes[0].fill(x_h, y_h, facecolor="white")
            elif isinstance(poly, Polygon):
                exterior_geom: LinearRing = poly.exterior
                x_poly, y_poly = exterior_geom.xy
                axes[0].fill(
                    x_poly,
                    y_poly,
                    facecolor=color_poly,
                    edgecolor="black",
                    linewidth=0.5,
                )
                for hole in list(poly.interiors):
                    x_h, y_h = hole.xy
                    axes[0].fill(x_h, y_h, facecolor="white")

        # Plotear contorno total (línea exterior)
        boundary = gpd.GeoDataFrame(geometry=[zones.unary_union], crs=zones.crs)
        boundary.boundary.plot(ax=axes[0], color="black", linewidth=1)

        # Ajustar límites con un pequeño margen
        axes[0].set_xlim(bounds[0] - margin * dx, bounds[2] + margin * dx)
        axes[0].set_ylim(bounds[1] - margin * dy, bounds[3] + margin * dy)

        # Eliminar ejes y grilla
        axes[0].set_xticks([])
        axes[0].set_yticks([])
        axes[0].grid(False)

    # Superponer puntos de muestreo en negro
    if not samples.empty:
        samples.plot(ax=axes[0], color="black", markersize=5)

    axes[0].set_title("Zonificación agronómica.")

    # PANEL 2: Barplot de áreas por zona
    if not zones.empty:
        # Asegurarnos de que exista la columna "area_ha"
        if "area_ha" not in zones.columns:
            zones["area_ha"] = zones.geometry.area / 10000.0

        # Ordenamos por cluster para que los colores coincidan en orden
        zones_sorted = zones.sort_values("cluster").reset_index(drop=True)
        cluster_ids = zones_sorted["cluster"].tolist()
        areas_ha = zones_sorted["area_ha"].tolist()

        # Paleta "tab10" para generar colores en orden
        base_cmap = plt.get_cmap("tab10")
        colores = [base_cmap(i) for i in cluster_ids]

        # Dibujar las barras con colores correspondientes
        axes[1].bar(cluster_ids, areas_ha, color=colores, edgecolor="black")

        axes[1].set_xticks(cluster_ids)
        axes[1].set_xticklabels([str(cid) for cid in cluster_ids])
        axes[1].set_xlabel("Zona")
        axes[1].set_ylabel("Área (ha)")
        axes[1].set_title("Área por zona.")

    plt.tight_layout()
    plt.savefig(
        out_png,
        dpi=250,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
        pad_inches=0,
    )
    plt.close(fig)
    logger.info(f"Visualización guardada en {out_png}.")
