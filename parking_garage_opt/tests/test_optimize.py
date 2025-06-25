from parking_garage_opt.models.geometry import Geometry
from parking_garage_opt.solver.optimize import optimise


def test_optimise_fixed():
    geom = Geometry(span_x=25, span_y=25, slab_thick=7.5, max_beam_depth=18)
    result = optimise(geom, False)
    assert len(result) == 1
    assert result[0].slab_thick == 7.5


def test_optimise_variable():
    geom = Geometry(span_x=25, span_y=25, slab_thick=7.5, max_beam_depth=18)
    result = optimise(geom, True, slab_thickness_range=[6.5, 7.5])
    assert [g.slab_thick for g in result] == [6.5, 7.5]
