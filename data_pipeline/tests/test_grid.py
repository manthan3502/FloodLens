import geopandas as gpd
import pytest
from shapely.geometry import box

from data_pipeline.processing.grid import make_grid


def test_grid_preserves_exact_boundary_weights():
    villages = gpd.GeoDataFrame(
        {"id": ["a", "b"], "geometry": [box(0, 0, 125, 250), box(125, 0, 250, 250)]},
        crs=32643,
    )
    grid, parts = make_grid(villages)
    assert len(grid) == 1
    assert grid.iloc[0].village_id == "a"  # stable ID tie-break
    assert parts.area_m2.sum() == 62500
    assert sorted(parts.area_m2) == [31250, 31250]


def test_grid_rejects_degrees_for_metre_spacing():
    with pytest.raises(ValueError, match="EPSG:32643"):
        make_grid(
            gpd.GeoDataFrame({"id": ["a"], "geometry": [box(74, 16, 75, 17)]}, crs=4326)
        )
