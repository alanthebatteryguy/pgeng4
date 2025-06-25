from solver.cost import Beam, Design, Materials, cost_of


def test_cost_example():
    design = Design(
        fc=6000,
        slab_area=1000,
        slab_thick=6,
        rho=0.005,
        beams=[Beam(bw=12, depth=24, length=30, tendons=4, tendon_length=30)],
    )
    materials = Materials(
        rebar_cost=1.2,
        strand_cost=2.0,
        formwork_slab=2.0,
        formwork_beam=3.0,
        pump_cost=15.0,
    )
    cost = cost_of(design, materials)
    assert abs(cost - 24797.68740740741) < 1e-6
