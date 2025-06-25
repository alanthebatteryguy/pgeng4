from parking_garage_opt.solver.cost import concrete_unit_price


def test_concrete_unit_price():
    assert concrete_unit_price(6000) > concrete_unit_price(5000)
