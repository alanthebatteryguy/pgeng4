from pydantic import BaseModel, PositiveInt, confloat

class Concrete(BaseModel):
    fc: confloat(ge=5_000, le=22_000)
    unit_cost: confloat(gt=0)

class PTStrand(BaseModel):
    diameter: confloat(eq=0.6) = 0.6
    A: float = 0.217
    fpy: PositiveInt = 243_000
    unit_cost: confloat(gt=0)

class Rebar(BaseModel):
    fy: PositiveInt = 60_000
    unit_cost: confloat(gt=0)
