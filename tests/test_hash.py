import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from app.optimize import optimize, compute_inputs_hash, git_commit_hash


def test_hash_consistency():
    inputs = {'fc': 6000}
    result1 = optimize(inputs)
    result2 = optimize(inputs)
    assert result1['run_hash'] == result2['run_hash']


def test_hash_changes_with_override():
    inputs = {'fc': 6000}
    result1 = optimize(inputs)
    result2 = optimize(inputs, {'deflection_multiplier': 3.0})
    assert result1['run_hash'] != result2['run_hash']
