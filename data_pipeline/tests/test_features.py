import numpy as np
import pytest
from rasterio.transform import from_origin

from data_pipeline.processing.features import otsu, window_values


def test_otsu_separates_bimodal_change_and_is_deterministic():
    values = np.r_[np.linspace(-9, -7, 100), np.linspace(-1, 1, 900)]
    result = otsu(values)
    assert -7.1 < result < -1
    assert otsu(values) == result


def test_otsu_rejects_empty_or_constant_evidence():
    for values in [[np.nan], [1, 1, 1]]:
        with pytest.raises(ValueError):
            otsu(values)


def test_raster_pixel_centers_are_not_double_counted_at_cell_edges():
    data = np.arange(100).reshape(10, 10)
    transform = from_origin(0, 100, 10, 10)
    left = window_values(data, transform, [0, 0, 50, 100])
    right = window_values(data, transform, [50, 0, 100, 100])
    assert left.size + right.size == data.size
    assert left.sum() + right.sum() == data.sum()
