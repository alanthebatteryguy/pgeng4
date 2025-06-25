from pydantic import BaseModel, confloat, PositiveInt

class DesignState(BaseModel):
    fc: PositiveInt
    P_avg: PositiveInt  # average compressive stress after losses, psi
    rho: confloat(gt=0)  # reinforcement ratio as fraction (e.g. 0.004)
    slab_thick: confloat(gt=4, lt=36)
    beam_depth: confloat(gt=0)
