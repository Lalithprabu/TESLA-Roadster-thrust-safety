"""
Sim 5 - Landing impact: suspension alone vs suspension plus an external airbag.

One-degree-of-freedom drop of the body onto its suspension. The suspension is a
linear spring-damper with 0.20 m travel, then a stiff bump stop (structure).
The airbag is a vented bag under the floor that fires at 1 m and offers up to
0.5 m of stroke; its gas is compressed polytropically and vents through an orifice.
Outputs peak and average body deceleration versus drop height.
"""
import json
import numpy as np
from common import MASS, G, P_ATM
import plotstyle as ps

K_SUSP = 140e3        # N/m total wheel rate, ASSUMED
C_SUSP = 18e3         # N s/m total damping, ASSUMED
TRAVEL = 0.20         # m
K_STOP = 3.0e6        # N/m bump stop / structure, ASSUMED
BAG_AREA = 2.6        # m^2 contact footprint, ASSUMED
BAG_STROKE = 0.50     # m
BAG_P0 = 1.25e5       # Pa absolute inflation pressure, ASSUMED
P_RELIEF = 1.80e5     # Pa absolute, vent (relief) opening pressure, ASSUMED
N_POLY = 1.3


def drop(height, airbag, dt=2e-5):
    v = -np.sqrt(2 * G * height)           # velocity at first contact (bag or tyre)
    x = BAG_STROKE if airbag else 0.0      # +x = distance above tyre contact
    bag_V = BAG_AREA * BAG_STROKE
    bag_m = BAG_P0 * bag_V / (287.05 * 293.15)
    bag_m0 = bag_m
    acc_hist, t = [], 0.0
    while True:
        F = 0.0
        if airbag and x <= BAG_STROKE and bag_m > 0:
            V = max(BAG_AREA * max(x, 0.0), 0.01)
            # polytropic compression of the trapped gas from its inflated state
            p = BAG_P0 * (bag_m / bag_m0 * bag_V / V) ** N_POLY
            if p > P_RELIEF:               # relief vents hold the bag at P_RELIEF
                bag_m = bag_m0 * (V / bag_V) * (P_RELIEF / BAG_P0) ** (1 / N_POLY)
                p = P_RELIEF
            F += max(p - P_ATM, 0.0) * BAG_AREA
        if x < 0:                          # tyres/suspension compressing
            comp = -x
            F += K_SUSP * comp + (C_SUSP * (-v) if v < 0 else 0.0)
            if comp > TRAVEL:
                F += K_STOP * (comp - TRAVEL)
        a = F / MASS - G
        if F > 0:
            acc_hist.append(a + G)
        v += a * dt
        x += v * dt
        t += dt
        if v >= 0 and x < 0.0 or t > 2.0:
            break
    acc = np.array(acc_hist) / G
    peak = acc.max() if acc.size else 0.0
    mean = acc[acc > 0.2].mean() if (acc > 0.2).any() else 0.0
    return peak, mean


def main():
    heights = np.arange(0.5, 6.01, 0.25)
    res = {"suspension_only": [], "with_airbag": []}
    for h in heights:
        res["suspension_only"].append(drop(h, False))
        res["with_airbag"].append(drop(h, True))
    so = np.array(res["suspension_only"]); ab = np.array(res["with_airbag"])
    ps.setup()
    fig, ax = ps.plt.subplots(figsize=(9.6, 4.0))
    ax.plot(heights, so[:, 0], color=ps.ORANGE, label="Suspension only")
    ax.plot(heights, ab[:, 0], color=ps.BLUE, label="Suspension + external airbag")
    ax.set_xlabel("Drop height (m), car upright")
    ax.set_title("Peak body deceleration (g)")
    ax.legend(loc="upper left")
    i5 = int(np.argmin(np.abs(heights - 5.0)))
    ax.annotate(f"{so[i5,0]:.0f} g", (5, so[i5, 0]), textcoords="offset points", xytext=(6, 6), color=ps.INK2)
    ax.annotate(f"{ab[i5,0]:.0f} g", (5, ab[i5, 0]), textcoords="offset points", xytext=(6, 6), color=ps.INK2)
    ps.headline(fig, f"From 5 m the airbag cuts peak body load from {so[i5,0]:.0f} g to {ab[i5,0]:.0f} g",
                "1,850 kg car, 0.20 m suspension travel then bump stop; 0.5 m airbag with 1.8 bar relief vents")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig5_landing.png", dpi=160)
    out = {f"{h:.2f}m": {"susp_peak_g": round(float(a[0]), 1), "susp_mean_g": round(float(a[1]), 1),
                         "airbag_peak_g": round(float(b[0]), 1), "airbag_mean_g": round(float(b[1]), 1)}
           for h, a, b in zip(heights, so, ab) if abs(h - round(h)) < 1e-9}
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
