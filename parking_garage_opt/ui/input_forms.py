"""User input models."""

from dataclasses import dataclass


@dataclass
class GeometryInput:
    """Parameters collected from the UI."""

    span_x: int
    span_y: int
    slab_thick: float
    max_beam_depth: float
    optimise_slab_thickness: bool = False

    def to_geometry(self):
        from ..models.geometry import Geometry

        return Geometry(
            span_x=self.span_x,
            span_y=self.span_y,
            slab_thick=self.slab_thick,
            max_beam_depth=self.max_beam_depth,
        )
