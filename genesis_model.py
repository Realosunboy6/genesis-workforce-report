"""
Genesis workforce & production aging-chain model (Python replica of the Vensim model).

Stocks:  Rookies -> Experienced -> Gray Hairs (first-order delays)
Flows:   hiring (exogenous), learning, maturation, retirement
Output:  total workforce, lamp production = sum(stock * productivity) * multiplier

Retirement assumption (CALIBRATED against the report's baseline: the model
reproduces ~1,233 workers / ~3.72M lamps only if retirement_time is the mean
number of years spent as a Gray Hair, NOT total career length):
  gray_tenure = retirement_time.

Baseline parameters mirror the report:
  hiring: 50/yr in year 1, 100/yr in years 2..10
  learning_time = 1 yr, maturation_time = 5 yrs, gray_tenure = 10 yrs
  productivity: rookie 1000, experienced 2000, gray hair 4000 lamps/yr
  initial workforce 850, split by steady-state mix of the delays (stated assumption)

Improved scenario: hiring 50/yr in year 1 then 147.14/yr flat (Raj: "the hiring
rate has to be 147/year to reach 1700 employees"), maturation 3 yrs,
gray_tenure 15 yrs, productivity x1.4167 at year 10.
"""
import csv

PROD = {"rookie": 1000.0, "experienced": 2000.0, "gray": 4000.0}
DT = 0.01          # integration step (years); halved in validation test
HORIZON = 10.0     # years


def hiring_baseline(t):
    """50/yr in year 1, 100/yr afterwards."""
    return 50.0 if t < 1.0 else 100.0


def hiring_high(t):
    """50/yr in year 1, then 147.14/yr flat (report: 'hire 50 ... before gradually
    increasing ... to around 147.14 employees per year'; Raj: 'the hiring rate
    has to be 147/year to reach 1700 employees')."""
    return 50.0 if t < 1.0 else 147.14


def initial_mix(total, learning, maturation, gray_tenure):
    """Steady-state mix of the aging chain (proportional to mean residence time)."""
    w = [learning, maturation, gray_tenure]
    s = sum(w)
    return [total * x / s for x in w]


# True initial stocks from the group's .mdl (shared 2026-10-02):
#   Roockies = INTEG(Hiring Rate - Learning Rate, 100)
#   Experienced = INTEG(Learning Rate - Maturing Rate, 250)
#   Gray Hair = INTEG(Maturing Rate - Retiring Rate, 500)
TRUE_INIT = (100.0, 250.0, 500.0)


def simulate(hiring_fn, learning, maturation, gray_tenure,
             prod_mult=1.0, dt=DT, horizon=HORIZON,
             init_total=850.0, init=None):
    r, e, g = init if init is not None else (TRUE_INIT if init_total == 850.0
                                            else initial_mix(init_total, learning, maturation, gray_tenure))
    t = 0.0
    hist = []
    while t < horizon - 1e-12:
        h = hiring_fn(t)
        learn = r / learning
        matur = e / maturation
        retir = g / gray_tenure
        r += (h - learn) * dt
        e += (learn - matur) * dt
        g += (matur - retir) * dt
        t += dt
        hist.append((t, r, e, g))
    workforce = r + e + g
    production = (PROD["rookie"] * r + PROD["experienced"] * e + PROD["gray"] * g) * prod_mult
    return {
        "t": t, "rookies": r, "experienced": e, "gray": g,
        "workforce": workforce, "production": production, "history": hist,
    }


def scenario_table():
    """2^3 design: hiring {base, high} x maturation {5, 3} x gray_tenure {10, 15};
    learning fixed at 1 yr. Returns rows with year-10 outcomes at base productivity
    plus the productivity multiplier needed to hit 7.8M lamps."""
    rows = []
    for hi, (hname, hfn) in enumerate([("base", hiring_baseline), ("high", hiring_high)]):
        for mi, mat in enumerate([5.0, 3.0]):
            for ri, ret in enumerate([10.0, 15.0]):
                res = simulate(hfn, 1.0, mat, ret)
                base_prod = res["production"]
                need_mult = 7.8e6 / base_prod
                rows.append({
                    "scenario": f"S{len(rows)+1}",
                    "hiring": hname, "learning": 1.0,
                    "maturation": mat, "retirement": ret,
                    "workforce_y10": res["workforce"],
                    "rookies_y10": res["rookies"],
                    "experienced_y10": res["experienced"],
                    "gray_y10": res["gray"],
                    "production_base_y10": base_prod,
                    "required_multiplier": need_mult,
                    "required_gain_pct": (need_mult - 1.0) * 100.0,
                })
    return rows


def validation_checks():
    out = {}
    # 1. time-step independence: halve dt, compare baseline year-10 outcomes
    b1 = simulate(hiring_baseline, 1.0, 5.0, 10.0, dt=0.01)
    b2 = simulate(hiring_baseline, 1.0, 5.0, 10.0, dt=0.005)
    out["timestep_workforce_relerr"] = abs(b1["workforce"] - b2["workforce"]) / b2["workforce"]
    out["timestep_production_relerr"] = abs(b1["production"] - b2["production"]) / b2["production"]
    # 2. extreme condition: zero hiring -> workforce and production decay toward 0
    z = simulate(lambda t: 0.0, 1.0, 5.0, 10.0)
    out["zero_hiring_workforce_y10"] = z["workforce"]
    out["zero_hiring_production_y10"] = z["production"]
    # 3. extreme condition: zero productivity -> production 0, workforce unaffected
    zp = simulate(hiring_baseline, 1.0, 5.0, 10.0, prod_mult=0.0)
    out["zero_prod_production_y10"] = zp["production"]
    out["zero_prod_workforce_y10"] = zp["workforce"]
    out["baseline_workforce_for_ref"] = b1["workforce"]
    return out


if __name__ == "__main__":
    print("=== BASELINE (report claims ~1,233 workers, ~3.72M lamps at year 10) ===")
    b = simulate(hiring_baseline, 1.0, 5.0, 10.0)
    print(f"workforce y10 = {b['workforce']:.1f}")
    print(f"production y10 = {b['production']/1e6:.3f} M lamps")
    print(f"mix y10: rookies={b['rookies']:.0f} experienced={b['experienced']:.0f} gray={b['gray']:.0f}")

    print("\n=== IMPROVED SCENARIO (report claims 1,700 workers, 5.51M lamps) ===")
    imp = simulate(hiring_high, 1.0, 3.0, 15.0, prod_mult=1.4167)
    imp_base = simulate(hiring_high, 1.0, 3.0, 15.0, prod_mult=1.0)
    print(f"workforce y10 = {imp['workforce']:.1f}")
    print(f"production y10 @+41.67% = {imp['production']/1e6:.3f} M lamps")
    print(f"production y10 @base prod = {imp_base['production']/1e6:.3f} M lamps")
    print(f"mix y10: rookies={imp['rookies']:.0f} experienced={imp['experienced']:.0f} gray={imp['gray']:.0f}")

    print("\n=== 8-SCENARIO DESIGN TABLE ===")
    rows = scenario_table()
    for r_ in rows:
        print(f"{r_['scenario']}: hire={r_['hiring']:>4} mat={r_['maturation']:.0f} ret={r_['retirement']:.0f} "
              f"| workforce={r_['workforce_y10']:7.1f} prod_base={r_['production_base_y10']/1e6:5.3f}M "
              f"| need x{r_['required_multiplier']:.3f} (+{r_['required_gain_pct']:.1f}%)")

    with open("genesis_scenarios.csv", "w", newline="") as f:
        cols = ["scenario", "hiring", "learning", "maturation", "retirement",
                "workforce_y10", "rookies_y10", "experienced_y10", "gray_y10",
                "production_base_y10", "required_multiplier", "required_gain_pct"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote genesis_scenarios.csv")

    print("\n=== VALIDATION CHECKS ===")
    for k, v in validation_checks().items():
        print(f"{k} = {v:.6g}")

    print("\n=== INFEASIBILITY BOUND ===")
    print(f"required avg per worker = {7.8e6/1700:.1f} lamps/yr (gray-hair max = 4000)")
    print(f"all-gray-hair ceiling = {1700*4000/1e6:.1f}M < 7.8M  -> infeasible at base productivity")
