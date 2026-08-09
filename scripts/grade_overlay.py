#!/usr/bin/env python3
"""
Grade / elevation overlay for the CP mountain section scenes A-F.

Reads working/profile.csv (1-km smoothed grade, tunnel mask) and lays out, per
4-ft module of each scene, the grade, elevation change and running elevation.
Also produces scene summaries and the vertical-design implications for a model
railroad built on the 1:1000 run compression.

Produces output/cpr_grade_overlay-proto.md
"""
import csv
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mountain_plan import SCENES

WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

MODULE_M = 4.0 * 0.3048  # 1.2192 m


def main():
    rows = list(csv.DictReader(open(os.path.join(WORK, "profile.csv"))))
    dist = np.array([float(r["dist_km"]) for r in rows])
    elev = np.array([float(r["elev_m"]) for r in rows])
    grade1 = np.array([float(r["grade_1km_pct"])
                       if r["grade_1km_pct"].strip() else np.nan for r in rows])
    intun = np.array([int(r["in_tunnel"]) if r["in_tunnel"] else 0
                      for r in rows])

    def interp(x):
        return float(np.interp(x, dist, elev))

    L = []
    L.append("# CP Mountain Section \u2014 Grade & Elevation Overlay")
    L.append("")
    L.append("Per 4-ft module grade/elevation from the MRDEM-30 profile "
             "(1-km smoothed grade; tunnel rows masked). Module numbers match "
             "`cpr_scene_modules-proto.md`. Runs eastbound (Vancouver \u2192 Calgary); "
             "negative grade = descending eastbound.")
    L.append("")

    scene_summary = []
    for code, name, a, b, _ in SCENES:
        mods = int((b - a) / MODULE_M) + 1
        elev0 = interp(a)
        L.append(f"## Scene {code} \u2014 {name}  (km {a:.1f}-{b:.1f})")
        L.append("")
        L.append("| mod | proto km | model m | elev in | elev out | \u0394elev | avg grade | max grade |")
        L.append("|---|---|---|---|---|---|---|---|")
        cum = elev0
        running = []
        for i in range(mods):
            km0 = a + i * MODULE_M
            km1 = min(km0 + MODULE_M, b)
            e0 = interp(km0)
            e1 = interp(km1)
            de = e1 - e0
            mask = (dist >= km0) & (dist <= km1) & np.isfinite(grade1) & (intun == 0)
            if mask.sum() >= 2:
                avg = float(np.mean(grade1[mask]))
                mx = float(np.max(np.abs(grade1[mask])))
            else:
                avg = mx = float("nan")
            running.append(e1)
            ag = f"{avg:+.2f}" if math.isfinite(avg) else "\u2014"
            mg = f"{mx:.2f}" if math.isfinite(mx) else "\u2014"
            L.append(f"| {code}{i+1:02d} | {km0:.2f}\u2013{km1:.2f} | "
                     f"{km0-a:.2f}\u2013{km1-a:.2f} | {e0:.0f} | {e1:.0f} | "
                     f"{de:+.0f} | {ag} | {mg} |")
        L.append("")

        valid = grade1[(dist >= a) & (dist <= b) & np.isfinite(grade1) & (intun == 0)]
        ruling_d = float(np.min(valid)) if len(valid) else 0.0
        ruling_u = float(np.max(valid)) if len(valid) else 0.0
        net = interp(b) - elev0
        scene_summary.append((code, name, a, b, elev0, interp(b), net,
                              ruling_d, ruling_u, mods))

    L.append("## Scene summaries (eastbound)")
    L.append("")
    L.append("| scene | feature | elev in | elev out | net \u0394 m | ruling descent % | ruling climb % | model m |")
    L.append("|---|---|---|---|---|---|---|---|")
    for code, name, a, b, e0, e1, net, rd, ru, mods in scene_summary:
        L.append(f"| {code} | {name} | {e0:.0f} | {e1:.0f} | {net:+.0f} | {rd:.2f} | "
                 f"{ru:.2f} | {(b-a):.0f} |")
    L.append("")

    L.append("## Vertical design implications")
    L.append("")
    L.append("At the 1:1000 run compression a **true-scale vertical** keeps the "
             "prototype grade: 1 m of layout rises/fell exactly the prototype "
             "metres. The table above is that elevation in **millimetres** per "
             "metre of layout when built true-scale. Key facts:")
    L.append("")
    total_net = scene_summary[-1][5] - scene_summary[0][4]
    L.append(f"- Whole section (km 606-812): net **{total_net:+.0f} m** over "
             f"{(812.0-605.7):.0f} m of layout ({total_net/1000.0:+.1f} m of rise over "
             f"{206.3:.0f} m of benchwork).")
    big_up = max(scene_summary, key=lambda s: s[6])
    L.append(f"- Steepest net climb is Scene {big_up[0]} ({big_up[1]}): "
             f"**{big_up[6]:+.0f} m** of rise over {big_up[9]:.0f} m of layout "
             f"({big_up[6]/big_up[9]:+.2f}% average model grade).")
    big_down = min(scene_summary, key=lambda s: s[6])
    L.append(f"- Steepest net descent is Scene {big_down[0]} ({big_down[1]}): "
             f"**{big_down[6]:+.0f} m**.")
    L.append("")
    L.append("### What that means for benchwork")
    L.append("")
    L.append("- A 2.2% ruling grade (Rogers west slope, Kicking Horse) is "
             "**runable in HO** at 2.2% model grade; 4.5% (Kicking Horse 4.5% "
             "4.5% prototypes) is not \u2014 the modern Kicking Horse spiral climb "
             "is ~2.2% but OSM terrain shows steeper single points.")
    L.append("- True-scale 1:1000 vertical over the mountain section needs "
             "~**1 m of total rise/fall**, which is a lot for flat benchwork. "
             "Recommended compromises, in order:")
    L.append("  1. **Flat bench (0% model grade), grades shown as scenery** \u2014 "
             "simplest; the train does not climb.")
    L.append("  2. **One ruling climb** (e.g. the Rogers 2.2% or Kicking Horse "
             "2.2%) built at prototype grade over the relevant scene, everything "
             "else flat \u2014 needs 0.3-0.5 m of end-to-end bench rise per scene.")
    L.append("  3. **Rising layout** \u2014 the full section climbs at ~0.5% model "
             "grade (track rises 1 m over 200 m), gentle enough for the 12 ft "
             "train and visually conveys the mountain crossing.")
    L.append("- If you build a grade at all, keep it \u2264 2% so the 12 ft train "
             "(2 AC4400) can restart mid-grade after a stop.")
    L.append("")

    with open(os.path.join(OUT, "cpr_grade_overlay-proto.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_grade_overlay-proto.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
