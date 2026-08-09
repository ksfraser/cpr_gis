#!/usr/bin/env python3
"""
Operator views of the stepped-wedge module cross-section.

Three views of the 2-ft-deep module used across the compressed build:

  output/render/cpr_wedge_side.png    side elevation (operator's view, aisle)
  output/render/cpr_wedge_end.png     end-plate view
  output/render/cpr_wedge_stack2.png  two modules nested inverted (2x2x4 box)

Cross-section, front (aisle) to back (wall), z in inches above the L0 rail:

  depth  0- 8 in   front band,  L0 rail at z=0   (yards / sidings, visible)
  depth  8-16 in   45 deg riser                  (scenery slope)
  depth 16-24 in   main band,   L1 rail at z=+8  (mainline, visible)
  depth 20-24 in   45 deg scenery back slope to z=+16 (module back)

Track and scenery sit BELOW the 45 deg reference slope (riser + back slope);
the two 45 deg faces are what let an inverted mate nest on top.  Exact
nesting is proven with a cardboard mock-up before framing (riser angle
45-60 deg is the tuning knob).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "render")
os.makedirs(OUT, exist_ok=True)

# --- cross-section geometry, inches -------------------------------------
D = 24.0      # module depth (2 ft)
FB = 8.0      # front band depth
MB = 16.0     # main band front depth
Z1 = 8.0      # L1 rail height on the main band
SB = 20.0     # scenery back-slope start depth
H = 16.0      # max scenery height at the module back
L0_D = 4.0    # L0 track depth (front band)
L1_D = 18.0   # L1 track depth (main band)
RAIL = 0.5    # rail-head height above the band surface, in

STRUCT = [(0, 0), (FB, 0), (MB, Z1), (D, Z1), (D, 0)]          # stepped wedge
SCEN = [(SB, Z1), (D, H), (D, Z1)]                              # back scenery hill

WOOD = "#d9c9a3"
RISER = "#c9b28a"
GRASS = "#8fbf6a"
TREE = "#2f6b3f"
TRACK = "#333333"
BALLAST = "#9aa0a6"
REF = "#c0392b"
BAND_Z = 0.0


def draw_module(ax, dx=0.0, dz=0.0, fc=WOOD, edge="k", alpha=1.0,
                hatched=False, reflected=False):
    st = [(x + dx, z + dz) for x, z in
          (STRUCT if not reflected else [(x, H - z) for x, z in STRUCT])]
    ax.add_patch(Polygon(st, closed=True, facecolor=fc, edgecolor=edge,
                         lw=1.6, alpha=alpha,
                         hatch="//" if hatched else None))
    sc = [(x + dx, z + dz) for x, z in
          (SCEN if not reflected else [(x, H - z) for x, z in SCEN])]
    ax.add_patch(Polygon(sc, closed=True, facecolor=GRASS, edgecolor=edge,
                         lw=1.4, alpha=alpha,
                         hatch=".." if hatched else None))


def draw_track(ax, d, z):
    ax.plot([d - 0.9, d + 0.9], [z + RAIL, z + RAIL], color=TRACK, lw=2.2,
            zorder=5, solid_capstyle="butt")
    ax.plot([d - 0.9, d + 0.9], [z - 0.15, z - 0.15], color=BALLAST, lw=3.0,
            zorder=4, solid_capstyle="butt")


def draw_pine(ax, x, y, h, color=TREE):
    ax.add_patch(Polygon([(x - h / 3, y), (x, y + h), (x + h / 3, y)],
                         closed=True, facecolor=color, edgecolor="none"))
    ax.plot([x, x], [y, y + h * 0.22], color="#5a3a1a", lw=0.8)


def reference_line(ax, label=True):
    ax.plot([FB, MB], [0, Z1], color=REF, lw=1.4, ls="--")
    ax.plot([SB, D], [Z1, H], color=REF, lw=1.4, ls="--")
    if label:
        ax.text(12, 3.2, "45 deg reference slope\n(track + scenery below)",
                color=REF, fontsize=7.5, ha="center")


def side_view():
    fig, ax = plt.subplots(figsize=(8, 5))
    draw_module(ax)
    reference_line(ax)
    draw_track(ax, L0_D, BAND_Z)          # L0 yard/siding
    draw_track(ax, L1_D, Z1)              # L1 mainline
    # scenery: shrubs on the front band, pines on the riser + main band,
    # all kept below the 45 deg reference silhouette
    for x, h in [(1.2, 2.2), (5.6, 2.8)]:
        draw_pine(ax, x, 0, h)
    draw_pine(ax, 9.5, 1.5, 3.2)          # rooted on the riser
    draw_pine(ax, 13.5, 5.5, 3.0)
    draw_pine(ax, 22.0, Z1, 1.0)          # behind the mainline, under back slope
    # labels
    ax.annotate("L0 yard / siding track\n(rail 0 in)", xy=(L0_D, 0.6),
                xytext=(1.2, 6.2), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.annotate("L1 mainline\n(rail +8 in)", xy=(L1_D, Z1 + 0.7),
                xytext=(15.0, 11.2), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.annotate("front band", xy=(4, -1.4), xytext=(2.2, -3.4),
                fontsize=7, color="#555",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#555"))
    ax.annotate("45 deg riser", xy=(12, 4.5), xytext=(8.6, -3.4),
                fontsize=7, color="#555",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#555"))
    ax.annotate("main band", xy=(20, Z1 - 1.2), xytext=(16.2, -3.4),
                fontsize=7, color="#555",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#555"))
    ax.annotate("back slope\n(scenery)", xy=(24.1, 12), xytext=(26.8, 11),
                fontsize=7, color="#555",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#555"))
    ax.text(-2.0, 8, "AISLE", rotation=90, fontsize=8, color="#777", va="center")
    ax.text(25.2, 8, "WALL", rotation=-90, fontsize=8, color="#777", va="center")
    ax.text(12, 17.2, "operator stands in the aisle, looking at the module face",
            ha="center", fontsize=8.5, color="#444")
    ax.set_xlim(-3, 30); ax.set_ylim(-4.5, 19)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Side view of the stepped wedge (front = aisle, back = wall)",
                 fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT, "cpr_wedge_side.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"wrote {p}")


def end_view():
    fig, ax = plt.subplots(figsize=(7, 5))
    plate = [(0, 0), (FB, 0), (MB, Z1), (D, Z1), (D, H), (D, 0)]
    ax.add_patch(Polygon(plate, closed=True, facecolor=WOOD, edgecolor="k",
                         lw=1.8))
    ax.plot([SB, D], [Z1, H], color=GRASS, lw=2.2)   # back scenery slope edge
    draw_track(ax, L0_D, BAND_Z)
    draw_track(ax, L1_D, Z1)
    # Free-mo bolt pattern along the plate edges (through-boards)
    for x in (2, 22):
        for z in (1.0, 6.0):
            ax.add_patch(plt.Circle((x, z), 0.35, fc="#777", ec="none"))
    ax.annotate("L0 rail hole", xy=(L0_D, 0.8), xytext=(0.5, 10.5),
                fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.annotate("L1 rail hole", xy=(L1_D, Z1 + 0.8), xytext=(9.5, 12.6),
                fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.text(12, -1.8, "end plate: 24 in wide \u00d7 16 in max (3/4 in ply, "
            "track centred, last 6 in straight/level)",
            ha="center", fontsize=8, color="#444")
    ax.set_xlim(-2, 27); ax.set_ylim(-3.5, 18)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("End view \u2014 the module end plate", fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT, "cpr_wedge_end.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"wrote {p}")


def stack_view():
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.add_patch(Polygon([(0, 0), (24, 0), (24, 24), (0, 24)], closed=True,
                         fill=False, edgecolor="#888", lw=2.0, ls="--"))
    ax.text(12, 24.8, "storage box 2 \u00d7 2 \u00d7 4 ft",
            ha="center", fontsize=9, color="#555")
    draw_module(ax)                                   # bottom module, right-side up
    draw_module(ax, fc="#e0d4b8", edge="#666", hatched=True,
                reflected=True)                       # inverted mate interlocks
    ax.plot([0, 24], [8, 8], color="#999", lw=0.8, ls=":")
    ax.text(24.6, 8, "treads meet", fontsize=7.5, color="#777", va="center")
    ax.plot([0, 24], [16, 16], color="#aaa", lw=0.8, ls=":")
    ax.text(24.6, 16, "pair height", fontsize=7.5, color="#777", va="center")
    ax.annotate("bottom module (right side up)", xy=(7, 3),
                xytext=(-9.5, 4), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.annotate("inverted mate (hatched):\nfront band at top, back slope down,\n"
                "45 deg faces interlock against the bottom",
                xy=(7, 12), xytext=(1, 27), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.set_xlim(-12, 30); ax.set_ylim(-3, 32)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Two modules stacked \u2014 inverted pair nests to the box",
                 fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT, "cpr_wedge_stack2.png")
    fig.savefig(p, dpi=130); plt.close(fig)
    print(f"wrote {p}")


def main():
    side_view()
    end_view()
    stack_view()


if __name__ == "__main__":
    main()
