"""Material property helpers."""

def strength_dependent_props(fc_psi: float, user_override: dict | None = None) -> dict:
    """Return f'c-dependent properties with optional overrides."""
    base = {
        "Ec": 1_000_000 + 40_000 * (fc_psi ** 0.5),  # ACI 363R
        "fr": 7.5 * (fc_psi ** 0.5),                 # ACI 318 24.3.3
        "eps_sh": 750e-6 * (4000 / fc_psi) ** 0.3,    # ACI 209R
        "phi_creep": 2.0 * (4000 / fc_psi) ** 0.118,  # ACI 209R strength factor
        "ld_factor": (40 / 3) / (fc_psi ** 0.5),      # ACI 25.4.2.3 rearranged
        "s_max": lambda h_in: min(8 * h_in, 36),      # PTI 8h rule
    }
    if user_override:
        base.update(user_override)
    return base
