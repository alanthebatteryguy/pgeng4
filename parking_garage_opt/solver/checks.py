"""Structural check functions per ACI 318-19 and PTI."""
from dataclasses import dataclass
from .props import strength_dependent_props
from ..models.design_state import DesignState
from ..models.project import Geometry

@dataclass
class CheckResult:
    service_comp: bool
    service_tension: bool
    spacing: bool


def run_checks(state: DesignState, geom: Geometry, user_override: dict | None = None) -> CheckResult:
    props = strength_dependent_props(state.fc, user_override)
    # Service compression check (approx):
    comp_ok = state.P_avg < 0.45 * state.fc
    # Tensile stress check using modulus of rupture
    tension_ok = state.P_avg > -props["fr"]
    # Constructability: tendon spacing <= 8h
    spacing_ok = props["s_max"](state.slab_thick) >= geom.span_x  # simplistic
    return CheckResult(service_comp=comp_ok, service_tension=tension_ok, spacing=spacing_ok)
