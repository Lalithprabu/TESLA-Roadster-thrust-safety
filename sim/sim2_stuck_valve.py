"""
Sim 2 - Stuck-open outer thruster valve while inverted mid-roll.

Compares three monitor strategies after a 20 ms detection delay:
  0  undetected   - controller fights the stuck valve
  1  cut all gas  - safety monitor closes the master valves at once
  2  isolate + recover - close only the faulty line, level the car, land, then cut
"""
import json
import numpy as np
from common import HopSim, classify
import plotstyle as ps

FAULT_T = 1.45          # s, car is close to inverted (phi ~ 180 deg)
DELAY = 0.02            # s
LABELS = {0: "Undetected", 1: "Cut all gas", 2: "Isolate line, recover"}
COLORS = {0: ps.YELLOW, 1: ps.ORANGE, 2: ps.BLUE}


def run_case(strategy, fault=True):
    sim = HopSim(1, strategy=strategy, stuck_open_t=FAULT_T if fault else np.inf,
                 detect_delay=DELAY)
    land, hist = sim.run(record=True)
    t = np.array([h[0] for h in hist])
    z = np.array([h[2][0] for h in hist])
    phi = np.degrees(np.array([h[3][0] for h in hist]))
    return land, t, z, phi


def main():
    ps.setup()
    fig, axes = ps.plt.subplots(1, 2, figsize=(9.6, 4.0))
    out = {}
    land, t, z, phi = run_case(0, fault=False)
    axes[0].plot(t, phi, color=ps.GREY, lw=1.4, ls="--", label="No fault")
    axes[1].plot(t, z, color=ps.GREY, lw=1.4, ls="--", label="No fault")
    out["no_fault"] = land
    for s in (0, 1, 2):
        land, t, z, phi = run_case(s)
        out[LABELS[s]] = land
        axes[0].plot(t, phi, color=COLORS[s], label=LABELS[s])
        axes[1].plot(t, z, color=COLORS[s], label=LABELS[s])
        axes[1].plot(t[-1], 0, "o", color=COLORS[s], ms=8, mec=ps.SURFACE, mew=2)
    axes[0].axvline(FAULT_T, color=ps.INK2, lw=1)
    axes[0].text(FAULT_T + 0.05, 20, "valve sticks open", color=ps.INK2, fontsize=9)
    axes[0].set_title("Roll angle (degrees)")
    axes[0].set_yticks([0, 180, 360, 540, 720, 900])
    axes[1].set_title("Height (m)")
    for ax in axes:
        ax.set_xlabel("Time (s)")
        ax.set_xlim(0, 4.6)
    axes[1].set_ylim(-0.2, 6.5)
    axes[1].legend(loc="upper right")
    ps.headline(fig, "Cutting all gas mid-roll lands the car on its roof; isolating the line lands it upright",
                "Outer-right valve sticks fully open at 1.45 s (car inverted); 20 ms detection delay")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig2_stuck_valve.png", dpi=160)
    table = {}
    for k, land in out.items():
        safe, hard, ua, nl = classify(land)
        table[k] = {
            "touchdown_s": round(float(land["t"][0]), 2),
            "roll_at_touchdown_deg": round(float(np.degrees(land["phi"][0])), 1),
            "vertical_speed_m_s": round(float(land["vz"][0]), 2),
            "outcome": "safe" if safe[0] else ("hard landing" if hard[0] else "unsafe attitude"),
            "gas_used_kg": round(float(land["gas_used"][0]), 1),
        }
    print(json.dumps(table, indent=2))
    return table


if __name__ == "__main__":
    main()
