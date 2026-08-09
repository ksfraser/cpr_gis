#!/usr/bin/env python3
"""
Per-scene, module-by-module track diagrams for the CP mountain section
(Revelstoke -> Field, scenes A-F).

Lays out every 4-ft module (1.2192 m at 1:1000 run compression) of each scene
and lists what track the module carries: straight / curve (direction, avg and
max deg/100ft, true-scale HO radius) / tunnel, annotated with yards, sidings,
multi-track spans and landmarks.

Sidings and yards are compressed to the design standard (12 ft usable siding /
yard long enough for the 12 ft train); the module grid below is the linear
1:1000 base so positions fall where they fall.

Reads working/features.json. Produces output/cpr_scene_modules.md
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mountain_plan import SCENES, ho_radius_ft, FT_PER_KM

WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

MODULE_M = 4.0 * 0.3048  # 1.2192 m per 4-ft module

TUNNEL_NAMES = {
    585: "Eagle Pass bore (585 m)",
    14636: "MacDonald Tunnel (14.6 km)",
    1885: "Rogers portal pair (1.9 km)",
    619: "Albert Canyon bore (619 m)",
    276: "Golden short bore (276 m)",
}


def tunnel_label(t):
    key = min(TUNNEL_NAMES, key=lambda k: abs(k - t["len_km"] * 1000))
    return TUNNEL_NAMES[key] if abs(key - t["len_km"] * 1000) < 200 else \
        f"tunnel km {t['km0']:.1f}-{t['km1']:.1f} ({t['len_km']*1000:.0f} m)"


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    runs = f["runs"]
    mts = f["multitrack"]
    tunnels = f["tunnels"]
    yards = f["yards"]
    sidings = f["sidings"]

    L = []
    L.append("# CP Mountain Section \u2014 Module-by-Module Track Diagrams")
    L.append("")
    L.append("One row per **4-ft module** (1.2192 m) on the linear 1:1000 base "
             "(1 proto km = 1 model m). Modules are numbered west-to-east from "
             "each scene start. Curve radius is the true-scale HO design value "
             "(from avg deg/100ft); max deg/100ft in parentheses is the noisy "
             "single-vertex peak.")
    L.append("")
    L.append("Sidings/yard spans are compressed to the design standard: a siding "
             "becomes **12 ft usable over 4 modules**, a yard is **just long "
             "enough for the 12 ft train**. Their prototype km is shown; the "
             "linear grid below is the build reference for plain single-track.")
    L.append("")

    for code, name, a, b, desc in SCENES:
        mods = int((b - a) / MODULE_M) + 1
        L.append(f"## Scene {code} \u2014 {name}  (km {a:.1f}-{b:.1f}, "
                 f"{(b-a):.0f} m \u2192 {mods} \u00d7 4-ft modules)")
        L.append("")
        L.append(desc)
        L.append("")
        L.append("| mod | model m | proto km | module carries | features |")
        L.append("|---|---|---|---|---|")
        for i in range(mods):
            km0 = a + i * MODULE_M
            km1 = min(km0 + MODULE_M, b)
            off0 = km0 - a
            off1 = km1 - a
            pieces = []
            for r in runs:
                if r["km1"] <= km0 or r["km0"] >= km1:
                    continue
                ln = min(r["km1"], km1) - max(r["km0"], km0)
                if ln < 0.01:
                    continue
                if r["kind"] == "CURVE":
                    rft = ho_radius_ft(abs(r["avg_deg_per100ft"]))
                    pieces.append(
                        f"curve {r['dir']} {r['avg_deg_per100ft']:+.2f}\u00b0 avg/"
                        f"{r['max_deg_per100ft']:.2f} max (R\u2248{rft:.0f} ft) {ln:.2f} m")
                else:
                    pieces.append(f"straight {ln:.2f} m")
            feat = []
            for t in tunnels:
                if t["km0"] <= km1 and t["km1"] >= km0:
                    feat.append("**" + tunnel_label(t) + "** \u2192 scenic portal/mountain")
            for s in sidings:
                if km0 <= s["km"] <= km1:
                    feat.append(f"siding {s['name']} {s['len_km']*FT_PER_KM:.0f} ft \u2192 12 ft std")
            for y in yards:
                if y["km0"] <= km1 and y["km1"] >= km0:
                    feat.append(f"yard ({y['max_tracks']} trk)")
            for m in mts:
                if m["km0"] <= km1 and m["km1"] >= km0 and m["max_tracks"] >= 2:
                    feat.append(f"MT ({m['max_tracks']} trk)")
            track = " \u00b7 ".join(pieces) if pieces else "\u2014"
            L.append(f"| {code}{i+1:02d} | {off0:.2f}\u2013{off1:.2f} | "
                     f"{km0:.2f}\u2013{km1:.2f} | {track} | {'; '.join(dict.fromkeys(feat))} |")
        L.append("")

    with open(os.path.join(OUT, "cpr_scene_modules.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_scene_modules.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
