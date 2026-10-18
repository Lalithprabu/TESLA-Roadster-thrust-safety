"""Shared chart style (validated light-mode palette, recessive grid, thin marks)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
GREY = "#9a9893"


def setup():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE, "font.size": 10.5,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "xtick.color": INK2, "ytick.color": INK2,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "lines.linewidth": 2.0, "legend.frameon": False, "legend.fontsize": 9.5,
    })


def headline(fig, text, sub=None):
    fig.text(0.012, 0.975, text, fontsize=13, fontweight="bold", color=INK, va="top")
    if sub:
        fig.text(0.012, 0.925, sub, fontsize=10, color=INK2, va="top")
