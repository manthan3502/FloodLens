import geopandas as gpd
import pytest
from shapely.geometry import Point

from data_pipeline.validation import validate_geometry


def test_invalid_coordinates_and_duplicate_geometry_rejected():
    for shapes in [[Point(0, 0)], [Point(74.2, 16.7), Point(74.2, 16.7)]]:
        frame = gpd.GeoDataFrame(
            {"id": list(range(len(shapes))), "geometry": shapes}, crs=4326
        ).to_crs(32643)
        with pytest.raises(ValueError):
            validate_geometry(frame)


def test_crs_roundtrip_preserves_location():
    frame = gpd.GeoDataFrame({"id": ["a"], "geometry": [Point(74.2, 16.7)]}, crs=4326)
    validate_geometry(frame.to_crs(32643))
    back = frame.to_crs(32643).to_crs(4326).geometry.iloc[0]
    assert back.distance(frame.geometry.iloc[0]) < 1e-8
