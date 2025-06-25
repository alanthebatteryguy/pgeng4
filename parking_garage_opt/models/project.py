from pydantic import BaseModel, Field, PositiveInt, confloat

class Geometry(BaseModel):
    """Basic geometric inputs for a single bay."""
    span_x: PositiveInt = Field(..., description="Span in x-direction (ft)")
    span_y: PositiveInt = Field(..., description="Span in y-direction (ft)")
    slab_thick: confloat(gt=4, lt=36) = Field(..., description="Slab thickness (in)")
    max_beam_depth: confloat(gt=0) = Field(..., description="Maximum beam depth (in)")

class Project(BaseModel):
    name: str
    geometry: Geometry
