from dataclasses import dataclass
from typing import List

STEEL_DENSITY = 490  # lb/ft^3
STRAND_UNIT_WEIGHT = 0.522  # lb/ft

@dataclass
class Beam:
    bw: float      # in
    depth: float   # in
    length: float  # ft
    tendons: int
    tendon_length: float  # ft per tendon

@dataclass
class Materials:
    rebar_cost: float       # $/lb
    strand_cost: float      # $/lb
    formwork_slab: float    # $/ft^2
    formwork_beam: float    # $/ft^2
    pump_cost: float        # $/yd^3


def concrete_unit_price(fc: int) -> float:
    base = 220
    if fc <= 8_500:
        add = (fc - 5_000) // 700 * 10
    else:
        add = 50 + (fc - 8_500) // 1_200 * 18
    return base + add

@dataclass
class Design:
    fc: int
    slab_area: float  # ft^2
    slab_thick: float  # in
    rho: float
    beams: List[Beam]


def takeoffs(d: Design):
    vol_slab = d.slab_area * d.slab_thick / 12 / 27
    vol_beam = sum(b.bw * b.depth * b.length for b in d.beams) / 12**3 / 27
    wt_rebar = d.rho * 12 * d.slab_thick / 12 * d.slab_area * STEEL_DENSITY
    wt_pt = sum(b.tendons * b.tendon_length for b in d.beams) * STRAND_UNIT_WEIGHT
    form_slab_area = d.slab_area
    form_beam_area = sum((2 * b.depth / 12 + b.bw / 12) * b.length for b in d.beams)
    return vol_slab, vol_beam, wt_rebar, wt_pt, form_slab_area, form_beam_area


def cost_of(d: Design, m: Materials) -> float:
    vol_slab, vol_beam, wt_rebar, wt_pt, a_slab, a_beam = takeoffs(d)
    unit_price = concrete_unit_price(d.fc)
    conc_cost = (vol_slab + vol_beam) * unit_price
    rebar_cost = wt_rebar * m.rebar_cost
    pt_cost = wt_pt * m.strand_cost
    form_cost = a_slab * m.formwork_slab + a_beam * m.formwork_beam
    pump_cost = (vol_slab + vol_beam) * m.pump_cost
    return conc_cost + rebar_cost + pt_cost + form_cost + pump_cost
