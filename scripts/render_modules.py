#!/usr/bin/env python3
"""
Render track diagrams and the elevation profile for the compressed module
plan (scenes A-F) as PNG images.

Outputs (into output/render/):
  cpr_scene_A.png ... cpr_scene_F.png   per-scene module track diagrams
  cpr_compressed_overview.png           whole section, one strip
  cpr_elevation_profile.png             model elevation vs layout length

Uses the same module data and grade/elevation logic as compressed_plan.py.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from compressed_plan import MODULES, SCENES, compute_elevations

OUT = os.path.join(ROOT, "output", "render")
os.makedirs(OUT, exist_ok=True)

FT = 4.0                     # one 4-ft module bay in x units
COLOR = {
    "CORE":  {"run": "#dbe9c8", "tunnel": "#c8b8a0", "yard": "#bcd4e8"},
    "FILLER": {"run": "#e8e8d0", "tunnel": "#d8ccb8", "yard": "#e0e0f0"},
    "OPTIONAL": {"run": "#f5e9c8", "tunnel": "#eadfc8", "yard": "#f0e0d8"},
}


def _kind_color(kind, gclass):
    return COLOR.get(kind, {}).get(gclass, "#eeeeee")


def draw_module(ax, x0, mid, nbays, kind, name, width, gclass):
    w = FT * nbays
    h = 2.0 if width.startswith("24") else 1.3
    fc = _kind_color(kind, gclass)
    ec = "k"
    ls = "solid" if kind == "CORE" else ("dotted" if kind == "OPTIONAL" else "dashed")
    rect = mpatches.FancyBboxPatch((x0, 0.0), w, h,
                                   boxstyle="round,pad=0.02",
                                   facecolor=fc, edgecolor=ec,
                                   linestyle=ls, linewidth=1.4)
    ax.add_patch(rect)

    y_main = h - 0.45
    if gclass == "tunnel":
        bore = mpatches.FancyBboxPatch((x0 + 0.12, y_main - 0.22), w - 0.24,
                                       0.5, boxstyle="round,pad=0.02",
                                       facecolor="#3a3a3a", edgecolor="#222")
        ax.add_patch(bore)
        ax.plot([x0 + 0.12, x0 + w - 0.12], [y_main, y_main],
                color="#f5f5f5", lw=1.6, zorder=3)
        ax.plot([x0 + 0.12, x0 + 0.12], [y_main - 0.20, y_main + 0.20],
                color="#f5f5f5", lw=1.2, zorder=3)
    elif gclass == "yard":
        ax.plot([x0, x0 + w], [y_main, y_main], color="k", lw=1.7, zorder=3)
        if "body" in name:
            for i in range(4):
                yy = y_main - 0.32 * (i + 1)
                ax.plot([x0 + 0.25, x0 + w - 0.25], [yy, yy],
                        color="k", lw=1.15, zorder=3)
        if "ladder" in name:
            for i in range(4):
                yy = y_main - 0.32 * (i + 1)
                ax.plot([x0, x0 + 0.95], [y_main, yy],
                        color="k", lw=1.0, zorder=3)
        if "lead" in name or "tail" in name:
            ax.plot([x0, x0 + w], [y_main - 0.32, y_main - 0.32],
                    color="k", lw=1.15, zorder=3)
    else:
        ax.plot([x0, x0 + w], [y_main, y_main], color="k", lw=1.7, zorder=3)

    ax.text(x0 + w / 2, h + 0.16, mid, ha="center", va="bottom",
            fontsize=9, fontweight="bold")
    ax.text(x0 + w / 2, -0.08, name, ha="center", va="top",
            fontsize=6.5, rotation=0)
    return x0 + w


def render_scene(code):
    fig, ax = plt.subplots(figsize=(4 * len(MODULES[code]) / 3.0 + 2, 3.4))
    x = 0.0
    for mid, nbays, kind, name, carries, width, gclass in MODULES[code]:
        x = draw_module(ax, x, mid, nbays, kind, name, width, gclass)
    ax.set_xlim(-0.4, x + 0.4)
    ax.set_ylim(-1.0, 3.0)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(f"Scene {code} \u2014 compressed modules  "
                 f"(4-ft bays, \u2013\u2013 FILLER \u00b7 \u2026 OPTIONAL)",
                 fontsize=11, loc="left")
    fig.tight_layout()
    path = os.path.join(OUT, f"cpr_scene_{code}.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"wrote {path}")


def render_overview():
    total = sum(4 * n for mods in MODULES.values() for _, n, *_ in mods)
    fig, ax = plt.subplots(figsize=(total / 3.0, 5.0))
    x = 0.0
    for code, name, _, _, _ in SCENES:
        x0 = x
        for mid, nbays, kind, mname, carries, width, gclass in MODULES[code]:
            x = draw_module(ax, x, mid, nbays, kind, mname, width, gclass)
        ax.text((x0 + x) / 2, 2.6, f"Scene {code} \u2014 {name}",
                ha="center", fontsize=9, fontweight="bold")
        ax.plot([x, x], [-0.6, 2.4], color="#666", lw=0.8, alpha=0.6)
    ax.set_xlim(-0.4, x + 0.4)
    ax.set_ylim(-1.2, 3.0)
    ax.axis("off")
    ax.set_title("CP Mountain Section \u2014 compressed modules (west \u2192 east, "
                 "4-ft bays; dashed = omittable FILLER)", fontsize=11, loc="left")
    fig.tight_layout()
    path = os.path.join(OUT, "cpr_compressed_overview.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"wrote {path}")


def render_profile():
    elevs = compute_elevations()
    xs = [0.0]
    ys = [0.0]
    for e in elevs:
        xs.append(xs[-1] + e["len_m"])
        ys.append(e["cum_cm"])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(xs, ys, 0, step="post", color="#bcd4e8", alpha=0.7)
    ax.plot(xs, ys, drawstyle="steps-post", color="#1f4e79", lw=1.8,
            label="model rail top (cm above 50-in nominal)")

    # scene boundaries
    x_cum = 0.0
    for code, name, _, _, _ in SCENES:
        scene_len = sum(4 * n * 0.3048 for _, n, *_ in MODULES[code])
        x_cum += scene_len
        ax.axvline(x_cum, color="#999", lw=0.8, ls=":")
        ax.text(x_cum, ax.get_ylim()[1], f" {code} ", ha="left", va="top",
                fontsize=8, color="#555")

    # grade labels on graded modules
    for e in elevs:
        if abs(e["pct"]) > 0.05:
            ax.annotate(f"{e['pct']:+.1f}%", (e["cum_cm"], e["cum_cm"]),
                        textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=7, color="#c0392b")

    peak = max(abs(e["pct"]) for e in elevs)
    ax.set_xlabel("layout length (m, west \u2192 east)")
    ax.set_ylabel("model elevation above nominal (cm)")
    ax.set_title(f"Compressed layout elevation \u2014 max {peak:.1f}% grade "
                 f"(cap 2.5%), no full Vancouver\u2192Calgary climb",
                 fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUT, "cpr_elevation_profile.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"wrote {path}")


def main():
    for code, _, _, _, _ in SCENES:
        render_scene(code)
    render_overview()
    render_profile()


if __name__ == "__main__":
    main()
