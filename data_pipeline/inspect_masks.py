"""Make inspectable SAR proxy maps and village summaries, never accuracy claims."""

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import ListedColormap
from rasterio.plot import plotting_extent

from data_pipeline.feasibility import ROOT


def main():
    villages = gpd.read_file(ROOT / "data/interim/villages-features.gpkg")
    rivers = gpd.read_file(ROOT / "data/interim/osm.gpkg").query("kind == 'river'")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    for column, year in enumerate([2019, 2021]):
        with rasterio.open(ROOT / f"data/interim/flood-{year}.tif") as src:
            mask = src.read(1)
            extent = plotting_extent(src)
        for row in [0, 1]:
            ax = axes[row, column]
            villages.plot(ax=ax, color="#eff3ed", edgecolor="#a7b4aa", linewidth=0.25)
            # Grey is missing SAR; orange is detected change proxy.
            ax.imshow(
                np.ma.masked_where(mask != 255, mask),
                extent=extent,
                cmap=ListedColormap(["#d1d4d7"]),
                alpha=0.65,
                zorder=2,
            )
            ax.imshow(
                np.ma.masked_where(mask != 1, mask),
                extent=extent,
                cmap=ListedColormap(["#dc6229"]),
                interpolation="nearest",
                zorder=3,
            )
            rivers.plot(ax=ax, color="#2c84aa", linewidth=0.5, zorder=4)
            region = villages if row == 0 else villages[villages.tehsil == "Shirol"]
            xmin, ymin, xmax, ymax = region.total_bounds
            ax.set_xlim(xmin - 1000, xmax + 1000)
            ax.set_ylim(ymin - 1000, ymax + 1000)
            ax.set_title(
                f"{year}: {'study area' if row == 0 else 'Shirol, known affected tehsil'}"
            )
            ax.set_aspect("equal")
            ax.tick_params(labelsize=7)
    fig.suptitle(
        "SAR change-detection proxies | orange: detected change · grey: unobserved · blue: OSM rivers\n2021 acquisition: 22 July, before documented 25 July rescue operations; not peak extent or ground-truth validation.",
        fontsize=11,
    )
    path = ROOT / "docs/evidence/m1-sar-inspection.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    grid = gpd.read_file(ROOT / "data/interim/grid-features.gpkg")
    joined = grid.merge(
        villages[["id", "tehsil"]].rename(columns={"id": "village_id"}), on="village_id"
    )
    summary = joined.groupby("tehsil")[
        ["flood_fraction_2019", "flood_fraction_2021"]
    ].agg(["count", "mean", "max"])
    (ROOT / "docs/evidence/m1-sar-tehsils.json").write_text(
        summary.to_json(), encoding="utf-8"
    )
    print(path)
    print(summary)


if __name__ == "__main__":
    main()
