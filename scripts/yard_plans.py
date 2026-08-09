#!/usr/bin/env python3
"""
Turnout & track plans for the modelled yards of the CP mountain section
(Revelstoke -> Field, scenes A-F).

Yards are compressed to the design standard: modelled only long enough for
the 12 ft train (shortest yard track >= 12 ft usable). Each yard is drawn on
4 x 4-ft modules (16 ft total = 12 ft usable + ladder + west lead), with #6
turnouts on a west-end ladder. Prototype track count is not reproduced.

Reads working/features.json. Produces output/cpr_yard_plans-proto.md
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mountain_plan import SCENES, FT_PER_KM

WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

MODULE_KM = 4.0 * 0.3048      # 1.2192 proto km per 4-ft module at 1:1000
NMOD = 4                       # modules per modelled yard
TOTAL_FT = 16.0                # 4 x 4 ft
USABLE_FT = 12.0               # usable length standard

# mountain-section span
A0, B1 = 605.7, 812.0


def plan_lines(name, n_yard, west_note):
    """Render a compact ASCII turnout plan.  All lines short (plain ASCII)."""
    W = 60
    L = []
    L.append("```")
    L.append("                  W (west)                        E (east)")
    L.append("   ft: 0        4        8        12      16")
    L.append("       [ M1    ][ M2    ][ M3    ][ M4    ]")
    L.append("  main " + "=" * (W - 8) + ">")
    L.append("  lead " + "-" * 5 + "\\" + " " * 2 + west_note)
    pad = 8
    for i in range(1, n_yard + 1):
        L.append(f"   t{i}  " + " " * (pad - 3) + "\\"
                 + " " * (i * 1) + "=" * (W - pad - i - 2) + ">")
    L.append("  (west-end ladder, #6 turnouts; each yard track 12 ft usable)")
    L.append("```")
    return L


def module_table(y):
    rows = []
    w0 = y["km0"]
    for i in range(NMOD):
        k0 = w0 + i * MODULE_KM
        k1 = k0 + MODULE_KM
        off0 = i * 4.0
        off1 = (i + 1) * 4.0
        if i == 0:
            content = "west lead + ladder entry (runaround)"
        elif i == 1:
            content = "ladder turnouts + yard-track heads"
        elif i == NMOD - 1:
            content = "yard tracks + east tail clearance"
        else:
            content = "yard tracks (12 ft usable body)"
        rows.append((f"M{i+1}", f"{off0:.0f}-{off1:.0f} ft",
                     f"{k0:.2f}-{k1:.2f} km", content))
    return rows


def n_yard_tracks(max_tracks):
    """Practical modelled count (prototype fan not reproduced)."""
    if max_tracks >= 9:
        return 6
    return 4


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    yards = [y for y in f["yards"] if y["km0"] <= B1 and y["km1"] >= A0]
    yards.sort(key=lambda y: y["km0"])

    L = []
    L.append("# CP Mountain Section \u2014 Yard Turnout & Track Plans")
    L.append("")
    L.append("Modelled yards for Revelstoke, Golden and Field, plus the Rogers "
             "wye and Glacier cluster. Design standard: a yard is **only as long "
             "as the 12 ft train needs** \u2014 shortest yard track \u2265 "
             f"{USABLE_FT:.0f} ft usable \u2014 built on "
             f"{NMOD} \u00d7 4-ft modules ({TOTAL_FT:.0f} ft total). Full "
             "prototype track count is not reproduced; shown are main + lead + "
             "a practical fan of yard tracks. Turnouts are **#6** (right for the "
             "89-ft well-cars).")
    L.append("")
    L.append("On the 1:1000 run compression every prototype yard here spans "
             f"only ~0.4-2.2 km = 1-7 ft of track \u2014 less than the train \u2014 "
             "so each yard is *lengthened* to the 12 ft standard rather than "
             "compressed. The module grid below is the build reference.")
    L.append("")

    for code, scene_name, a, b, _ in SCENES:
        ys = [y for y in yards if y["km0"] <= b and y["km1"] >= a]
        if not ys:
            continue
        L.append(f"## Scene {code} \u2014 {scene_name}: yards")
        L.append("")
        L.append("| prototype | km | proto len | proto ft | tracks | model |")
        L.append("|---|---|---|---|---|---|")
        for y in ys:
            L.append(f"| {y['km0']:.1f}-{y['km1']:.1f} | {y['km0']:.2f}\u2013{y['km1']:.2f} | "
                     f"{y['len_km']*1000:.0f} m | {y['len_km']*FT_PER_KM:.0f} ft | "
                     f"{y['max_tracks']} | "
                     f"{TOTAL_FT:.0f} ft ({NMOD} \u00d7 4-ft) |")
        L.append("")

        for y in ys:
            ny = n_yard_tracks(y["max_tracks"])
            L.append(f"### {y['km0']:.1f}-{y['km1']:.1f} km \u2014 {y['max_tracks']} trk prototype")
            L.append("")
            L.append(f"Prototype {y['len_km']*1000:.0f} m ({y['len_km']*FT_PER_KM:.0f} ft). "
                     f"Modelled: main + west lead + **{ny} yard tracks**, "
                     f"each {USABLE_FT:.0f} ft usable over "
                     f"{NMOD} \u00d7 4-ft modules. Prototype fan not reproduced.")
            L.append("")
            L.append("| mod | model offset | proto km | module carries |")
            L.append("|---|---|---|---|")
            for m, o, k, c in module_table(y):
                L.append(f"| {m} | {o} | {k} | {c} |")
            L.append("")
            L.extend(plan_lines("", ny, "west runaround"))
            L.append("")

    L.append("## Notes")
    L.append("")
    L.append("- **#6 turnouts** throughout: 89-ft well-cars and AC4400s track "
             "cleanly; a #6 frog is ~6 in in HO so the whole ladder fits in the "
             "west 2 ft of M1-M2.")
    L.append("- **12 ft usable** matches the siding standard, so any yard track "
             "holds the same 2 \u00d7 5-well + 2 AC4400 + caboose consist that a "
             "siding holds.")
    L.append("- Add a **runaround** via the west lead/headshunt so a solo loco "
             "can pull around the consist; the east end is a simple stub clear of "
             "the main.")
    L.append("- Prototype track counts (Field 7, Golden up to 10, Revelstoke 9) "
             "are scenery-level fans in the mountain model; model only what "
             "operation needs.")
    L.append("- Mount yards flat; grade handling is in `cpr_grade_overlay-proto.md`.")

    with open(os.path.join(OUT, "cpr_yard_plans-proto.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_yard_plans-proto.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
