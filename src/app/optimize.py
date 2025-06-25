import json
import hashlib
import subprocess
from typing import Dict, Tuple

from .constants_loader import load_constants


def git_commit_hash() -> str:
    """Return the current git commit hash."""
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], encoding='utf-8'
        ).strip()
    except Exception:
        commit = 'unknown'
    return commit


def compute_inputs_hash(inputs: Dict, constants: Dict, commit: str) -> str:
    """Compute SHA256 hash of inputs, constants and commit."""
    data = {
        'inputs': inputs,
        'constants': constants,
        'commit': commit,
    }
    payload = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def optimize(inputs: Dict, overrides: Dict | None = None) -> Dict:
    """Dummy optimisation routine returning hash and merged constants."""
    merged, defaults = load_constants(overrides)
    commit = git_commit_hash()
    run_hash = compute_inputs_hash(inputs, merged, commit)
    # placeholder for real optimisation
    return {
        'inputs': inputs,
        'constants': merged,
        'defaults': defaults,
        'commit': commit,
        'run_hash': run_hash,
    }
