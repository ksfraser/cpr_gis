#!/usr/bin/env python3
"""
Gym setup for the -comp mountain section: fold the linear strip.

The -comp and -proto plans draw Revelstoke->Field as a straight west->east
strip; neither incorporates curves.  For a gym setup the strip is folded
into N parallel runs joined by 180 deg return loops ("dogbone" for N=2, a
serpentine for N>=3).  N runs need N-1 loops; fold points are chosen between
scenes to keep the runs balanced.  The loops are a gym artifact, not part of
the -proto -- which is why the proto has so few curves.

Outputs:
  output/cpr_gym_setup.md
  output/render/cpr_gym_fold.png
"""
import itertools
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from compressed_plan import MODULES, SCENES

OUT = os.path.join(ROOT, "output")
RENDER = os.path.join(ROOT, "output", "render")
os.makedirs(RENDER, exist_ok=True)

R = 30.0 / 12.0       # 180 deg loop radius, ft (Free-mo min 24 in; 30 in train)
MODULE_FT = 4.0       # one 4-ft bay
DEPTH_FT = 2.0        # module depth
AISLE_FT = 3.0        # walking aisle between parallel runs
NAMES = [n for _, n, *_ in SCENES]


def scene_bays():
    core = {}
    full = {}
    for code, *_ in SCENES:
        core[code] = sum(n for _, n, k, *_ in MODULES[code] if k == "CORE")
        full[code] = sum(n for _, n, *_ in MODULES[code])
    return core, full


def fold(bays, n_runs):
    """Return (boundaries, runs) splitting the ordered scenes into n_runs
    contiguous groups with the smallest possible longest run."""
    scenes = list(bays.values())
    best = None
    for cuts in itertools.combinations(range(1, len(scenes)), n_runs - 1):
        runs, prev = [], 0
        for c in cuts + (len(scenes),):
            runs.append(sum(scenes[prev:c]))
            prev = c
        score = max(runs)
        if best is None or score < best[0]:
            best = (score, cuts, runs)
    return best[1], best[2]


def write_doc(core, full):
    L = []
    L.append("# CP Mountain Section \u2014 Gym Setup  [-comp]")
    L.append("")
    L.append("The `-comp` module plan (`cpr_module_plan-comp.md`) and the "
             "`-proto` 1:1000 designs draw the section as a **straight "
             "west\u2192east strip and do NOT include curves**. To set it up "
             "in a gym the strip is folded into **N parallel runs** joined by "
             "**180\u00b0 return loops** (a dogbone for N=2, a serpentine for "
             "N\u22653). The loops are a *gym artifact* \u2014 they are not part "
             "of the -proto, which is why the proto has few curves.")
    L.append("")
    L.append(f"Folding rule: **N runs = N\u22121 loops**. Each run is a stretch "
             f"of the single-track main with its yards/sidings; the return "
             f"loops use radius **{R*12:.0f} in** (Free-mo minimum 24 in; "
             f"30 in keeps the 89-ft well-car train comfortable).")
    L.append("")

    for label, bays, total_bays in (("minimum (core modules only)", core,
                                     sum(core.values())),
                                    ("full build (core + filler + optional)",
                                     full, sum(full.values()))):
        L.append(f"## {label.capitalize()} \u2014 {total_bays} modules = "
                 f"{total_bays*MODULE_FT:.0f} ft")
        L.append("")
        L.append("| runs | 180\u00b0 loops | longest run | gym length (min) | "
                 "fits a \u2264 60 ft gym? |")
        L.append("|---|---|---|---|---|")
        for n in (2, 3, 4):
            cuts, runs = fold(bays, n)
            longest = max(runs) * MODULE_FT
            need = longest + 2 * R
            ok = "yes" if need <= 60 else "no"
            L.append(f"| {n} | {n-1} | {longest:.0f} ft | {need:.0f} ft | {ok} |")
        L.append("")
        for n in (2, 3, 4):
            cuts, runs = fold(bays, n)
            L.append(f"### {n}-run fold  ({n-1} loop{'s' if n-1 != 1 else ''})")
            L.append("")
            L.append("| run | scenes | modules | length |")
            L.append("|---|---|---|---|")
            prev = 0
            for i, c in enumerate(cuts + (len(bays),)):
                scenes = list(bays.values())[prev:c]
                L.append(f"| {i+1} | " + " \u2192 ".join(
                    [f"{NAMES[j]} ({scenes[k]} mod)" for k, j in
                     enumerate(range(prev, c))]) + f" | {sum(scenes)} | "
                    f"{sum(scenes)*MODULE_FT:.0f} ft |")
                prev = c
            L.append("")
        L.append("")
    L.append("## Operations (gym dogbone)")
    L.append("")
    L.append("- Trains leave the west end (Revelstoke) through scenes A\u2013C, "
             "take the 180\u00b0 return loop, and come back through D\u2013F to "
             "the east end (Field) \u2014 continuous running with one turn.")
    L.append("- The two ends (Revelstoke yard / Field yard) sit at the front "
             "of the gym; the loop(s) stick out the back/ends.")
    L.append("- Add a second 180\u00b0 loop at the front (a true oval) only if "
             "pure continuous running is wanted; the dogbone already gives a "
             "full continuous lap because the two end yards join the runs.")
    L.append("- Curve grade: keep the loops flat (yards are flat anyway); "
             "the scene grades (\u00b12.5% cap) stay on the straight runs.")
    L.append("")
    L.append(f"Footprint: length = longest run + {2*R:.0f} ft for the loop "
             f"overhang; width = {n_runs_label()}.")
    with open(os.path.join(OUT, "cpr_gym_setup.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_gym_setup.md ({len(L)} lines)")


def n_runs_label():
    return "runs \u00d7 module depth + aisles + aisle to wall"


def render_fold(bays, n_runs):
    import numpy as np

    cuts, runs = fold(bays, n_runs)
    scenes = list(bays.values())
    run_ft = [r * MODULE_FT for r in runs]
    row = DEPTH_FT + AISLE_FT

    groups = []
    prev = 0
    for c in cuts + (len(scenes),):
        groups.append((prev, c))
        prev = c

    codes = [code for code, *_ in SCENES]

    fig, ax = plt.subplots(figsize=(13, 3.6 + 1.2 * n_runs))
    for i, (a, b) in enumerate(groups):
        y = i * row
        ft = run_ft[i]
        go_east = i % 2 == 0
        ax.add_patch(Rectangle((0, y), ft, DEPTH_FT, facecolor="#dbe9c8",
                               edgecolor="k", lw=1.2))
        if go_east:
            ax.annotate("", xy=(ft, y + DEPTH_FT / 2), xytext=(0, y + DEPTH_FT / 2),
                        arrowprops=dict(arrowstyle="-|>", color="#1f4e79", lw=1.6))
        else:
            ax.annotate("", xy=(0, y + DEPTH_FT / 2), xytext=(ft, y + DEPTH_FT / 2),
                        arrowprops=dict(arrowstyle="-|>", color="#1f4e79", lw=1.6))
        ax.text(ft / 2, y + DEPTH_FT / 2, f"run {i+1}: {ft:.0f} ft",
                ha="center", va="center", fontsize=8.5, fontweight="bold")
        # scene letters + yard markers along the run
        off = 0.0
        for j in range(a, b):
            code = codes[j]
            sft = scenes[j] * MODULE_FT
            cx = off + sft / 2
            if not go_east:
                cx = ft - cx
            ax.text(cx, y + DEPTH_FT + 0.15, code, ha="center",
                    fontsize=7.5, color="#333")
            xacc = 0.0
            for mid, nb, kind, mname, *_ in MODULES[code]:
                if "yard" in mname:
                    xr = off + xacc + nb * MODULE_FT / 2
                    if not go_east:
                        xr = ft - xr
                    ax.plot([xr], [y + DEPTH_FT / 2], marker="o", ms=6,
                            color="#c0392b", zorder=5)
                    ax.text(xr, y - 0.35, mname.split("\u2014")[0].strip(),
                            ha="center", fontsize=6, color="#c0392b")
                xacc += nb * MODULE_FT
            off += sft
    # 180 deg return loops between the runs
    th = np.linspace(0, np.pi, 61)
    for i in range(n_runs - 1):
        y0 = i * row + DEPTH_FT / 2
        y1 = (i + 1) * row + DEPTH_FT / 2
        if i % 2 == 0:                      # east-end loop
            xe = max(run_ft[i], run_ft[i + 1])
            if run_ft[i] < xe:
                ax.plot([run_ft[i], xe], [y0, y0], color="#1f4e79", lw=1.6)
            if run_ft[i + 1] < xe:
                ax.plot([run_ft[i + 1], xe], [y1, y1], color="#1f4e79", lw=1.6)
            xs = [xe + R * np.sin(t) for t in th]
            ys = [y0 + (y1 - y0) * t / np.pi for t in th]
            ax.plot(xs, ys, color="#1f4e79", lw=1.6)
            ax.text(xe + R + 0.3, (y0 + y1) / 2, f"180\u00b0 loop\nR={R*12:.0f} in",
                    fontsize=7.5, va="center", color="#1f4e79")
        else:                               # west-end loop
            xs = [-R * np.sin(t) for t in th]
            ys = [y0 + (y1 - y0) * t / np.pi for t in th]
            ax.plot(xs, ys, color="#1f4e79", lw=1.6)
            ax.text(-R - 0.3, (y0 + y1) / 2, f"180\u00b0 loop\nR={R*12:.0f} in",
                    fontsize=7.5, va="center", ha="right", color="#1f4e79")
    # footprint
    L_foot = max(run_ft) + 2 * R
    W_foot = n_runs * row
    ax.add_patch(Rectangle((0, -AISLE_FT), L_foot, W_foot + 2 * AISLE_FT,
                           fill=False, edgecolor="#888", ls="--", lw=1.2))
    ax.text(L_foot / 2, -AISLE_FT - 0.5,
            f"footprint \u2248 {L_foot:.0f} ft \u00d7 {W_foot + 2*AISLE_FT:.0f} ft "
            "(loops + aisles included)",
            ha="center", fontsize=8.5, color="#555")
    ax.set_xlim(-2 * R - 2, L_foot + 1.5)
    ax.set_ylim(-row - 0.8, n_runs * row + 1.2)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"Gym fold: {n_runs} runs, {n_runs-1} \u00d7 180\u00b0 loops "
                 f"(west = left, \u2192 east; loops not in the -proto)",
                 fontsize=11)
    fig.tight_layout()
    p = os.path.join(RENDER, "cpr_gym_fold.png")
    fig.savefig(p, dpi=125)
    plt.close(fig)
    print(f"wrote {p}")
    return L_foot


def main():
    core, full = scene_bays()
    write_doc(core, full)
    n = int(os.environ.get("GYM_RUNS", "2"))
    render_fold(core, n)


if __name__ == "__main__":
    main()
