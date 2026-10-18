"""Run every simulation and rebuild the viewer.

Outputs: charts, JSON and CSV in ../results, the animated viewer in ../viewer/index.html.
Requirements, hazards, TARA and traceability live in ../tools/requirements_db.py, not here.
"""
import contextlib
import io
import json
import os
import re
import runpy
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RESULTS = os.path.join(ROOT, "results")
VIEWER = os.path.join(ROOT, "viewer")

import sim1_gas_budget, sim2_stuck_valve, sim3_ftti, sim4_monte_carlo  # noqa: E402,E401
import sim5_landing, sim6_fta_metrics, sim7_component_fmea  # noqa: E402,E401

STEPS = [("sim1", sim1_gas_budget), ("sim2", sim2_stuck_valve), ("sim3", sim3_ftti),
         ("sim4", sim4_monte_carlo), ("sim5", sim5_landing), ("sim6", sim6_fta_metrics),
         ("sim7", sim7_component_fmea)]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>
"""


def build_viewer():
    """Export trajectories and inline them into a single self-contained HTML file."""
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(os.path.join(HERE, "export_visual.py"), run_name="__main__")
    with open("visual_data.json", encoding="utf-8") as f:
        data = f.read()
    with open(os.path.join(HERE, "viewer_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    heights = [round(0.25 * i, 2) for i in range(33)]            # landing-load curve, 0-8 m
    load = dict(h=heights, susp=[round(float(sim5_landing.drop(h, False)[0]), 1) for h in heights],
                bag=[round(float(sim5_landing.drop(h, True)[0]), 1) for h in heights])
    split = tpl.index("</style>") + len("</style>")
    body = tpl[split:].replace("__DATA__", data).replace("__LOAD__", json.dumps(load, separators=(",", ":")))
    page = (HEAD + tpl[:split] + "\n</head>\n<body>\n" + body
            + "\n</body>\n</html>\n")
    left = re.findall(r"__[A-Z]+__", body)
    if left:
        raise SystemExit(f"viewer placeholders not filled: {left}")
    os.makedirs(VIEWER, exist_ok=True)
    with open(os.path.join(VIEWER, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    t0 = time.time()
    os.makedirs(RESULTS, exist_ok=True)
    os.chdir(RESULTS)                      # every script writes to the working directory
    for name, mod in STEPS:
        print(f"running {name} ...", flush=True)
        with contextlib.redirect_stdout(io.StringIO()):
            result = mod.main()
        with open(f"{name}_out.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
    print("building viewer ...", flush=True)
    build_viewer()
    print(f"done in {time.time() - t0:.0f} s: results/ and viewer/index.html")
