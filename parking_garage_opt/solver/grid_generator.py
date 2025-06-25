"""Generate geometry design candidates."""

from typing import Iterable, Iterator, Optional

from ..models.geometry import Geometry


def generate_geometries(
    base: Geometry,
    optimise_slab_thickness: bool,
    slab_thickness_range: Optional[Iterable[float]] = None,
) -> Iterator[Geometry]:
    """Yield Geometry variants."""

    if optimise_slab_thickness:
        if not slab_thickness_range:
            raise ValueError(
                "slab_thickness_range required when optimise_slab_thickness is True"
            )
        for h in slab_thickness_range:
            yield base.copy(update={"slab_thick": h})
    else:
        yield base
