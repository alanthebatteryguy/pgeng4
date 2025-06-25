"""Basic geometry dataclass used in optimisation routines."""

from dataclasses import dataclass, replace


@dataclass
class Geometry:
    span_x: int
    span_y: int
    slab_thick: float
    max_beam_depth: float

    def copy(self, update: dict | None = None) -> "Geometry":
        """Return a copy of this instance applying ``update`` if provided."""

        update = update or {}
        return replace(self, **update)
