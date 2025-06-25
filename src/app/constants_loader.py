from pathlib import Path

DEFAULTS_PATH = Path(__file__).resolve().parents[2] / 'constants.yml'


def _parse_constants(path: Path) -> dict:
    constants = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            # remove comments
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
            constants[key] = value
    return constants


def load_constants(overrides=None):
    """Load constants and merge any user overrides."""
    defaults = _parse_constants(DEFAULTS_PATH)
    overrides = overrides or {}
    merged = defaults.copy()
    merged.update(overrides)
    return merged, defaults
