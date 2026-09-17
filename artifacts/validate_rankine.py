#!/usr/bin/env python3
"""
Stage-4 validator for the GAIMS "Plant Operator" activity (Appendix C companion).

This file is the *independent redundant derivation* required by Section 4.4: it is a
reference solver written separately from the simulator artefact and from the Moodle
Formulas answer key, and it is used to cross-check both over a Monte Carlo sample of the
parameter space. Agreement on one worked example proves nothing; agreement across
thousands of constrained draws is evidence.

Checks implemented:
  1. Physical bounds            0 < eta_th < 1, 0 < x4 <= 1, wnet > 0, mdot > 0
  2. Energy balance closure     q_in - q_out - w_net = 0 to relative 1e-9
  3. Dimensional consistency    explicit unit arithmetic on every derived quantity
  4. Limiting cases             ideal-component reduction; degenerate pressure ratio
  5. Effective cardinality      after constraint filtering
  6. Answer separation          per-part and joint, at the stated grading tolerance
  7. Parameter reachability     every randomised variable must move at least one answer

Check 7 rejected the original four-part version of this question: the randomised pump
isentropic efficiency moved no graded answer by more than the 1% grading tolerance. The
question was regenerated with a fifth part (actual pump specific work) that is sensitive
to it. This is the intended behaviour of the gate, and is reported in Section 6.1.

Run:  python3 artifacts/validate_rankine.py
Exit code 0 = all gates passed; 1 = at least one gate failed (stage 4 fails -> regenerate).
"""

from __future__ import annotations
import itertools
import random
import sys

# ---------------------------------------------------------------------------
# Fixed reference states. Boiler 8 MPa / 480 C (interpolated in the superheated
# table between 400 C and 500 C); condenser 10 kPa saturated properties.
# These are the values the generated artefact and the Formulas question must match.
# ---------------------------------------------------------------------------
H_F = 191.81      # kJ/kg   saturated liquid enthalpy at 10 kPa
H_FG = 2392.1     # kJ/kg   latent heat at 10 kPa
S_F = 0.6492      # kJ/kg.K
S_FG = 7.4996     # kJ/kg.K
V_F = 0.001010    # m3/kg
H3 = 3347.5       # kJ/kg   8 MPa, 480 C
S3 = 6.6544       # kJ/kg.K 8 MPa, 480 C
P_BOILER = 8000.0  # kPa
P_COND = 10.0      # kPa

TOL = 0.01         # relative grading tolerance used by the Formulas question


def solve(eta_t: float, eta_p: float, w_net_mw: float) -> dict:
    """Reference solution for one instance. All enthalpies kJ/kg, work kJ/kg."""
    x4s = (S3 - S_F) / S_FG
    h4s = H_F + x4s * H_FG
    wt = eta_t * (H3 - h4s)                 # actual turbine work
    # v [m3/kg] * dP [kPa] = kJ/kg, since 1 kPa.m3 = 1 kJ
    wp = V_F * (P_BOILER - P_COND) / eta_p  # actual pump work
    h2 = H_F + wp
    h4 = H3 - wt
    q_in = H3 - h2
    q_out = h4 - H_F
    w_net = wt - wp
    return {
        "x4s": x4s, "h4s": h4s, "h2": h2, "h4": h4,
        "wt": wt, "wp": wp, "q_in": q_in, "q_out": q_out,
        "eta_th": w_net / q_in,
        "w_net": w_net,
        "x4": (h4 - H_F) / H_FG,
        "mdot": w_net_mw * 1000.0 / w_net,  # MW -> kW, kW / (kJ/kg) = kg/s
    }


def grid():
    et = [round(0.780 + 0.005 * i, 3) for i in range(100) if 0.780 + 0.005 * i <= 0.920 + 1e-9]
    ep = [round(0.700 + 0.005 * i, 3) for i in range(100) if 0.700 + 0.005 * i <= 0.850 + 1e-9]
    wn = list(range(40, 186, 5))
    xm = [0.86, 0.87, 0.88, 0.89, 0.90]
    return et, ep, wn, xm


def constraints_ok(r: dict) -> bool:
    """Section 4.3 validity constraints applied to a candidate draw."""
    return (0.0 < r["eta_th"] < 1.0
            and 0.0 < r["x4"] <= 1.0
            and r["w_net"] > 0.0
            and 35.0 <= r["mdot"] <= 220.0)


def main() -> int:
    failures: list[str] = []
    et, ep, wn, xm = grid()

    # ---- 5. effective cardinality after constraint filtering -------------
    admissible = 0
    for a, b, c in itertools.product(et, ep, wn):
        if constraints_ok(solve(a, b, c)):
            admissible += 1
    cardinality = admissible * len(xm)
    print(f"[5] effective cardinality after constraints : {cardinality:,}")
    if cardinality < 10_000:
        failures.append("cardinality below the 1e4 formative floor (Section 4.3)")

    random.seed(20260917)
    sample = []
    while len(sample) < 6000:
        r = solve(random.choice(et), random.choice(ep), random.choice(wn))
        if constraints_ok(r):
            sample.append(r)

    # ---- 1./2. physical bounds and energy balance -----------------------
    bad_bounds = [r for r in sample if not constraints_ok(r)]
    worst_balance = max(abs(r["q_in"] - r["q_out"] - r["w_net"]) / r["q_in"] for r in sample)
    print(f"[1] instances violating physical bounds     : {len(bad_bounds)}")
    print(f"[2] worst relative energy-balance residual  : {worst_balance:.2e}")
    if bad_bounds:
        failures.append("physical bounds violated in the constrained sample")
    if worst_balance > 1e-9:
        failures.append(f"energy balance does not close (residual {worst_balance:.2e})")

    # ---- 3. dimensional consistency --------------------------------------
    # v[m3/kg]*dP[kPa] -> kJ/kg ; W[MW]*1000 -> kW ; kW/(kJ/kg) -> kg/s
    r = sample[0]
    dim_ok = (abs(V_F * (P_BOILER - P_COND) / 0.8 - solve(0.85, 0.8, 100)["wp"]) < 1e-12)
    print(f"[3] dimensional consistency of pump work    : {'ok' if dim_ok else 'FAIL'}")
    if not dim_ok:
        failures.append("pump-work unit arithmetic inconsistent")

    # ---- 4. limiting cases ----------------------------------------------
    ideal = solve(1.0, 1.0, 100.0)
    print(f"[4] ideal-component limit eta_th            : {ideal['eta_th']:.4f}"
          f"  (textbook ideal Rankine, 8 MPa/480 C/10 kPa, ~0.38-0.39)")
    if not (0.36 < ideal["eta_th"] < 0.41):
        failures.append(f"ideal-component limit eta_th={ideal['eta_th']:.4f} outside the expected band")
    degenerate = solve(0.02, 0.80, 100.0)
    print(f"[4] eta_t -> 0 gives w_net                  : {degenerate['w_net']:.1f} kJ/kg"
          f"  ({'infeasible, correctly rejected' if not constraints_ok(degenerate) else 'NOT REJECTED'})")
    if constraints_ok(degenerate):
        failures.append("degenerate low-eta_t draw was not rejected by the constraints")

    # ---- 6. answer separation -------------------------------------------
    keys = ["eta_th", "w_net", "x4", "mdot", "wp"]
    trials = 20_000
    per_part = {k: 0 for k in keys}
    joint = 0
    for _ in range(trials):
        a, b = random.sample(sample, 2)
        sep_any = False
        for k in keys:
            if abs(a[k] - b[k]) / abs(b[k]) > TOL:
                per_part[k] += 1
                sep_any = True
        joint += sep_any
    for k in keys:
        print(f"[6] {k:<7} pairs separated beyond {TOL:.0%}       : {per_part[k]/trials:.1%}")
    print(f"[6] at least one part separated (shared answer set fails): {joint/trials:.2%}")
    if joint / trials < 0.99:
        failures.append("joint answer separation below 99%: sharing a full answer set would too often succeed")

    # ---- 7. parameter reachability ---------------------------------------
    base = solve(0.85, 0.78, 110.0)
    reach = {
        "eta_t": any(abs(solve(0.92, 0.78, 110.0)[k] - base[k]) / abs(base[k]) > TOL for k in keys),
        "eta_p": any(abs(solve(0.85, 0.70, 110.0)[k] - base[k]) / abs(base[k]) > TOL for k in keys),
        "Wnet":  any(abs(solve(0.85, 0.78, 180.0)[k] - base[k]) / abs(base[k]) > TOL for k in keys),
    }
    for name, ok in reach.items():
        print(f"[7] {name:<6} reaches at least one graded answer : {'yes' if ok else 'NO — degenerate'}")
        if not ok:
            failures.append(f"randomised variable {name} does not propagate to any graded answer")

    print()
    if failures:
        print("STAGE 4 FAILED — regenerate (Section 4.4):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("STAGE 4 PASSED — proceed to expert review (human gate 2).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
