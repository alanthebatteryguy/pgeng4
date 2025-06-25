from dataclasses import dataclass
from typing import Optional
from ..models.design_state import DesignState
from ..models.project import Geometry
from ..models.materials import Concrete, PTStrand, Rebar
from .checks import run_checks
from .cost import cost_of

@dataclass
class ScoredDesign:
    state: DesignState
    cost: float
    checks: dict


def evaluate_candidate(state: DesignState, geom: Geometry, materials: tuple, user_override: Optional[dict] = None) -> Optional[ScoredDesign]:
    conc, strand, rebar = materials
    checkres = run_checks(state, geom, user_override)
    if not (checkres.service_comp and checkres.service_tension and checkres.spacing):
        return None
    cost = cost_of(geom, conc, strand, rebar, state)
    return ScoredDesign(state=state, cost=cost, checks=checkres.__dict__)
