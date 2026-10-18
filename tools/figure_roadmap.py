"""Draw Figure 9, the verification and validation roadmap (docs/figures/F11_vv_roadmap.png)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "sim"))
import plotstyle as ps  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

PHASES = [
    ("1  Concept", "Done (this study)", True,
     ["Sims 1-7", "FMEA, FMEDA, FTA, DFA", "STPA, TARA", "Requirements and trace"]),
    ("2  Components", "Next", False,
     ["COPV burst, cycle, fire", "Valve cold and life tests", "Supplier FMEDA data", "Software unit tests"]),
    ("3  Integration (HIL)", "Planned", False,
     ["Fault injection, timing", "Backup hop law", "Attack injection", "VER-02 to VER-04, 22-24"]),
    ("4  Physical tests", "Planned", False,
     ["Thrust stand, blowdown", "Drop tests (airbag)", "Tethered hops", "Crash with charged tanks"]),
    ("5  Validation, release", "Planned", False,
     ["Model correlation", "~3e7 hop-equivalents", "Penetration test", "Independent assessment"]),
]
GATES = ["Architecture\nfrozen", "Parts\nqualified", "HIL\npassed", "Model\nvalidated"]


def main(out=os.path.join(HERE, "..", "docs", "figures", "F11_vv_roadmap.png")):
    ps.setup()
    fig = plt.figure(figsize=(13.2, 4.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 4.9)
    ax.axis("off")
    fig.text(0.032, 0.95, "Every number in this study is concept-stage evidence until phases 2-5 replace it",
             fontsize=14, fontweight="bold", color=ps.INK, va="top")
    w, gap, x0, y0, h = 2.24, 0.34, 0.42, 0.95, 3.2
    for i, (title, state, done, items) in enumerate(PHASES):
        x = x0 + i * (w + gap)
        face = "#e8f1fb" if done else ps.SURFACE
        edge = ps.BLUE if done else "#cfcdc6"
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=face, ec=edge, lw=2.0 if done else 1.3,
                                    ls="-" if done else (0, (4, 3))))
        ax.text(x + 0.18, y0 + h - 0.3, title, fontsize=12, fontweight="bold", color=ps.INK, va="top")
        ax.text(x + 0.18, y0 + h - 0.72, state, fontsize=10, color=ps.BLUE if done else ps.INK2, va="top")
        for j, it in enumerate(items):
            ax.text(x + 0.18, y0 + h - 1.2 - j * 0.46, it, fontsize=10.2, color=ps.INK, va="top")
        if i < len(GATES):
            gx = x + w + gap / 2
            ax.annotate("", xy=(gx + 0.15, y0 + h / 2), xytext=(gx - 0.15, y0 + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=ps.GREY, lw=1.4))
            ax.text(gx, y0 - 0.2, GATES[i], fontsize=8.8, color=ps.INK2, ha="center", va="top")
    ax.text(x0, 0.12, "Solid: evidence exists.  Dashed: planned.  Gates under the arrows are the exit criteria for each phase.",
            fontsize=9.5, color=ps.INK2)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=150)
    return out


if __name__ == "__main__":
    print(main())
