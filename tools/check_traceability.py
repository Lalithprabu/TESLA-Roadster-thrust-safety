"""
Check every traceability link in data/*.csv.

  hazard -> safety goal -> functional safety requirement -> technical safety
  requirement -> architecture element and verification item

Exits with status 1 if a link is broken, so it can run in CI.
"""
import csv
import os
import sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUT_OF_SCOPE = {"FSR-3.1"}   # allocated to the steer-by-wire item


def load(name):
    with open(os.path.join(DATA, f"{name}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ids(cell):
    return [x.strip() for x in cell.split(",") if x.strip()]


def main():
    hz, sg = load("hazards"), load("safety_goals")
    fsr, tsr = load("functional_safety_requirements"), load("technical_safety_requirements")
    el, ver = load("architecture_elements"), load("verification")
    sg_ids, fsr_ids = {r["id"] for r in sg}, {r["id"] for r in fsr}
    el_ids, ver_ids = {r["id"] for r in el}, {r["id"] for r in ver}
    errors, report = [], []

    for r in hz:
        if r["safety_goal"] not in sg_ids:
            errors.append(f"{r['id']}: unknown goal {r['safety_goal']}")
    covered = {r["safety_goal"] for r in hz}
    for g in sg_ids - covered:
        errors.append(f"{g}: no hazard leads to this goal")

    for r in fsr:
        if r["safety_goal"] not in sg_ids:
            errors.append(f"{r['id']}: unknown goal {r['safety_goal']}")
    for g in sg_ids - {r["safety_goal"] for r in fsr}:
        errors.append(f"{g}: no functional safety requirement")

    fsr_used = set()
    for r in tsr:
        for f in ids(r["fsr"]):
            if f not in fsr_ids:
                errors.append(f"{r['id']}: unknown FSR {f}")
            fsr_used.add(f)
        for e in ids(r["allocated_to"]):
            if e not in el_ids:
                errors.append(f"{r['id']}: unknown element {e}")
        if not ids(r["allocated_to"]):
            errors.append(f"{r['id']}: not allocated")
        for v in ids(r["verification"]):
            if v not in ver_ids:
                errors.append(f"{r['id']}: unknown verification item {v}")
        if not ids(r["verification"]):
            errors.append(f"{r['id']}: no verification")
    for f in fsr_ids - fsr_used - OUT_OF_SCOPE:
        errors.append(f"{f}: no technical safety requirement")

    tsr_ids = {r["id"] for r in tsr}
    ver_by_id = {v["id"]: v for v in ver}
    # bidirectional: a TSR that names a verification item must be named back by it
    for r in tsr:
        for v in ids(r["verification"]):
            if v in ver_by_id and r["id"] not in ids(ver_by_id[v]["covers"]):
                errors.append(f"{v}: does not list {r['id']} in 'covers'")

    # cybersecurity chain: damage -> threat -> goal -> control -> verification
    ds, ts = load("damage_scenarios"), load("tara")
    cg, cc = load("cybersecurity_goals"), load("cybersecurity_controls")
    ds_ids, cg_ids, cc_ids = {r["id"] for r in ds}, {r["id"] for r in cg}, {r["id"] for r in cc}
    for d in ds:
        for g in ids(d["safety_goal"].replace("-", "")):
            if g not in sg_ids:
                errors.append(f"{d['id']}: unknown safety goal {g}")
    for t in ts:
        for d in ids(t["damage"]):
            if d not in ds_ids:
                errors.append(f"{t['id']}: unknown damage scenario {d}")
        if t["cyber_goal"] not in cg_ids:
            errors.append(f"{t['id']}: unknown cybersecurity goal {t['cyber_goal']}")
        for c_ in ids(t["controls"]):
            if c_ not in cc_ids:
                errors.append(f"{t['id']}: unknown control {c_}")
        if int(t["after_risk"]) > 3:
            errors.append(f"{t['id']}: residual risk {t['after_risk']} above 3 not accepted")
    for g in cg_ids - {t["cyber_goal"] for t in ts}:
        errors.append(f"{g}: no threat scenario")
    for g in cg_ids:
        if not any(g in ids(c_["cyber_goal"]) for c_ in cc):
            errors.append(f"{g}: no control")
    used_cc = {c_ for t in ts for c_ in ids(t["controls"])}
    for c_ in cc:
        if c_["id"] not in used_cc:
            errors.append(f"{c_['id']}: treats no threat")
        v = c_["verification"]
        if v not in ver_by_id:
            errors.append(f"{c_['id']}: unknown verification {v}")
        elif c_["id"] not in ids(ver_by_id[v]["covers"]):
            errors.append(f"{v}: does not list {c_['id']} in 'covers'")

    for v in ver:
        for t in ids(v["covers"]):
            if t not in tsr_ids and t not in cc_ids:
                errors.append(f"{v['id']}: covers unknown {t}")

    status = {}
    for v in ver:
        status[v["status"]] = status.get(v["status"], 0) + 1
    report.append(f"hazards {len(hz)}, goals {len(sg)}, FSR {len(fsr)}, TSR {len(tsr)}, "
                  f"elements {len(el)}, verification items {len(ver)}")
    report.append(f"damage scenarios {len(ds)}, threats {len(ts)}, cybersecurity goals {len(cg)}, controls {len(cc)}")
    report.append("verification status: " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())))
    report.append(f"out of scope: {', '.join(sorted(OUT_OF_SCOPE))}")
    print("\n".join(report))
    if errors:
        print("BROKEN LINKS:\n  " + "\n  ".join(errors))
        sys.exit(1)
    print("traceability check passed: every link resolves")


if __name__ == "__main__":
    main()
