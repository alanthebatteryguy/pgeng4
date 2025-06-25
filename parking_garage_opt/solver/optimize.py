"""Basic optimiser interface."""

from typing import Iterable, List, Optional

from ..models.geometry import Geometry
from .grid_generator import generate_geometries


def optimise(
    geometry: Geometry,
    optimise_slab_thickness: bool,
    slab_thickness_range: Optional[Iterable[float]] = None,
) -> List[Geometry]:
    """Return list of candidate geometries."""

    return list(
        generate_geometries(geometry, optimise_slab_thickness, slab_thickness_range)
    )
