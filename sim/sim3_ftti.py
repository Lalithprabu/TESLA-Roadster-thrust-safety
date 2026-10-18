"""
Sim 3 - Fault tolerant time interval (FTTI) for a stuck-open thruster valve.

Sweeps the detection-plus-isolation delay and the moment in the manoeuvre at
which the valve sticks. For each delay it reports the share of fault timings
that end in a hard landing (> 5 m/s) or an unsafe attitude (> 30 deg).
Run for the baseline lift-group size (9 kN) and an up-sized group (11 kN),
because after one outer group is isolated the inner pair must still lift the car.
"""
import json
import numpy as np
from common import HopSim, classify
import plotstyle as ps

DELAYS = np.round(np.arange(0.0, 0.601, 0.01), 3)
FAULT_TIMES = np.round(np.arange(0.6, 3.01, 0.05), 3)


def sweep(lift_max):
    dd, ff = np.meshgrid(DELAYS, FAULT_TIMES)
    sim = HopSim(dd.size, strategy=2, stuck_open_t=ff.ravel(), detect_delay=dd.ravel(),
                 lift_max=lift_max)
    land, _ = sim.run()
    safe, hard, ua, nl = classify(land)
    bad = (~safe).reshape(dd.shape)
    unsafe_att = ua.reshape(dd.shape)
    return bad.mean(axis=0), unsafe_att.mean(axis=0)


def first_delay(frac, level=0.0):
    idx = np.where(frac > level)[0]
    return float(DELAYS[idx[0]]) if idx.size else None


def main():
    ps.setup()
    res = {}
    fig, ax = ps.plt.subplots(figsize=(9.6, 4.2))
    for lift, color in ((9000, ps.ORANGE), (11000, ps.BLUE)):
        bad, ua = sweep(lift)
        ax.plot(DELAYS * 1000, bad * 100, color=color,
                label=f"{lift/1000:.0f} kN per lift group")
        res[f"{lift}N"] = {
            "share_bad_at_20ms_pct": round(float(bad[DELAYS == 0.02][0] * 100), 1),
            "share_bad_at_100ms_pct": round(float(bad[DELAYS == 0.10][0] * 100), 1),
            "share_bad_at_300ms_pct": round(float(bad[DELAYS == 0.30][0] * 100), 1),
            "first_delay_with_unsafe_attitude_ms": (None if first_delay(ua) is None
                                                    else round(first_delay(ua) * 1000)),
            "first_delay_bad_over_10pct_ms": (None if first_delay(bad, 0.10) is None
                                              else round(first_delay(bad, 0.10) * 1000)),
        }
    ax.axvline(20, color=ps.INK2, lw=1)
    ax.text(26, 12, "TSR-09\ntarget 20 ms", color=ps.INK2, fontsize=9)
    ax.set_xlabel("Detection + isolation delay (ms)")
    ax.set_title("Share of fault timings ending in a hard or unsafe landing (%)")
    ax.set_xlim(0, 600)
    ax.legend(loc="upper left", bbox_to_anchor=(0.08, 1.0))
    ps.headline(fig, "Bad outcomes climb after ~180 ms with 9 kN groups and ~400 ms with 11 kN groups",
                f"Stuck-open outer valve injected at {len(FAULT_TIMES)} moments from 0.6 s to 3.0 s; isolate-and-recover strategy")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig3_ftti.png", dpi=160)
    print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    main()
