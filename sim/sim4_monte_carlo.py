"""
Sim 4 - Monte Carlo of hops (SOTIF and fault-handling effectiveness).

Each run draws vehicle load, inertia, centre-of-gravity offset, crosswind gust,
fill level, fill temperature, thruster scatter and, with stressed probabilities,
one of three faults. Four safety-concept configurations are compared on the
same random draws:

  A  no reserve check, monitor cuts all gas on any fault (naive)
  B  reserve check before take-off, monitor cuts all gas
  C  reserve check, isolate-and-recover logic (9 kN lift groups)
  D  C with 11 kN lift groups

Fault probabilities are deliberately STRESSED (about 1 in 8 runs has a fault)
so that conditional outcomes can be estimated; they are not field rates.
Sim 6 combines these conditional results with failure rates.
"""
import json
import numpy as np
from common import (HopSim, classify, fill_mass, P_FILL_BAR, P_MIN_BAR, GAMMA, MASS)
import plotstyle as ps

N = 12000
SEED = 2026
RESERVE_FACTOR = 1.2
NOMINAL_NEED_KG = 134.2          # Sim 1 reference hop at nominal conditions


def draw(rng, n):
    d = dict(
        mass=rng.uniform(1800, 2000, n),
        inertia=rng.normal(600, 30, n),
        cg_offset=rng.uniform(-0.04, 0.04, n),
        gust=rng.uniform(0, 12, n) * rng.choice([-1, 1], n),
        gust_t=rng.uniform(0, 3, n),
        thrust_scale=rng.normal(1.0, 0.03, n),
        fill_frac=rng.uniform(0.4, 1.0, n),
        gas_T=rng.uniform(263, 313, n),
        detect_delay=rng.uniform(0.01, 0.05, n),
    )
    u = rng.uniform(size=n)
    kind = np.select([u < 0.05, u < 0.10, u < 0.13], [1, 2, 3], 0)   # 1 stuck-open, 2 leak, 3 stuck-closed
    tf = rng.uniform(0.5, 3.0, n)
    d["stuck_open_t"] = np.where(kind == 1, tf, np.inf)
    d["leak_t"] = np.where(kind == 2, tf, np.inf)
    d["leak_rate"] = np.where(kind == 2, rng.uniform(5, 40, n), 0.0)
    d["stuck_closed_t"] = np.where(kind == 3, tf, np.inf)
    d["kind"] = kind
    p = P_FILL_BAR * d["fill_frac"]
    d["gas_kg"] = fill_mass(p, d["gas_T"])
    d["usable_kg"] = d["gas_kg"] * (1 - (P_MIN_BAR / p) ** (1 / GAMMA))
    return d


def run_config(d, reserve, strategy, lift_max):
    n = len(d["mass"])
    keys = ["mass", "inertia", "cg_offset", "gust", "gust_t", "thrust_scale", "gas_kg",
            "gas_T", "stuck_open_t", "stuck_closed_t", "leak_t", "leak_rate", "detect_delay"]
    land, _ = HopSim(n, strategy=strategy, lift_max=lift_max,
                     **{k: d[k] for k in keys}).run()
    safe, hard, ua, nl = classify(land)
    need = NOMINAL_NEED_KG * d["mass"] / MASS
    refused = (d["usable_kg"] < RESERVE_FACTOR * need) if reserve else np.zeros(n, bool)
    bad = (hard | ua | nl) & ~refused
    return dict(refused=refused, bad=bad, ua=ua & ~refused, hard=hard & ~refused,
                drift=np.abs(land["y"]))


def main():
    rng = np.random.default_rng(SEED)
    d = draw(rng, N)
    configs = {
        "A: no reserve check, cut on fault": (False, 1, 9000),
        "B: reserve check, cut on fault": (True, 1, 9000),
        "C: reserve check, isolate + recover": (True, 2, 9000),
        "D: C with 11 kN lift groups": (True, 2, 11000),
    }
    res, rows = {}, []
    # minimum fill fraction that passes the reserve check at nominal mass and 293 K
    fr = np.linspace(0.3, 1.0, 701)
    p = P_FILL_BAR * fr
    usable = fill_mass(p, 293.15) * (1 - (P_MIN_BAR / p) ** (1 / GAMMA))
    ok = fr[usable >= RESERVE_FACTOR * NOMINAL_NEED_KG]
    res["min_fill_fraction_nominal"] = round(float(ok[0]), 3) if ok.size else None
    for name, (reserve, strat, lift) in configs.items():  # same draws d for every configuration
        r = run_config(d, reserve, strat, lift)
        flown = ~r["refused"]
        fault = d["kind"] > 0
        res[name] = {
            "hops_refused_pct": round(100 * r["refused"].mean(), 1),
            "bad_per_flown_hop_pct": round(100 * r["bad"][flown].mean(), 2),
            "bad_no_fault_pct": round(100 * r["bad"][flown & ~fault].mean(), 2),
            "bad_given_stuck_open_pct": round(100 * r["bad"][flown & (d["kind"] == 1)].mean(), 1),
            "bad_given_leak_pct": round(100 * r["bad"][flown & (d["kind"] == 2)].mean(), 1),
            "bad_given_stuck_closed_pct": round(100 * r["bad"][flown & (d["kind"] == 3)].mean(), 1),
            "unsafe_attitude_per_flown_pct": round(100 * r["ua"][flown].mean(), 2),
            "drift_p95_m": round(float(np.nanpercentile(r["drift"][flown], 95)), 2),
            "n_flown": int(flown.sum()),
            "n_flown_stuck_open": int((flown & (d["kind"] == 1)).sum()),
            "n_flown_leak": int((flown & (d["kind"] == 2)).sum()),
            "n_flown_stuck_closed": int((flown & (d["kind"] == 3)).sum()),
        }
        rows.append((name, res[name]))
    ps.setup()
    fig, ax = ps.plt.subplots(figsize=(9.6, 4.2))
    cats = ["No fault", "Stuck-open valve", "Leak", "Stuck-closed valve"]
    keys = ["bad_no_fault_pct", "bad_given_stuck_open_pct", "bad_given_leak_pct",
            "bad_given_stuck_closed_pct"]
    colors = [ps.YELLOW, ps.ORANGE, ps.AQUA, ps.BLUE]
    width = 0.2
    x = np.arange(len(cats))
    for i, ((name, v), c) in enumerate(zip(rows, colors)):
        vals = [v[k] for k in keys]
        ax.bar(x + (i - 1.5) * width, vals, width * 0.92, color=c, label=name)
        for xi, val in zip(x + (i - 1.5) * width, vals):
            ax.text(xi, val + 1.2, f"{val:.0f}", ha="center", fontsize=8.5, color=ps.INK2)
    ax.set_xticks(x, cats)
    ax.set_title("Hard or unsafe landings, share of flown hops in each group (%)")
    ax.legend(loc="upper left", ncol=2)
    ax.set_ylim(0, 128)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.grid(axis="x", visible=False)
    ps.headline(fig, "Reserve check ends gas starvation; recovery saves most faults, but a stuck-closed valve still fails 1 in 3",
                f"{N} random hops per configuration, same draws; faults injected in ~13% of runs (stressed rate)")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig4_monte_carlo.png", dpi=160)
    print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    main()
