"""
Sim 7 - Representative component-level FMEA and FMEDA.

Tesla has published no bill of materials, so this uses REPRESENTATIVE parts
typical for the job (automotive solenoid valves, strain-gauge pressure sensors,
lockstep microcontrollers, Type IV COPVs). Failure rates are representative
magnitudes for automotive and industrial parts, not values taken from a named
handbook table; replace them with supplier data before any compliance claim.

Part A  Design FMEA rows (S, O, D, action priority per the AIAG-VDA DFMEA table).
Part B  FMEDA for safety goal SG1 (no unintended thrust): SPFM, LFM and PMHF,
        with PMHF from the minimal cut sets of the SG1 fault tree.
"""
import csv
import itertools
import json
import numpy as np
import plotstyle as ps

T_LIFE = 10_000.0      # h, vehicle operating life
TAU_START = 1.0        # h, between power-on tests (one drive cycle)
TAU_CONT = 0.001       # h, continuous monitoring (about 4 s)

# ------------------------------------------------------------------ helpers
def occurrence(fit, qty=1):
    """This study's mapping from lifetime probability per vehicle to an O rating."""
    p = fit * qty * 1e-9 * T_LIFE
    for lim, o in ((1e-2, 8), (1e-3, 6), (1e-4, 4), (1e-5, 3), (1e-6, 2)):
        if p >= lim:
            return o
    return 1


AP_TABLE = {  # AIAG-VDA DFMEA action priority; columns D = 7-10, 5-6, 2-4, 1
    "S9": {"O8": "HHHH", "O6": "HHHH", "O4": "HHHM", "O2": "HMLL", "O1": "LLLL"},
    "S7": {"O8": "HHHH", "O6": "HHHM", "O4": "HMMM", "O2": "MMLL", "O1": "LLLL"},
    "S4": {"O8": "HHMM", "O6": "MMML", "O4": "MLLL", "O2": "LLLL", "O1": "LLLL"},
    "S2": {"O8": "MMLL", "O6": "LLLL", "O4": "LLLL", "O2": "LLLL", "O1": "LLLL"},
}


def action_priority(s, o, d):
    if s <= 1:
        return "L"
    sk = "S9" if s >= 9 else "S7" if s >= 7 else "S4" if s >= 4 else "S2"
    ok = "O8" if o >= 8 else "O6" if o >= 6 else "O4" if o >= 4 else "O2" if o >= 2 else "O1"
    col = 0 if d >= 7 else 1 if d >= 5 else 2 if d >= 2 else 3
    return AP_TABLE[sk][ok][col]


# ------------------------------------------------------------------ Part A: DFMEA
# component, qty, FIT per unit, [(mode, share, effect, S, goal, cause, prevention,
#                               design verification, D, field diagnostic, DC)]
DFMEA = [
    ("COPV (Type IV, ~100 L, 400 bar)", 6, 10, [
        ("Rupture", 0.05, "Blast and fragments", 10, "SG2", "Fatigue, impact or heat damage",
         "Burst ratio >= 2.25, impact shield, segregation", "Burst, cycle, fire, drop tests (GTR 13 style)", 2,
         "Impact log, pressure-rate monitor", 0.60),
        ("Liner or boss leak", 0.95, "Gas loss; reserve error in flight", 9, "SG6", "Liner fatigue, seal ageing",
         "Qualified seals, cold-soak qualification", "Leak and permeation test after cold cycling", 3,
         "Pressure decay vs model", 0.95)]),
    ("Pressure relief device (burst disc + thermal)", 6, 5, [
        ("Opens early", 0.6, "Uncontrolled vent; possible net thrust", 8, "SG2", "Disc fatigue",
         "Rating margin, thrust-neutral diffuser", "Cycle test of discs", 3, "Pressure drop", 0.99),
        ("Fails to open in fire", 0.4, "Tank rupture in fire", 10, "SG2", "Corrosion, wrong part fitted",
         "Dual thermal and pressure PRD, poka-yoke fitting", "Bonfire test", 2, "None in service", 0.0)]),
    ("Group isolation valve (NC solenoid)", 3, 100, [
        ("Stuck open", 0.15, "Group cannot be isolated after crash", 9, "SG2", "Seat contamination, ice",
         "Filter, dry air, heated body", "Contamination and cold-soak test", 3, "Power-on leak-down test", 0.99),
        ("Stuck closed", 0.35, "Group gas unavailable; lower reserve", 7, "SG6", "Coil open, armature seizure",
         "Coil derating", "Life test", 3, "Pre-arm function test", 0.99)]),
    ("Master valve A / B (NC solenoid, series)", 2, 100, [
        ("Stuck open or seat leak", 0.40, "One SG1 barrier lost (latent)", 10, "SG1", "Seat damage, ice, debris",
         "Different suppliers for A and B, filter, heated body", "Contamination, cold-soak, life tests", 3,
         "Inter-stage and manifold pressure, power-on leak-down", 0.99),
        ("Closes in flight (coil or power loss)", 0.45, "All thrust lost mid-hop", 10, "SG6", "Coil open, driver or supply loss",
         "Dual-wound coil, hold-up energy store (TSR-21)", "HIL power-loss injection", 3, "Coil current monitor", 0.90)]),
    ("Pressure regulator (dome-loaded)", 3, 60, [
        ("Fails high", 0.3, "Over-pressure in manifold; thrust excess", 8, "SG5", "Seat leak, creep",
         "Second stage plus relief valve", "Endurance test", 3, "Manifold pressure", 0.99),
        ("Fails low or freezes", 0.4, "Thrust shortfall in flight", 10, "SG6", "Icing at high flow",
         "Dry air, heated regulator", "Full-flow cold discharge test", 3, "Manifold pressure vs command", 0.95)]),
    ("Line isolation valve (NC solenoid)", 4, 100, [
        ("Stuck open", 0.15, "Stuck thruster cannot be isolated", 10, "SG6", "Seat contamination",
         "Filter, heated body", "Contamination test", 3, "Pre-arm function test", 0.99),
        ("Stuck closed", 0.35, "Lift group lost", 10, "SG6", "Coil open, seizure",
         "Coil derating, dual-wound coil", "Life test", 3, "Pre-arm function test", 0.99)]),
    ("Thruster valve (fast solenoid)", 10, 80, [
        ("Stuck open", 0.15, "Asymmetric thrust; latent SG1 barrier loss", 10, "SG1/SG6", "Armature wear, ice",
         "Heated valve, dry air", "Life and cold-cycle test", 3, "Line pressure vs command; pre-arm test", 0.95),
        ("Stuck closed", 0.35, "Roll authority lost (weak spot)", 10, "SG6", "Coil open, seizure",
         "Derated coil; individually controlled nozzles (TSR-17)", "Life test, HIL", 3, "Pre-arm function test", 0.95),
        ("Slow response", 0.15, "Control degradation", 7, "SG6", "Wear, low voltage",
         "Voltage regulation", "Response-time test", 4, "Command vs pressure timing", 0.90),
        ("Seat leak", 0.20, "Small unwanted thrust; latent SG1", 6, "SG1", "Seat erosion",
         "Seat material selection", "Leak test", 4, "Power-on leak-down", 0.90)]),
    ("Pressure transducer (strain gauge)", 8, 40, [
        ("Drift or stuck in range", 0.5, "Wrong reserve estimate; hop starts short of gas", 9, "SG6", "Ageing, thermal shock",
         "Dissimilar dual sensors per group", "Thermal cycling", 3, "Cross-check with second sensor and gas model", 0.99),
        ("Open or short", 0.5, "Signal lost", 6, "SG6", "Connector, wire bond",
         "Automotive-grade connectors", "Vibration test", 3, "Range check", 0.99)]),
    ("IMU (MEMS)", 3, 100, [
        ("Wrong output", 0.4, "Wrong attitude corrections", 10, "SG6", "MEMS stiction, shock",
         "Three-way voting plus dissimilar monitor IMU", "Shock, vibration, HIL", 3, "Voting", 0.99),
        ("Loss of output", 0.6, "One attitude source lost", 6, "SG6", "Supply, interface",
         "Redundant supply", "HIL", 3, "Timeout", 0.99)]),
    ("Thrust control unit (lockstep MCU)", 1, 300, [
        ("Wrong output", 0.2, "Erroneous thrust or valve command", 10, "SG1/SG6", "Random hardware fault",
         "Lockstep cores, ECC memory", "Fault injection", 2, "Lockstep compare, monitor plausibility", 0.99),
        ("Loss of function in flight", 0.3, "No flight control until backup acts", 10, "SG6", "Reset, latch-up, clock",
         "Fail-operational backup controller (TSR-22)", "HIL fault injection", 3, "Watchdog", 0.99)]),
    ("Safety monitor (dissimilar MCU)", 1, 200, [
        ("Wrong output (enable)", 0.2, "One SG1 barrier lost", 10, "SG1", "Random hardware fault",
         "Simple code, self-test, dissimilar part", "Fault injection", 2, "Inter-stage pressure, TCU cross-check", 0.90),
        ("Loss of function in flight", 0.3, "Master valve A hold lost", 10, "SG6", "Reset, supply",
         "Hold-up energy store (TSR-21)", "HIL fault injection", 3, "TCU watchdog of monitor", 0.99)]),
    ("High-side switch, master valve A / B", 2, 20, [
        ("Short (stuck on)", 0.3, "One SG1 barrier lost", 10, "SG1", "Overstress",
         "Derating", "Fault injection", 3, "Output read-back", 0.99),
        ("Open", 0.5, "Master valve closes in flight", 10, "SG6", "Bond failure",
         "Dual-wound coil, second driver (TSR-21)", "HIL", 3, "Coil current", 0.99)]),
    ("Low-side valve driver", 10, 10, [
        ("Short (valve on)", 0.2, "Behaves as stuck-open valve", 10, "SG1/SG6", "Overstress",
         "Derating, supply enable from monitor", "Fault injection", 3, "Driver diagnostics", 0.95),
        ("Open (valve off)", 0.5, "Behaves as stuck-closed valve", 10, "SG6", "Bond failure",
         "Derating", "Fault injection", 3, "Open-load detection", 0.95)]),
    ("Arm-line harness, each channel", 2, 10, [
        ("Short to battery", 0.2, "One SG1 barrier lost", 10, "SG1", "Chafing",
         "Separate routing, protected conduit", "Harness review, vibration", 4, "Read-back", 0.90)]),
    ("Satellite and beacon receivers", 2, 150, [
        ("False position or replayed beacon", 0.1, "Zone wrongly authorised (needs both)", 8, "SG1", "Interference, spoofing",
         "Two independent sources, signed beacon", "Spoofing test", 3, "Cross-check with inertial data", 0.90)]),
    ("Low-voltage supply, thrust domain", 2, 50, [
        ("Loss in flight", 0.5, "Valves close; thrust lost", 10, "SG6", "Converter fault, connector",
         "Two feeds, hold-up energy store (TSR-21)", "HIL power-loss test", 3, "Voltage monitor", 0.99)]),
]


def build_dfmea():
    rows = []
    for comp, qty, fit, modes in DFMEA:
        for (mode, share, effect, s, goal, cause, prev, ver, d, diag, dc) in modes:
            lam = fit * share
            o = occurrence(lam, qty)
            rows.append(dict(component=comp, qty=qty, mode=mode, effect=effect, S=s, goal=goal, cause=cause,
                             prevention=prev, O=o, design_verification=ver, D=d, AP=action_priority(s, o, d),
                             field_diagnostic=diag, DC_pct=round(dc * 100), FIT_mode_total=round(lam * qty, 2)))
    return rows


# ------------------------------------------------------------------ Part B: SG1 FMEDA
# Basic events of the SG1 fault tree: (FIT acting, latent DC, test interval h)
EVENTS = {
    "vA_open":   (40.0, 0.99, TAU_START),       # master valve A stuck open or leaking
    "vB_open":   (40.0, 0.99, TAU_START),
    "hssA":      (6.0, 0.99, TAU_CONT),         # high-side switch short
    "hssB":      (6.0, 0.99, TAU_CONT),
    "harnA":     (2.0, 0.90, TAU_CONT),         # arm line short to battery
    "harnB":     (2.0, 0.90, TAU_CONT),
    "mon_wrong": (40.0 * 0.10, 0.99, TAU_CONT),  # monitor wrong enable, after self-test (90 %)
    "tcu_wrong": (60.0 * 0.01, 0.99, TAU_CONT),  # TCU wrong output, after lockstep (99 %)
    "hssEN":     (6.0, 0.99, TAU_CONT),         # driver-supply enable switch short
    "lsd":       (20.0, 0.95, TAU_START),       # any low-side driver short (10 x 2 FIT)
    "tv_open":   (120.0 + 160.0, 0.95, TAU_START),  # any thruster valve stuck open or leaking
    # common-cause events (beta-factor model, see dependent failure analysis)
    "ccf_masters": (0.02 * 40.0, 0.99, TAU_START),  # ice or debris holds both master valves open
    "ccf_computers": (0.01 * 0.6, 0.99, TAU_CONT),  # supply or EMC event drives both computers wrong
}
# SG1 tree: TOP = A AND B AND C
GATES = {
    "TOP": ("AND", ["A", "B", "C"]),
    "A": ("OR", ["vA_open", "hssA", "harnA", "mon_wrong", "ccf_masters", "ccf_computers"]),
    "B": ("OR", ["vB_open", "hssB", "harnB", "tcu_wrong", "ccf_masters", "ccf_computers"]),
    "C": ("OR", ["tv_open", "ELEC"]),
    "ELEC": ("AND", ["DRV", "EN"]),
    "DRV": ("OR", ["lsd", "tcu_wrong", "ccf_computers"]),
    "EN": ("OR", ["mon_wrong", "hssEN", "ccf_computers"]),
}


def cut_sets(node):
    if node in EVENTS:
        return [frozenset([node])]
    kind, kids = GATES[node]
    sets = [cut_sets(k) for k in kids]
    if kind == "OR":
        out = [s for group in sets for s in group]
    else:
        out = [frozenset().union(*combo) for combo in itertools.product(*sets)]
    out = list(set(out))
    return [s for s in out if not any(o < s for o in out)]   # keep minimal sets


def q(ev):
    lam, dc, tau = EVENTS[ev]
    return lam * 1e-9 * (dc * tau / 2 + (1 - dc) * T_LIFE / 2)


def cs_rate_fit(cs):
    """Rate of reaching the top event through this cut set: the last fault arrives last."""
    total = 0.0
    for k in cs:
        others = np.prod([q(m) for m in cs if m != k]) if len(cs) > 1 else 1.0
        total += EVENTS[k][0] * others
    return total


def fmeda_sg1(dfmea_rows):
    sr = sum(r["FIT_mode_total"] for r in dfmea_rows if "SG1" in r["goal"])
    sr += sum(r["FIT_mode_total"] for r in dfmea_rows
              if r["component"].startswith(("Master", "Thruster valve", "Low-side", "High-side",
                                            "Thrust control", "Safety monitor", "Arm-line"))
              and "SG1" not in r["goal"])   # safe faults of SG1 elements count in the total
    mpf = sum(v[0] for v in EVENTS.values())
    mpf_latent = sum(v[0] * (1 - v[1]) for v in EVENTS.values())
    css = cut_sets("TOP")
    singles = [c for c in css if len(c) == 1]
    spf = sum(EVENTS[next(iter(c))][0] for c in singles)
    contrib = sorted(((" + ".join(sorted(c)), cs_rate_fit(c), len(c)) for c in css), key=lambda x: (-x[1], x[0]))   # name breaks ties: repeatable order
    pmhf = sum(c[1] for c in contrib)
    return dict(lambda_safety_related_FIT=round(sr, 1), lambda_MPF_FIT=round(mpf, 1),
                lambda_latent_FIT=round(mpf_latent, 2), SPF_FIT=spf,
                SPFM_pct=round(100 * (1 - spf / sr), 2),
                LFM_pct=round(100 * (1 - mpf_latent / (sr - spf)), 2),
                PMHF_FIT=float(f"{pmhf:.3g}"), n_cut_sets=len(css),
                order_counts={str(k): sum(1 for c in css if len(c) == k) for k in (1, 2, 3, 4)},
                top_cut_sets=[dict(cut_set=c, FIT=float(f"{f:.3g}"), order=o) for c, f, o in contrib[:8]],
                targets_ASIL_D=dict(SPFM_pct=99, LFM_pct=90, PMHF_FIT=10))


def main():
    rows = build_dfmea()
    with open("component_fmea.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    m = fmeda_sg1(rows)
    with open("sg1_cut_sets.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["cut_set", "order", "FIT"])
        for c in m["top_cut_sets"]:
            w.writerow([c["cut_set"], c["order"], c["FIT"]])
    ap = {k: sum(1 for r in rows if r["AP"] == k) for k in "HML"}
    out = dict(n_rows=len(rows), action_priority=ap, sg1=m,
               high_priority=[f'{r["component"]}: {r["mode"]}' for r in rows if r["AP"] == "H"])
    ps.setup()
    fig, ax = ps.plt.subplots(figsize=(9.6, 3.9))
    top = m["top_cut_sets"][:6][::-1]
    names = dict(ccf_computers="common cause, both computers", ccf_masters="common cause, both master valves",
                 tv_open="thruster valve open", mon_wrong="monitor wrong", tcu_wrong="TCU wrong",
                 vA_open="master A open", vB_open="master B open", harnA="arm line A short",
                 harnB="arm line B short", hssA="switch A short", hssB="switch B short")
    labels = [" + ".join(names.get(e, e) for e in c["cut_set"].split(" + ")) for c in top]
    labels = [l[0].upper() + l[1:] for l in labels]
    vals = [c["FIT"] for c in top]
    ax.barh(range(len(top)), vals, color=ps.BLUE, height=0.55)
    for i, v in enumerate(vals):
        ax.text(v * 1.15, i, f"{v:.1e} FIT", va="center", color=ps.INK2, fontsize=9)
    ax.set_yticks(range(len(top)), labels)
    ax.set_xscale("log"); ax.set_xlim(min(vals) / 3, max(vals) * 20)
    ax.set_xlabel("Contribution to PMHF (FIT, log scale)")
    ax.grid(axis="y", visible=False)
    ps.headline(fig, "Common-cause faults dominate the tiny residual risk of unintended thrust",
                f"SG1 minimal cut sets, representative failure rates; total PMHF {m['PMHF_FIT']:.1e} FIT vs 10 FIT target")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig7_sg1_cut_sets.png", dpi=160)
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
