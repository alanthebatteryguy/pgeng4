from typing import Any
from ..models.materials import Concrete, PTStrand, Rebar
from ..models.project import Geometry


def concrete_unit_price(fc: int) -> float:
    base = 220
    if fc <= 8_500:
        add = (fc - 5_000) // 700 * 10
    else:
        add = 50 + (fc - 8_500) // 1_200 * 18
    return base + add


def cost_of(geom: Geometry, conc: Concrete, strand: PTStrand, rebar: Rebar, state: Any) -> float:
    slab_area = geom.span_x * geom.span_y
    vol_slab = slab_area * state.slab_thick / 12 / 27
    wt_rebar = state.rho * state.slab_thick / 12 * slab_area * 490  # 490 lb/ft^3 steel
    concrete_cost = vol_slab * concrete_unit_price(state.fc)
    rebar_cost = wt_rebar * rebar.unit_cost
    # PT weight per area approximate
    pt_wt = slab_area * strand.A * state.P_avg / strand.fpy
    pt_cost = pt_wt * strand.unit_cost
    return concrete_cost + rebar_cost + pt_cost
