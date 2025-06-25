from parking_garage_opt.solver.props import strength_dependent_props


def test_strength_dependent_props():
    props = strength_dependent_props(6000)
    expect = 1_000_000 + 40_000 * (6000 ** 0.5)
    assert abs(props["Ec"] - expect) / expect < 0.01
    assert props["s_max"](7) == min(8*7, 36)
