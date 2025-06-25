from itertools import product
from typing import Iterable
from ..models.design_state import DesignState


def coarse_mesh(base: DesignState, n_fc: int = 3) -> Iterable[DesignState]:
    fc_values = [base.fc + i * 700 for i in range(n_fc)]
    P_values = [base.P_avg + i * 100 for i in range(n_fc)]
    rho_values = [base.rho + i * 0.002 for i in range(n_fc)]
    for fc, P, rho in product(fc_values, P_values, rho_values):
        yield DesignState(fc=fc, P_avg=P, rho=rho, slab_thick=base.slab_thick, beam_depth=base.beam_depth)


def fine_mesh(state: DesignState) -> Iterable[DesignState]:
    fc_values = [state.fc + i * 100 for i in range(-1, 2)]
    P_values = [state.P_avg + i * 25 for i in range(-1, 2)]
    rho_values = [state.rho + i * 0.0005 for i in range(-1, 2)]
    for fc, P, rho in product(fc_values, P_values, rho_values):
        yield DesignState(fc=fc, P_avg=P, rho=rho, slab_thick=state.slab_thick, beam_depth=state.beam_depth)
