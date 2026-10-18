"""Export trajectories from the hop simulator for the animated viewer (50 Hz)."""
import json
import numpy as np
from common import HopSim, classify, fill_mass, P_FILL_BAR, LIFT_D

STEP = 10   # dt 0.002 s x 10 = 50 Hz


def run(label, group, note, fault=None, fault_t=None, delay=0.02, strategy=2, **kw):
    sim = HopSim(1, strategy=strategy, detect_delay=delay, **kw)
    land, h = sim.run(record=True)
    safe, hard, ua, nl = classify(land)
    outcome = "safe" if safe[0] else ("hard" if hard[0] else ("unsafe" if ua[0] else "none"))
    fr = h[::STEP] + [h[-1]]
    frames = [[round(x[0], 3), round(float(x[1][0]), 3), round(float(x[2][0]), 3),
               round(float(x[3][0]), 4)] + [round(float(f) / 1000, 2) for f in x[5][0]] +
              [round(float(x[6][0]), 1), round(float(x[7][0]) - 273.15, 1), round(float(x[8][0]), 1)]
              for x in fr]
    return dict(id=label, group=group, note=note, fault=fault, faultT=fault_t, delay=delay,
                strategy=strategy, outcome=outcome,
                land=dict(t=round(float(land["t"][0]), 2), roll=round(float(np.degrees(land["phi"][0])), 1),
                          vz=round(float(land["vz"][0]), 2), vy=round(float(land["vy"][0]), 2),
                          y=round(float(land["y"][0]), 2), gas=round(float(land["gas_used"][0]), 1)),
                frames=frames)


S = []
S.append(run("nominal", "Reference", "No fault. Climb to 4.5 m, 360° roll, controlled landing.", strategy=0))
FT = 1.45
S.append(run("so-undetected", "Stuck-open valve", "Outer-right valve sticks open while inverted. Nothing reacts.",
             "Stuck open, outer right", FT, strategy=0, stuck_open_t=FT))
S.append(run("so-cut", "Stuck-open valve", "Safety monitor closes the master valves 20 ms after the fault.",
             "Stuck open, outer right", FT, strategy=1, stuck_open_t=FT))
for d in (0.02, 0.1, 0.2, 0.3, 0.4):
    S.append(run(f"so-recover-{int(d*1000)}", "Stuck-open valve",
                 f"Faulty line isolated after {int(d*1000)} ms, then level, descend and land.",
                 "Stuck open, outer right", FT, delay=d, strategy=2, stuck_open_t=FT))
# stuck-closed: show one recovered and one failed case from a scan of fault times
sc = []
for tf in np.arange(0.9, 2.3, 0.05):
    r = run("tmp", "", "", strategy=2, stuck_closed_t=float(tf))
    sc.append((round(float(tf), 2), r["outcome"]))
good = next(t for t, o in sc if o == "safe")
bad = 1.45
S.append(run("sc-ok", "Stuck-closed valve", f"Outer-left valve sticks closed at {good:.2f} s; recovery succeeds.",
             "Stuck closed, outer left", round(good, 2), strategy=2, stuck_closed_t=good))
S.append(run("sc-bad", "Stuck-closed valve", f"Outer-left valve sticks closed at {bad:.2f} s; not enough roll authority left.",
             "Stuck closed, outer left", round(bad, 2), strategy=2, stuck_closed_t=bad))
S.append(run("leak-cut", "Leak", "30 kg/s leak at 1.3 s. Monitor closes all gas.",
             "Leak 30 kg/s", 1.3, strategy=1, leak_t=1.3, leak_rate=30.0))
S.append(run("leak-recover", "Leak", "30 kg/s leak at 1.3 s. Recovery uses the remaining gas to land.",
             "Leak 30 kg/s", 1.3, strategy=2, leak_t=1.3, leak_rate=30.0))
low = fill_mass(P_FILL_BAR * 0.45)
S.append(run("starved", "Gas reserve", "45% fill, no reserve check. The hop starts without enough air.",
             None, None, strategy=0, gas_kg=low))
S.append(run("gust", "Crosswind", "12 m/s side gust hits at the inverted point. No fault.",
             None, None, strategy=0, gust=12.0, gust_t=1.45))
meta = dict(liftD=LIFT_D.tolist(), liftMax=9.0, dt=0.02,
            sc_scan=[[round(t, 2), o] for t, o in sc])
json.dump(dict(meta=meta, scenarios=S), open("visual_data.json", "w"), separators=(",", ":"))
for s in S:
    print(s["id"], s["outcome"], s["land"])
