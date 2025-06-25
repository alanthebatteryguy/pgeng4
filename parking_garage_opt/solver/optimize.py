from concurrent.futures import ProcessPoolExecutor
from heapq import nsmallest
from .grid_generator import coarse_mesh, fine_mesh
from .scorer import evaluate_candidate, ScoredDesign
from ..models.design_state import DesignState
from ..models.project import Geometry
from ..models.materials import Concrete, PTStrand, Rebar


def optimise(project: Geometry, base_state: DesignState, materials: tuple) -> list[ScoredDesign]:
    grid = list(coarse_mesh(base_state))
    with ProcessPoolExecutor() as ex:
        survivors = list(filter(None, ex.map(lambda s: evaluate_candidate(s, project, materials), grid)))
    top = nsmallest(5, survivors, key=lambda d: d.cost)
    refined = []
    for cand in top:
        refined.extend(fine_mesh(cand.state))
    with ProcessPoolExecutor() as ex:
        finals = list(filter(None, ex.map(lambda s: evaluate_candidate(s, project, materials), refined)))
    return sorted(finals, key=lambda d: d.cost)
