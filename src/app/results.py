from typing import Dict


def display_results(result: Dict) -> None:
    """Print optimisation results including hash and constants."""
    print(f"Run hash: {result['run_hash']}")
    print(f"Git commit: {result['commit']}")
    print("\nConstants used:")
    for key, default_val in result['defaults'].items():
        val = result['constants'][key]
        if val != default_val:
            print(f"- {key}: {val} (override, default {default_val})")
        else:
            print(f"- {key}: {val}")
