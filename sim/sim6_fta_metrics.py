"""
Sim 6 - Quantitative fault tree and hardware architectural metrics.

Part A: FMEDA-style metrics for safety goal SG1 (no unintended thrust), using
        ASSUMED failure rates (FIT = failures per 1e9 h) and diagnostic coverages.
        Computes SPFM, LFM and a simplified PMHF and compares them with the
        ISO 26262-5 targets for ASIL D (SPFM >= 99 %, LFM >= 90 %, PMHF < 10 FIT).

Part B: probability of a hard or unsafe landing per hop, combining
        latent-fault probabilities (pre-arm test coverage, lifetime) with the
        conditional outcomes measured in Sim 4. Zero counts use the rule of three
        (95 % upper bound = 3/n) so the estimate stays conservative.
"""
import json
import numpy as np
import plotstyle as ps

T_LIFE_H = 10_000.0          # vehicle operating lifetime (h), ASSUMED
TEST_INTERVAL_H = 1.0        # pre-arm checks run before every arming (~1 h of use), ASSUMED

# ---------------------------------------------------------------- Part A: FMEDA
# name, FIT, safety-related share, single-point share (no mechanism), DC residual,
# share that is multiple-point, DC latent (detected by start-up / periodic tests)
FMEDA = [
    ("Master valve A (NC, spring return)", 40, 1.0, 0.0, 0.00, 0.5, 0.99),
    ("Master valve B (NC, spring return)", 40, 1.0, 0.0, 0.00, 0.5, 0.99),
    ("Thruster valve x10 (stuck open)",    100, 1.0, 0.0, 0.00, 1.0, 0.95),
    ("Thruster valve drivers x10",          50, 0.6, 0.0, 0.00, 1.0, 0.95),
    ("Thrust control unit (lockstep MCU)", 100, 0.5, 0.0, 0.00, 1.0, 0.99),
    ("Safety monitor (dissimilar MCU)",     60, 0.5, 0.0, 0.00, 1.0, 0.99),
    ("Arm-line driver and harness",         20, 1.0, 0.02, 0.90, 0.98, 0.95),
    ("Zone authorisation (GNSS + beacon)",  80, 0.3, 0.0, 0.00, 1.0, 0.90),
    ("Low-voltage power (dual feed)",       30, 0.4, 0.0, 0.00, 1.0, 0.99),
]


def fmeda():
    rows, sr, spf_rf, mpf, mpf_lat = [], 0.0, 0.0, 0.0, 0.0
    for name, fit, s_rel, spf, dc_rf, mpf_share, dc_lat in FMEDA:
        lam_sr = fit * s_rel
        lam_spf = lam_sr * spf * (1 - dc_rf)          # residual after the mechanism
        lam_mpf = lam_sr * mpf_share
        lam_lat = lam_mpf * (1 - dc_lat)
        sr += lam_sr; spf_rf += lam_spf; mpf += lam_mpf; mpf_lat += lam_lat
        rows.append(dict(element=name, fit=fit, safety_related_fit=round(lam_sr, 1),
                         spf_rf_fit=round(lam_spf, 2), latent_fit=round(lam_lat, 2)))
    spfm = 1 - spf_rf / sr
    lfm = 1 - mpf_lat / (sr - spf_rf)
    # simplified dual-point term: a latent fault in one channel waits on average
    # T_LIFE/2 for a fault in the partner channel (gas path vs command path)
    gas_path_lat = sum(r["latent_fit"] for r in rows[:2])
    cmd_path = sum(r["safety_related_fit"] for r in rows[2:])
    cmd_path_lat = sum(r["latent_fit"] for r in rows[2:])
    gas_path = sum(r["safety_related_fit"] for r in rows[:2])
    dpf = (gas_path_lat * 1e-9 * cmd_path * 1e-9 + cmd_path_lat * 1e-9 * gas_path * 1e-9) \
        * T_LIFE_H / 2 / 1e-9
    beta = 0.02                                        # common-cause share between the two master valves
    ccf = beta * 40 * (1 - 0.99)                       # CCF that escapes the leak-down test, FIT
    pmhf = spf_rf + dpf + ccf
    return rows, dict(SPFM_pct=round(100 * spfm, 2), LFM_pct=round(100 * lfm, 2),
                      PMHF_FIT=round(pmhf, 3), PMHF_single_point_FIT=round(spf_rf, 3),
                      PMHF_dual_point_FIT=round(dpf, 5), PMHF_common_cause_FIT=round(ccf, 3),
                      targets_ASIL_D=dict(SPFM_pct=99, LFM_pct=90, PMHF_FIT=10))


# ---------------------------------------------------------------- Part B: per-hop risk
FAULTS = {   # FIT of the failure mode across all relevant parts, ASSUMED
    "stuck_open": 100.0,     # 10 thruster valves x 10 FIT
    "stuck_closed": 100.0,
    "leak": 50.0,            # COPV, fittings, regulator
}


def latent_prob(fit, dc):
    return fit * 1e-9 * (dc * TEST_INTERVAL_H / 2 + (1 - dc) * T_LIFE_H / 2)


def cond(pct, n):
    """Conditional probability with rule-of-three bound when the count is zero."""
    return max(pct / 100.0, 3.0 / n)


def per_hop(mc, cfg, dc):
    c = mc[cfg]
    p_so = latent_prob(FAULTS["stuck_open"], dc) * cond(c["bad_given_stuck_open_pct"], c["n_flown_stuck_open"])
    p_sc = latent_prob(FAULTS["stuck_closed"], dc) * cond(c["bad_given_stuck_closed_pct"], c["n_flown_stuck_closed"])
    p_lk = latent_prob(FAULTS["leak"], 0.99) * cond(c["bad_given_leak_pct"], c["n_flown_leak"])
    sotif_bound = 3.0 / (c["n_flown"] - c["n_flown_stuck_open"] - c["n_flown_leak"] - c["n_flown_stuck_closed"])
    return dict(stuck_open=p_so, stuck_closed=p_sc, leak=p_lk, total_faults=p_so + p_sc + p_lk,
                sotif_upper_bound_from_mc=sotif_bound)


def main():
    rows, metrics = fmeda()
    mc = json.load(open("sim4_out.json"))
    steps = [
        ("C: recover, 9 kN groups, 95 % pre-arm test", "C: reserve check, isolate + recover", 0.95),
        ("D: recover, 11 kN groups, 95 % pre-arm test", "D: C with 11 kN lift groups", 0.95),
        ("D + 99.9 % pre-arm valve function test", "D: C with 11 kN lift groups", 0.999),
    ]
    hop = {label: per_hop(mc, cfg, dc) for label, cfg, dc in steps}
    out = dict(fmeda_rows=rows, sg1_metrics=metrics,
               per_hop={k: {kk: float(f"{vv:.3g}") for kk, vv in v.items()} for k, v in hop.items()},
               target_catastrophic_per_hop=1e-7)
    ps.setup()
    fig, ax = ps.plt.subplots(figsize=(9.6, 3.9))
    labels = list(hop.keys())
    y = np.arange(len(labels))[::-1]
    comp = [("stuck_closed", ps.BLUE, "Stuck-closed valve"), ("stuck_open", ps.ORANGE, "Stuck-open valve"),
            ("leak", ps.AQUA, "Leak")]
    totals = [hop[lab]["total_faults"] for lab in labels]
    ax.barh(y, totals, color=ps.BLUE, height=0.5)
    for yi, tot in zip(y, totals):
        ax.text(tot * 1.15, yi, f"{tot:.1e}", va="center", color=ps.INK2, fontsize=9)
    ax.axvline(1e-7, color=ps.INK, lw=1.2, ls="--")
    ax.text(1.1e-7, y[-1] - 0.42, "proposed target 1e-7", color=ps.INK, fontsize=9)
    ax.set_yticks(y, labels)
    ax.set_title("Probability of a hard or unsafe landing per hop from valve and leak faults")
    ax.set_xscale("log")
    ax.set_xlim(1e-8, 1e-4)
    ax.set_xlabel("Probability per hop (log scale)")
    ax.grid(axis="y", visible=False)
    ps.headline(fig, "Stuck-closed valves dominate; a near-perfect pre-arm valve test is the biggest lever",
                "Latent-fault probability (assumed FIT, test coverage, 10,000 h life) x conditional outcome from Sim 4")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig("fig6_per_hop_risk.png", dpi=160)
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
