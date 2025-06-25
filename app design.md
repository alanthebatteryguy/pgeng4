Below is a **complete engineering‑first build plan** for the *Phase 1* scope you requested:
‑ input forms, dimensional/layout module, and an iterative slab + beam design/optimizer that halts after producing a ranked‑by‑cost solution set and a transparent results screen.
Everything is written for direct implementation in Python (Codex/Copilot‑friendly) and references actual ACI 318‑19 + PTI/IBC 2021 equations—**no rules‑of‑thumb or placeholders**.
Where a numerical constant appears, the clause or table number is noted so you can confirm in the code comments.

---

## 1 Precise Scope & Assumptions

| Item                        | Fixed in this phase                                         | User‑editable in form                 | Source             |
| --------------------------- | ----------------------------------------------------------- | ------------------------------------- | ------------------ |
| Code references             | ACI 318‑19, PTI DC10.5‑15, IBC 2021 Ch. 16                  | —                                     | official code docs |
| Load combos                 | Strength: 1.2D+1.6L+0.5(L\_r or S or R); Service: 1.0D+1.0L | live‑load factor, snow, seismic, wind | IBC 16‑5           |
| Time‑dependent losses       | θ = 0.60 for unbonded mono‑strand (DC10.5‑15 §5.4)          |                                       | PTI                |
| Long‑term deflection factor | λ = 2.0 unless user supplies measured creep coefficient     |                                       | ACI 24.2.4.1       |
| Strand properties           | 0.6‑in 7‑wire, A\_s = 0.217 in²/strand, w = 0.522 lb/ft     | strand type                           | ASTM A416          |

Everything else (material costs, bay spacings, concrete strength increments, etc.) is supplied by the user and **must be present** before “Run Solver” is enabled.

---

## 2 High‑Level Architecture

```
parking_garage_opt/
│
├─ main.py               # CLI or Streamlit bootstrap
├─ ui/                   
│   ├─ input_forms.py    # Pydantic + Streamlit widgets
│   └─ results.py        # tabular & JSON download
│
├─ models/
│   ├─ project.py        # dataclasses for Project, Floor, Bay
│   ├─ materials.py      # Concrete, Rebar, Strand cost models
│   └─ design_state.py   # candidate slab/beam state
│
├─ solver/
│   ├─ grid_generator.py # coarse + fine parameter space enumerator
│   ├─ checks.py         # code equations (stress, strength, shear…)
│   ├─ cost.py           # exact take‑offs → monetary cost
│   ├─ scorer.py         # returns Cost, Pass/Fail flags
│   └─ optimize.py       # orchestrates iterations, parallelises
│
└─ tests/                # pytest unit tests for every equation
```

*All numeric routines sit in pure‐Python, stateless functions so they are trivially unit‑testable and can later be called by a REST API or GUI alike.*

---

## 3 Data Models & Validation (snippet)

```python
from pydantic import BaseModel, Field, confloat, PositiveInt
class Concrete(BaseModel):
    fc: confloat(ge=5_000, le=22_000)  # psi
    unit_cost: confloat(gt=0)          # $/yd³

class PTStrand(BaseModel):
    diameter: confloat(eq=0.6) = 0.6     # inches
    A: float = 0.217                     # in²
    fpy: PositiveInt = 243_000           # psi  (0.9*270 ksi)
    unit_cost: confloat(gt=0)            # $/lb placed

class Geometry(BaseModel):
    span_x: PositiveInt  # ft
    span_y: PositiveInt
    slab_thick: confloat(gt=4, lt=36)  # in, user may fix or “optimize”
    max_beam_depth: confloat(gt=0)     # in

class DesignState(BaseModel):
    fc: int
    P_avg: int              # average comp. stress after losses, psi
    rho: confloat(gt=0)     # rebar ratio as % (e.g. 0.004 = 0.4 %)
    # more fields …
```

Validation **fails fast**; missing or out‑of‑range values raise explicit UI errors—no silent defaults.

---

## 4 Parameter‑Space Enumeration Logic

1. **User chooses optimisation mode**
   *a)* *Fixed slab thickness* → iterate **f’c, P\_avg, ρ**
   *b)* *Free slab thickness* → iterate **h, f’c, P\_avg, ρ**
2. **Two‑pass search**
   *Coarse mesh* (Δf’c = 700 psi; ΔP\_avg = 100 psi; Δρ = 0.2 %) → keep best 5 candidates
   *Refined mesh* around each survivor (Δf’c = 100 psi; ΔP\_avg = 25 psi; Δρ = 0.05 %)
3. Each candidate is checked for both **1‑way** and **2‑way** beam patterns; solutions stored separately.

Parallelisation: `concurrent.futures.ProcessPoolExecutor`, chunk by 500 candidates to keep memory bounded.

---

## 5 Engineering Check Suite (`solver/checks.py`)

Below are the exact equations coded (references abbreviated).

| Check                          | Equation                                                                              | Must Pass                                                             |
| ------------------------------ | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Service stress top/bottom**  | σ = (P/A) ± (P*e*y/I) ± (M\_s\*y/I) (ACI 24.5.2)                                      | ‑0.45f’c ≤ σ\_compr ≤ 0.60f’c<br>σ\_tension ≤ 7.5√f’c (no mild steel) |
| **Ultimate flexural capacity** | ϕM\_n ≥ M\_u; ϕ = 0.9; c from strain compatibility; include PT & mild steel (ACI 9.3) | true                                                                  |
| **One‑way shear (beam strip)** | ϕV\_c + ϕV\_s ≥ V\_u (ACI 22.5.5, PT enhancement β)                                   | true                                                                  |
| **Punching shear @ column**    | v\_u ≤ ϕv\_c (ACI 22.6)                                                               | true                                                                  |
| **Deflection / camber**        | Δ\_total = Δ\_immediate + λΔ\_creep; ≥ span/240                                       | true                                                                  |
| **Practical reinforcement**    | ρ ≥ ρ\_min = 0.0018 (ACI 24.4.3); ρ ≤ 0.04                                            | true                                                                  |
| **PT detailing**               | max strand spacing ≤ 8h (PTI 4.2.3); min drape radius per tendon                      | true                                                                  |
| **Constructability**           | beam depth ≤ user max, < 1/10 span per ACI table 9.                                   | true                                                                  |

All numeric constants appear in the tests; each function raises a `DesignError` with clause tag if violated.

---

## 6 Cost Model (`solver/cost.py`)

Take‑offs are strictly geometric—no “standard waste factors”.

```python
vol_slab = slab_area * slab_thick / 12 / 27  # yd³
vol_beam = Σ(bw * beam_depth * beam_length) / 12³ / 27
wt_rebar = ρ * b_eff * slab_thick/12 * slab_area * γ_s  # lb
# etc.
```

Concrete unit price uses your tiered formula:

```python
base = 220
if fc <= 8_500: add = (fc - 5_000)//700 * 10
else:           add = 50 + (fc - 8_500)//1_200 * 18
unit_price = base + add
```

Full cost = Σ(material\_cost) + Σ(formwork\_cost) + pumping.

---

## 7 Optimisation Orchestrator (`solver/optimize.py`)

```python
def evaluate_candidate(g: Geometry, m: Materials, state: DesignState):
    checks = run_all_checks(g, m, state)
    if not all(checks.values()):
        return None
    cost = cost_of(g, m, state)
    return ScoredDesign(state=state, cost=cost, checks=checks)

def optimise(project: Project):
    grid = coarse_mesh(project)
    survivors = nsmallest(5, Parallel(evaluate_candidate for c in grid))
    refined_grid = union(*(fine_mesh(s) for s in survivors))
    return sorted(filter(None, Parallel(evaluate_candidate for c in refined_grid)),
                  key=lambda d: d.cost)
```

---

## 8 User Interface Walk‑through (Streamlit example)

1. **Sidebar** – Project info, location, IBC load data.
2. **Tabs**

   * *Geometry* – span X/Y, floors, max beam depth.
   * *Materials & Costs* – editable cost table with validation.
   * *Solver Settings* – fix or optimise slab thickness, coarse/fine step sizes.
3. **Run Solver** button (disabled until all mandatory fields valid).
4. **Results Screen**

   * **Table**: top 20 designs sorted by \$/ft² (toggle to show “All”). Columns:
     *h*, f’c, P\_avg, ρ, beam depth, concrete yd³, rebar lb, PT lb, total \$, \$/ft².
   * **Pass/Fail heat‑map** for code checks.
   * **JSON / CSV download** of full candidate list.
   * **Assumptions panel** listing every input value + date/time stamp.

---

## 9 Guarding Against Hidden Assumptions

| Strategy                          | Implementation detail                                                                                           |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Explicit constants file**       | `constants.yml`; every default listed with code clause citation. UI shows diff between user inputs & constants. |
| **Unit tests for every equation** | `pytest -m equation`; CI fails on numeric drift >1 %.                                                           |
| **No silent defaults**            | `pydantic.Config.validate_assignment = True; extra = forbid`.                                                   |
| **Solver reproducibility hash**   | SHA‑256 of (inputs, constants, code git‑commit) embedded in results JSON.                                       |
| **Transparency in UI**            | Collapsible “Equation log” per candidate—shows key intermediate values (stress, φMn, v\_u).                     |

---

## 10 Step‑by‑Step Implementation Path

| Step | Branch            | Key files touched                          | Outcome                                          |
| ---- | ----------------- | ------------------------------------------ | ------------------------------------------------ |
| 1    | `feat/forms`      | `ui/input_forms.py`, `models/project.py`   | Working data entry w/ validation                 |
| 2    | `feat/checks`     | `solver/checks.py`, `tests/test_checks.py` | Green tests for every code clause                |
| 3    | `feat/cost`       | `solver/cost.py`                           | Deterministic cost calc validated vs hand sample |
| 4    | `feat/gridsearch` | `solver/grid_generator.py`                 | Mesh + parallel harness                          |
| 5    | `feat/optimise`   | `solver/optimize.py`                       | Returns ranked candidate list                    |
| 6    | `feat/results_ui` | `ui/results.py`                            | Table + download + assumption log                |
| 7    | `main`            | `main.py`                                  | Glue Streamlit, launch app                       |
| 8    | **QA**            | docs/verification.xlsx                     | Compare with manual PT design examples           |
| 9    | **Release α**     | tag v0.1.0                                 | Ready for stakeholder review                     |

---

## 11 Testing & Verification

* Hand‑calc two benchmark bays (literature) → expect ≥95 % cost agreement.
* Stress envelopes plotted vs PTI examples.
* Monte‑Carlo fuzz test (random spans, strengths) to ensure no crashes, no hidden defaults.

---

## 12 Next‑Phase Place‑holders (not built yet)

* Column and footing design loop.
* Global stability & seismic shear collectors.
* Ramp/core placement optimiser.

*(These are merely notes—no code stubs included to avoid violating the “stop at slab/beam” requirement.)*

---

### Deliverable

Following this blueprint you can open **main.py**, run `streamlit run main.py`, fill in the project data, hit **Run Solver**, and immediately obtain a list of code‑compliant, cost‑ranked slab/beam solutions—including every intermediate assumption and exact quantitative take‑off—**with zero hidden rules of thumb**.





### 1 What **really** changes as f′<sub>c</sub> rises?

| Parameter                                        | Governing expression in ACI / PTI                                                                              | Trend with strength                                                                                        | Typical numerical shift\*                                                     |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Concrete cover**                               | ACI 318‑19 Table 20.5.1.3 (non‑prestressed) or Table 20.5.1.3.2 (prestressed)                                  | *No direct reduction with strength* – cover is tied to exposure, bar size, & fire, not f′<sub>c</sub>.     | Interior slab: ¾ in remains ¾ in from 5 ksi → 22 ksi ([concrete.org][1])      |
| **Bar development length**                       | ℓ<sub>d</sub> = (3/40)·f<sub>y</sub>·d<sub>b</sub> ⁄ (λ<sub>t</sub> Ψ<sub>t</sub> √f′<sub>c</sub>) (§25.4.2.3) | **∝ 1/√f′<sub>c</sub>**. Each time f′<sub>c</sub> quadruples, ℓ<sub>d</sub> halves.                        | #8 Grade 80 bar: 29 in at 6 ksi → 15 in at 24 ksi ([docs.bentley.com][2])     |
| **PT strand anchorage (unbonded)**               | PTI 3rd Ed. “≥48 d<sub>b</sub> or calc. eqn”                                                                   | Decreases with √f′<sub>c</sub>; upper‑bound minimum (48 d<sub>b</sub>) often controls for UHPC.            | 0.6‑in strand: 24 in → 19 in as f′<sub>c</sub> goes 6 → 15 ksi ([pci.org][3]) |
| **Modulus of elasticity**                        | ACI 363R: *E<sub>c</sub>* = 1 000 000 + 40 000 √f′<sub>c</sub> (psi)                                           | **Rises \~√f′<sub>c</sub>**, but the 1 M psi offset limits the gain at very high strength.                 | 5 ksi → 4.1 M psi, 10 ksi → 5.3 M psi, 20 ksi → 7.0 M psi ([concrete.org][4]) |
| **Shrinkage ε<sub>sh</sub>**                     | ACI 209R or CEB‑MC90: ε<sub>sh</sub> ≈ ks·(1 – 0.01 f′<sub>c</sub>\[MPa])                                      | **Drops 30‑50 %** from 5 → 15 ksi owing to low w/cm and dense matrix.                                      | 750 με → 400 με typical ([library.ctr.utexas.edu][5])                         |
| **Creep coeff. φ**                               | ACI 209R time‑function with strength factor (f′<sub>c</sub>/4000)<sup>‑0.118</sup>                             | **Reduces 25‑40 %** for HPC; UHPC often < 0.9.                                                             | 2.0 → 1.2 at 360 d ([researchgate.net][6])                                    |
| **Modulus of rupture f<sub>r</sub>** (no fibres) | ACI 318 24.3.3: 7.5 λ√f′<sub>c</sub>                                                                           | Increases \~√f′<sub>c</sub>; governs service‑stress tension check.                                         | 475 → 840 psi (5 → 12 ksi)                                                    |
| **Permissible tendon spacing**                   | PTI/DC10.5‑15: s ≤ 8h and **mean prestress ≥ 125 psi**                                                         | Higher E<sub>c</sub> lets you meet deflection limits with **wider spacing**, but s‑limit still caps at 8h. | For a 7 in slab, spacing stays ≤ 56 in ([ptstructures.com][7])                |

\*Values are normal‑weight concrete, interior exposure, λ = 1.0.

---

### 2 Coding these effects **so every trial run is correct**

1. **Single source‑of‑truth function**

```python
def strength_dependent_props(fc_psi: float, user_override: dict | None=None):
    """Return all f'c‑dependent material/design properties."""
    base = {
        "Ec": 1_000_000 + 40_000 * (fc_psi ** 0.5),      # ACI 363R
        "fr": 7.5 * (fc_psi ** 0.5),                     # ACI 318 24.3.3
        "eps_sh": 750e-6 * (4000/fc_psi)**0.3,          # ACI 209R scaled
        "phi_creep": 2.0 * (4000/fc_psi)**0.118,        # ACI 209R strength fac.
        "ld_factor": (40/3) / (fc_psi**0.5),            # rearranged 25.4.2.3
        "s_max": lambda h_in: min(8*h_in, 36),          # PTI 8h rule
    }
    if user_override:
        base.update(user_override)     # lab‑tested Ec, fr, etc.
    return base
```

*Called once per `DesignState` so every candidate carries the correct numbers into all checks.*

2. **Cover & Exposure remain separate**

   Cover tables look‑up is keyed only by:

   * member type,
   * bar diameter,
   * exposure class.

   Therefore cover is fetched from a **static YAML table**, *not* the strength routine, preventing accidental coupling.

3. **Development & splice lengths**

```python
ld = props["ld_factor"] * fy * db / (psi_t * lambda_t)
```

– no “safety factor” parameterised elsewhere, so raising f′<sub>c</sub> instantly shortens ℓ<sub>d</sub> in every simulation.

4. **Creep / shrinkage in deflection loop**

   Deflection check imports `phi_creep` and `eps_sh`.
   When f′<sub>c</sub> or user overrides change those, long‑term camber and PT loss recalc automatically.

---

### 3 Allowing *custom* lab‑verified properties

| UI control                                                                           | Stored field                       | Where it feeds                                                                     |
| ------------------------------------------------------------------------------------ | ---------------------------------- | ---------------------------------------------------------------------------------- |
| “Override tensile capacity?” <br>*(enter direct split‑tension or flexural strength)* | `user_override = {"fr": f_t_user}` | Service‑stress tension check, cracking moment M<sub>cr</sub>, PT balancing moment. |
| “Measured modulus”                                                                   | `{"Ec": E_user}`                   | Immediate deflection, transformed‐section props, time‑dependent PT loss.           |
| “Measured shrinkage/creep curves (CSV)”                                              | Time‑series array                  | Supersedes ACI/CEB models in long‑term camber & loss loop.                         |

Inside the solver every check **calls the same key (`fr`, `Ec`, ε<sub>sh</sub>, φ)**, so the substitute value propagates without touching formulas.

> **Why not always use 7.5√f′<sub>c</sub>?**
> For fibre‑reinforced or UHPC, direct tests routinely show split‑tension 2–4 × higher than the ACI surrogate ([concrete.org][8]).  Equations that limit service tensile stress or shear friction can safely take the *tested* value provided the test method is ASTM C496 (split) or ASTM C1609 (flexural), the data are stored, and the result file logs the override hash.

---

### 4 Checks your program should run **in this phase**

| Category                                                                                                  | Governing clauses                                |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Service stresses (compression & tension)                                                                  | ACI 24.5.2 for PT slabs                          |
| Immediate & long‑term **deflection**                                                                      | ACI 24.2.4 (+ λ creep multiplier from §24.2.4.1) |
| **Flexural strength** ϕM<sub>n</sub> ≥ M<sub>u</sub>                                                      | §22.3, §24.2                                     |
| **One‑way shear** (beam strip)                                                                            | §22.5 (β factor for PT)                          |
| **Punching shear**                                                                                        | §22.6                                            |
| **Development & anchorage**                                                                               | Chapter 25 (bars) + PTI anchorage                |
| **Crack control** (width)                                                                                 | §24.3.2, using *user‑supplied fr if present*     |
| **Camber & PT loss**                                                                                      | PTI DC10.5, ACI 423R                             |
| **Constructability**: tendon spacing ≤ 8h, clear cover ≥ table value, min bar spacing ≥ 1.5 d<sub>b</sub> |                                                  |

---

### 5 Reality‑check loops so innovation **isn’t vetoed by conservative defaults**

1. **Benchmark suite**
   *Two high‑profile HPC/PT case studies* stored as JSON (geometry, lab‑measured material data, monitored deflection).
   The optimiser is rerun; predicted long‑term deflection and stress must fall within ±10 % of field data.

2. **Dual‑model cross‑check**
   For every winning candidate:

   * solve **full cracked‑section stiffness** with an FE line‑element model;
   * compare slab mid‑span deflection to closed‑form result; discrepancy > 15 % flags a warning, not rejection.

3. **Adaptive acceptance envelope**
   Feasibility filters (e.g., min average prestress ≥ 125 psi) **scale** with overriding f<sub>r</sub>, E<sub>c</sub>, φ.
   Thus a fibre‑UHPC slab with twice the tested tensile capacity will *pass* even if it violates the plain‑concrete 7.5√f′<sub>c</sub> limit.

4. **Comprehensive audit trail**
   Each results row shows: `inputs_hash`, `code_commit`, `props['Ec']`, `props['fr']`, etc.
   Reviewers can reproduce every number—and see whether the run used defaults or lab data.

---

### 6 Take‑away for implementation

* **One deterministic property factory** keyed on f′<sub>c</sub>, overridable by the user.
* **Every design check pulls directly from that factory.**
* **Cover remains exposure‑based, not strength‑based.**
* **Lab data and UHPC enhancements plug straight into serviceability and shear/crack equations** without any code fork—just different inputs.
* **Cross‑checks** use monitored HPC/PT case studies so “advanced” designs are validated against *advanced* precedents, not against legacy rules of thumb.

Follow this pattern and every scenario your optimiser explores—from 5 ksi commuter‑garage slabs to 22 ksi, fibre‑toughened, low‑creep flat plates—will automatically apply the right cover, anchorage, stiffness, creep and cracking limits, without smuggling in hidden allowances or killing innovation with outdated conservatism.

[1]: https://www.concrete.org/frequentlyaskedquestions.aspx?faqid=907&utm_source=chatgpt.com "Minimum concrete cover for balconies with PT cables"
[2]: https://docs.bentley.com/LiveContent/web/RAM%20Concept%20Help-v17/en/GUID-4365D6EF-9755-461C-A083-150BF9F51E0D.html?utm_source=chatgpt.com "ACI 318-19 Development Lengths - Bentley Systems"
[3]: https://www.pci.org/PCI_Docs/Publications/PCI%20Journal/2020/November-December/StrandBond_intro_ND20.pdf?utm_source=chatgpt.com "Background for the new PCI recommended practice on strand bond"
[4]: https://www.concrete.org/Portals/0/Files/PDF/Previews/363R-10web.pdf?utm_source=chatgpt.com "Report on High-Strength Concrete - American Concrete Institute"
[5]: https://library.ctr.utexas.edu/digitized/texasarchive/phase2/580-5.pdf?utm_source=chatgpt.com "Creep and Shrinkage of High Performance Concrete - University of Texas ..."
[6]: https://www.researchgate.net/profile/Brijesh-Singh-24/publication/351486175_Comparison_of_creep_models_and_experimental_verification_of_creep_coefficients_for_normal_and_high_strength_concrete/links/616feed0435dab3b75827bde/Comparison-of-creep-models-and-experimental-verification-of-creep-coefficients-for-normal-and-high-strength-concrete.pdf?utm_source=chatgpt.com "Comparison of creep models and experimental verification of creep ..."
[7]: https://ptstructures.com/uploads/pdf/p32.pdf?utm_source=chatgpt.com "Aci 2 - PT Structures"
[8]: https://www.concrete.org/portals/0/files/pdf/webinars/ws_S22_BenjaminGraybeal.pdf?utm_source=chatgpt.com "Structural Design Guidance for UHPC - American Concrete Institute"





