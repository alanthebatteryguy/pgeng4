import pytest

from parking_garage_opt.models.geometry import Geometry
from parking_garage_opt.solver.grid_generator import generate_geometries


def test_fixed_slab_thickness():
    base = Geometry(span_x=30, span_y=30, slab_thick=8.0, max_beam_depth=20.0)
    variants = list(generate_geometries(base, False))
    assert len(variants) == 1
    assert variants[0].slab_thick == 8.0


def test_variable_slab_thickness():
    base = Geometry(span_x=30, span_y=30, slab_thick=8.0, max_beam_depth=20.0)
    variants = list(
        generate_geometries(base, True, slab_thickness_range=[7.0, 8.0, 9.0])
    )
    assert [g.slab_thick for g in variants] == [7.0, 8.0, 9.0]


def test_missing_range_error():
    base = Geometry(span_x=30, span_y=30, slab_thick=8.0, max_beam_depth=20.0)
    with pytest.raises(ValueError):
        list(generate_geometries(base, True))
