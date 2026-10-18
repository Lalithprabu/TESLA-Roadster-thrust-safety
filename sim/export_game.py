"""Export trajectories for the reaction-time game (viewer/play.html).

One stuck-open thruster valve at FAULT_T seconds into the 4.5 m hop. For every fault reaction
time in GRID the simulator runs the isolate-and-recover strategy; the page plays the run that
matches the player's measured time (rounded UP to the next grid step, so it never flatters).
Frames are [t, y, z, roll, F1..F4 (kN per lift thruster)] at 50 Hz.
"""
import json
import numpy as np
from common import HopSim, classify, LIFT_D

STEP = 20                      # dt 0.002 s x 20 = 25 Hz, the page interpolates
# Fault moments the page picks from at random, so the player cannot time it from take-off.
# 1.45-1.70 s is the inverted part of the roll; the isolation limit is 180-200 ms for all of them.
FAULT_TIMES = [1.45, 1.50, 1.55, 1.60, 1.65, 1.70]
GRID = [round(0.02 * i, 2) for i in range(1, 24)]          # 20 ... 460 ms


def run(delay, strategy, fault_t):
    sim = HopSim(1, strategy=strategy, detect_delay=delay, stuck_open_t=fault_t)
    land, h = sim.run(record=True)
    safe, hard, ua, nl = classify(land)
    outcome = "safe" if safe[0] else ("hard" if hard[0] else ("unsafe" if ua[0] else "none"))
    fr = h[::STEP] + [h[-1]]
    frames = [[round(x[0], 3), round(float(x[1][0]), 2), round(float(x[2][0]), 2), round(float(x[3][0]), 3)]
              + [round(float(f) / 1000, 1) for f in x[5][0][:4]] for x in fr]
    return dict(d=delay, outcome=outcome, t=round(float(land["t"][0]), 2),
                roll=round(float(np.degrees(land["phi"][0])), 1), vz=round(abs(float(land["vz"][0])), 1),
                frames=frames)


def build():
    out = []
    for ft in FAULT_TIMES:
        runs = [run(d, 2, ft) for d in GRID]
        never = run(0.02, 0, ft)                       # nothing reacts: the car hits the ground
        first_bad = next(r["d"] for r in runs if r["outcome"] != "safe")
        last_safe = max(r["d"] for r in runs if r["d"] < first_bad)
        out.append(dict(faultT=ft, runs=runs, never=never, limitMs=round(last_safe * 1000),
                        firstBadMs=round(first_bad * 1000)))
    return dict(liftD=LIFT_D.tolist(), grid=GRID, cases=out)


if __name__ == "__main__":
    d = build()
    json.dump(d, open("game_data.json", "w"), separators=(",", ":"))
    for c in d["cases"]:
        print(c["faultT"], "limit", c["limitMs"], "first bad", c["firstBadMs"], "no-reaction lands at", c["never"]["t"])
