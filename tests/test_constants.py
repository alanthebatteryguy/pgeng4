import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from app.constants_loader import load_constants


def test_load_defaults():
    merged, defaults = load_constants()
    assert merged == defaults
    assert 'compressive_strength_increment' in merged


def test_overrides():
    merged, defaults = load_constants({'deflection_multiplier': 3.0})
    assert merged['deflection_multiplier'] == 3.0
    assert defaults['deflection_multiplier'] == 2.0
