#!/usr/bin/env python3
"""
Multi-level NOLIX room plan for the FULL CP Vancouver -> Calgary route.

Turns the linear full-route design into a continuous-spiral layout that fits a
10 x 10 ft bedroom with the storage box nesting standard preserved:

  - Storage zone on the floor (buckets, boxes) below 4 ft.
  - Layout mounted above 4 ft; the mainline climbs one level (8 in) per lap
    around the room at a grade comfortably under 4%.
  - Level stack (user-confirmed): hidden 8-track staging below, then L0 / L1 /
    L2 (8-in steps); the top lap may carry a yard.
  - Each visible level carries 1-2 subdivisions so the whole 1,029 km route is
    one continuous Van->Cal transit.
  - Hidden return descends the same bench so the layout is a closed loop
    (continuous running).
  - Modules stay 2-ft-deep stepped wedges (front yard band + raised main band,
    45 deg riser) so they still nest inverted in pairs, 2 x 2 x 4 ft.

Also records the design discussion / decisions / discards (Section 9) so the
reasoning survives.

Reads working/features.json and output/cpr_segments.csv. Produces
output/cpr_nolix_room.md plus render/cpr_nolix_*.png diagrams.
"""
import csv
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")
RENDER = os.path.join(OUT, "render")

MODULE_FT = 4.0
MAX_GRADE = 4.0          # room-grade ceiling, % (user: keep below 4%)
LEVEL_IN = 8.0           # rail-to-rail level spacing, in (user: 8 not 12)
CLEAR_IN = 4.0           # min clearance for double-stack / hi-cube / dbl-deck
RAIL_TOP_MIN = 48.0      # lowest layout rail height, in (above storage zone)
RAIL_TOP_MAX = 64.0      # highest layout rail height, in (L0 + 2 x 8 in)

ROOM_FT = 10.0           # bedroom footprint, both dimensions
BENCH_IN = 24.0          # bench depth against the wall, in
DOOR_IN = 32.0           # door allowance reducing the usable lap, in

# Subdivisions, west -> east, from output/cpr_segments.csv (km boundaries)
SUBS = [
    ("Cascade",            "Vancouver -> Fraser Canyon -> Ashcroft", 0.0, 209.0),
    ("Thompson",           "Ashcroft -> Kamloops",                  209.0, 403.0),
    ("Shuswap",            "Kamloops -> Revelstoke",                403.0, 609.0),
    ("Mountain",           "Revelstoke -> Rogers Pass -> Field",    609.0, 810.0),
    ("Laggan",             "Field -> Banff -> Calgary",             810.0, 1029.3),
]

# Visible laps (west -> east).  Staging sits below L0.  The full 1,029 km route
# is folded into three visible levels (L0/L1/L2) plus hidden staging, matching
# the user's level stack; each visible level carries 1-2 subdivisions.
# Each lap is (lap id, list of subdivision names, front-band anchor).
LAPS = [
    ("L0", ["Cascade", "Thompson"], "Vancouver / Fraser Canyon / Kamloops"),
    ("L1", ["Shuswap", "Mountain"], "Revelstoke / Rogers Pass / Field"),
    ("L2", ["Laggan"],              "Golden / Banff / Calgary (top yard)"),
]

# Level heights: staging rail, then one per visible lap, 8-in steps.
def level_heights():
    h = RAIL_TOP_MIN
    return [h + i * LEVEL_IN for i in range(len(LAPS))]


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    yards, sidings, tunnels = f["yards"], f["sidings"], f["tunnels"]

    # ---- room / grade math
    lap_in = (ROOM_FT * 12 - BENCH_IN) * 4 - DOOR_IN
    grade = LEVEL_IN / lap_in * 100.0
    hs = level_heights()

    def module_rows(a, b):
        ys = [y for y in yards if y["km0"] <= b and y["km1"] >= a]
        ss = [s for s in sidings if a <= s["km"] <= b]
        ts = [t for t in tunnels if t["km0"] <= b and t["km1"] >= a]
        main_mods = int(lap_in / (MODULE_FT * 12))
        return ys, ss, ts, main_mods

    # ---- document
    L = []
    L.append("# CP Vancouver \u2192 Calgary \u2014 Multi-Level NOLIX Room Plan")
    L.append("")
    L.append("The full **1,029 km** route as one continuous mainline that climbs "
             "around a **10 \u00d7 10 ft bedroom**: one level per lap, hidden "
             "staging below, hidden return above, and a closed loop for "
             "continuous running.")
    L.append("")
    L.append(f"Room: **{ROOM_FT:.0f} \u00d7 {ROOM_FT:.0f} ft** \u00b7 layout rail "
             f"**{RAIL_TOP_MIN-LEVEL_IN:.0f}\u2013{RAIL_TOP_MAX:.0f} in** above the floor "
             f"\u00b7 storage below **4 ft** (buckets, boxes).")
    L.append("")

    L.append("## 1. How it fits the room (NOLIX lap math)")
    L.append("")
    L.append(f"Bench depth **{BENCH_IN:.0f} in** on the walls; usable mainline "
             f"per lap \u2248 **{lap_in:.0f} in ({lap_in/12:.0f} ft)** "
             f"({(ROOM_FT*12-BENCH_IN)*4:.0f} in of wall run minus "
             f"{DOOR_IN:.0f} in door allowance).")
    L.append("")
    L.append(f"Level spacing **{LEVEL_IN:.0f} in** rail-to-rail "
             f"(clearance \u2265 {CLEAR_IN:.0f} in for double-stack wells, hi-cube "
             f"boxes, double-deck passenger cars).")
    L.append("")
    L.append(f"**Lap grade \u2248 {grade:.2f}%** \u2014 comfortably under the "
             f"{MAX_GRADE:.0f}% ceiling. "
             f"{len(LAPS)} visible laps \u00d7 {LEVEL_IN:.0f} in = "
             f"**{hs[-1] - RAIL_TOP_MIN:.0f} in** of climb from L0 to the top lap; "
             f"add staging's {LEVEL_IN:.0f} in and the full transit rises "
             f"**{hs[-1] - (RAIL_TOP_MIN - LEVEL_IN):.0f} in**.")
    L.append("")
    L.append("| lap | subdivisions | rail height | front band |")
    L.append("|---|---|---|---|")
    for (code, subs, anchor), h in zip(LAPS, hs):
        L.append(f"| {code} | {' + '.join(subs)} | {h:.0f} in (main) | {anchor} |")
    L.append(f"| S  | staging | {RAIL_TOP_MIN - LEVEL_IN:.0f} in (hidden) | "
             f"Vancouver staging, 8 tracks |")
    L.append("")
    L.append("Grade is 8 in per \u224830 ft lap \u2014 a train does a full "
             "Vancouver \u2192 Calgary run in three visible laps plus the hidden "
             "return. Optional **extra laps** (extra wall passes, deeper lap) give "
             "the hidden descent tracks climb room so they also stay under 4%.")
    L.append("")

    # ---- linear full-route allocation per subdivision
    L.append("## 2. Linear full-route allocation (per subdivision)")
    L.append("")
    L.append("Each lap's **front band** carries that subdivision's yard/sidings/"
             "industries (12-ft train standard, 6-module yard body); the **back "
             "band** carries the mainline at +8 in.  Module counts below are "
             "4-ft bays for the core (CORE) build.")
    L.append("")
    L.append("| subdivision | proto km | yards | sidings | tunnels | main run | core mods |")
    L.append("|---|---|---|---|---|---|---|")
    tot_core = 0
    for code, _, a, b in SUBS:
        ys, ss, ts, main_mods = module_rows(a, b)
        core = main_mods + min(len(ys), 1) * 6 + min(len(ts), 2)
        tot_core += core
        L.append(f"| {code} | {a:.0f}\u2013{b:.0f} | {len(ys)} | {len(ss)} | "
                 f"{len(ts)} | {main_mods} | {core} |")
    L.append(f"|  | **1,029 km** |  |  |  |  | **{tot_core} \u2248 "
             f"{tot_core*MODULE_FT:.0f} ft** |")
    L.append("")
    L.append("Not every prototype yard is built \u2014 one representative yard per "
             "lap (the largest / most iconic) gets the full 6-module body; the "
             "rest appear as front-band tracks, sidings, or are dropped. This is "
             "the same representative-compression used on the mountain section.")
    L.append("")

    # ---- level plan
    L.append("## 3. Level plan (bottom \u2192 top)")
    L.append("")
    L.append("| level | rail | hidden? | front band (visible) | back band (main) |")
    L.append("|---|---|---|---|---|")
    L.append(f"| S | {RAIL_TOP_MIN-LEVEL_IN:.0f} in | **hidden** | 8 staging tracks | "
             f"return descent from L2 |")
    for (code, subs, anchor), h in zip(LAPS, hs):
        L.append(f"| {code} | {h:.0f} in | no | {anchor} | "
                 f"{' + '.join(subs)} main, +8 in |")
    L.append("")
    L.append("Within one lap the **front band is 0 in** and the main is **+8 in** "
             "on the same module \u2014 the visible/raised split.  The main climbs "
             "the next 8 in as it rounds the corner into the next lap's module row.")
    L.append("")
    L.append(f"Total rise staging \u2192 top: **{hs[-1] - (RAIL_TOP_MIN - LEVEL_IN):.0f} in**. "
             f"The top level ({hs[-1]:.0f} in) is reachable from a step stool; keep "
             f"scenery low-relief there.  If reach is a concern, cap the climb at "
             f"2 visible laps and fold the Laggan lap into L1.")
    L.append("")

    # ---- module cross-section / storage
    L.append("## 4. Module cross-section & the nesting box")
    L.append("")
    L.append("The module stays a **2-ft-deep stepped wedge** so any two modules "
             "still nest inverted into the storage box (2 \u00d7 2 \u00d7 4 ft "
             "pairs). Front-to-back:")
    L.append("")
    L.append("```")
    L.append("      front (aisle)                  back (wall)")
    L.append("    0-8 in:  L0 yard/siding track(s)  at 0 in    [visible]")
    L.append("    8-16 in: 45 deg riser             (scenery)")
    L.append("   16-24 in: L1 main track            at +8 in   [visible]")
    L.append("             scenery slope rises 45 deg to the module back")
    L.append("```")
    L.append("")
    L.append("Hidden tracks tuck under the riser at the rear of the front band "
             "(0 in, behind scenery) \u2014 the \u201cback-of-module at 0, hidden\u201d "
             "track.  The two 45 deg faces (riser + back slope) let an inverted "
             "mate nest in: treads meet treads, slopes interlock, box = "
             "2 \u00d7 2 \u00d7 4 ft.")
    L.append("")
    L.append("Design intent is verified with a cardboard cross-section mock-up "
             "before framing; riser steepness (45\u201360 deg) is a free tuning "
             "parameter to guarantee clean nesting.")
    L.append("")

    # ---- operations
    L.append("## 5. Operations \u2014 double main as single + passing")
    L.append("")
    L.append("The physical run is **double main**; it is *operated* as single "
             "track with passing sidings using crossovers:")
    L.append("")
    L.append("- **Continuous running (circles):** run one direction on each "
             "main \u2014 directional.  The hidden return closes the loop.")
    L.append("- **Prototype meets:** line the crossovers so a train changes "
             "tracks at each block; the second main *virtually does not exist* "
             "through that section \u2014 the segment reads as single track with "
             "the mate acting as a passing siding.")
    L.append("- Crossovers are **#6** (matching the 89-ft well-car minimum) and "
             "are thrown by the local switch list, so the \u201cmissing\u201d main "
             "can be re-added later for full double-track ops.")
    L.append("")
    L.append("This gives the familiar two-train-in-one-scene meets without "
             "duplicating the whole subdivision's trackage.")
    L.append("")

    # ---- storage
    L.append("## 6. Storage in the bedroom")
    L.append("")
    L.append("- **Below 4 ft:** buckets, boxes, workbench \u2014 plain storage, no "
             "layout.")
    L.append(f"- **Layout:** rail heights {RAIL_TOP_MIN-LEVEL_IN:.0f}\u2013{RAIL_TOP_MAX:.0f} in "
             f"on wall brackets; nothing on the floor.")
    L.append("- **Modules** come down in 4-ft bays and nest in 2 \u00d7 2 \u00d7 4 ft "
             "boxes (two modules per box).  A lap's yard modules pair with its "
             "main modules; staging modules pair among themselves.")
    L.append("")

    # ---- clearances
    L.append("## 7. Clearances")
    L.append("")
    L.append(f"- Level-to-level **{LEVEL_IN:.0f} in** rail spacing \u226b "
             f"{CLEAR_IN:.0f} in minimum \u2014 double-stack well cars, hi-cube "
             f"boxes, and double-deck passenger cars all clear.")
    L.append("- Main-vs-front-band within a module: 8 in, same headroom.")
    L.append("- Hidden return is 8 in below its visible main \u2014 unseen, "
             "maintenance access from the aisle.")
    L.append("")

    # ---- caveats
    L.append("## 8. Caveats & open questions")
    L.append("")
    L.append("- 10 \u00d7 10 ft at HO is *signature* scale, not a true scale model: "
             "the run is \u2248 1:8,600 rather than 1:1,000.  Each lap carries the "
             "*feel* of its subdivision, not every mile.")
    L.append("- Door allowance: the door wall limits the lap to \u2248 28-30 ft; a "
             "removable bridge or duckunder section may be needed on the door wall "
             "at the lower levels.")
    L.append("- Top-level reach at 64 in needs a step stool; consider capping the "
             "climb at 2 visible laps if reach is a concern.")
    L.append("- NOLIX running = long, slow reveals; meets happen where laps "
             "overlap visually.  True point-to-point (staging-to-staging with no "
             "return) is the discard alternative \u2014 it breaks continuous running.")
    L.append("- The room-grade \u2248 2.3% is a *continuous running grade*, not a "
             "scene-grade: scenes keep the mountain-section \u00b12.5% rule on top "
             "of it only where the prototype climbs (see `cpr_module_plan-comp.md`).")
    L.append("")

    # ---- decision log
    L.append("## 9. Design discussion log (decisions, ideas, discards)")
    L.append("")
    log = [
        ("Asked", "Bedroom size assumed 10 \u00d7 10 ft \u2014 user confirmed, "
                  "with grade ceiling < 4%."),
        ("Asked", "Level spacing \u2014 user accepted 8 in instead of the 12 in "
                  "example; 8 in rail-to-rail gives ~4 in clear for double-stack."),
        ("Asked", "Linear scope \u2014 user chose the FULL 1,029 km Van\u2192Cal, "
                  "not just the mountain section."),
        ("Asked", "Levels \u2014 hidden staging (8 tracks) below L0/L1/L2; top "
                  "level may carry a yard."),
        ("Asked", "Mainline \u2014 double main operated as single + passing via "
                  "crossovers; directional running for circles."),
        ("Asked", "Module tracks \u2014 user wants multiple tracks at different "
                  "heights in one module: front 0 in (visible), back 0 in "
                  "(hidden behind scenery), center ~1 ft (raised), back ~2 ft "
                  "(raised); three visible track bands plus hidden staging."),
        ("Idea",  "Fold the 1,029 km route into one level per lap \u2014 "
                  "Cascade+Thompson / Shuswap+Mountain / Laggan \u2192 three "
                  "visible laps, each 8 in higher."),
        ("Idea",  "Hidden return on the same bench (8 in below the visible main) "
                  "so staging connects top to bottom \u2192 closed loop for "
                  "continuous running."),
        ("Idea",  "Module cross-section = front yard band (0 in) + raised main "
                  "band (+8 in) with a 45 deg riser \u2014 keeps the two-triangle "
                  "nesting box intact."),
        ("Idea",  "Hidden tracks under the riser at the rear of the front band "
                  "gives the requested \u201cback-of-module at 0, hidden\u201d "
                  "track."),
        ("Idea",  "Optional extra laps so hidden descent tracks keep a gentle "
                  "grade (the ~4 in clearance also accommodates dbl-stack/ "
                  "hi-cube/dbl-deck equipment)."),
        ("Discard", "True 1:1000 linear build of the whole route (1,029 m / "
                    "\u2248 845 modules) \u2014 physically impossible in a "
                    "bedroom; kept as the linear *reference* only."),
        ("Discard", "All 34 yards with full 6-module bodies \u2014 one "
                    "representative yard per lap instead."),
        ("Discard", "Pure mushroom (stacked flat shelves, no climb) \u2014 no "
                    "grade interest, and the main loses the continuous-climb "
                    "theatre of the NOLIX."),
        ("Discard", "Staging-to-staging point-to-point with no return \u2014 "
                    "breaks the \u201crun trains in circles\u201d goal."),
        ("Discard", "A single 24-in module with 4 full track levels \u2014 the "
                    "profile stops being a nesting triangle; the raised bands are "
                    "instead kept to two levels per module (front 0 + main +8) "
                    "and the *lap* provides the next 8-in step."),
        ("Open",   "Nesting geometry to be proven with a cardboard mock-up; "
                   "riser angle is the tuning knob."),
        ("Open",   "Door-wall handling at lower levels (removable bridge vs "
                   "duckunder vs skipping a short section)."),
        ("Open",   "Where the hidden return crosses the door wall."),
        ("Open",   "Mushroom vs NOLIX choice is deferred: the NOLIX is the "
                   "current working plan; a wall-hugging mushroom variant "
                   "(flat shelves, no climb) is the fallback if the spiral "
                   "grades prove unworkable."),
    ]
    for kind, text in log:
        L.append(f"- **{kind}:** {text}")
    L.append("")

    with open(os.path.join(OUT, "cpr_nolix_room.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_nolix_room.md ({len(L)} lines)")

    # ---- diagrams
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle, FancyArrowPatch
    except ImportError:
        print("matplotlib not available; skipping diagrams")
        return

    # Footprint: top-down 10x10 room with lap rings, staging, door
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlim(0, ROOM_FT); ax.set_ylim(0, ROOM_FT)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), ROOM_FT, ROOM_FT, fill=False, lw=2,
                           ec="k", label="room 10x10"))
    ax.add_patch(Rectangle((0, 0), DOOR_IN/12, 0.6, fc="#cccccc", ec="none",
                           label=f"door {DOOR_IN:.0f} in"))
    ring = BENCH_IN / 12
    colors = ["#c9d8f0", "#b8e0b8", "#f0d0c0", "#e0c8f0"]
    for i, ((code, subs, anchor), h) in enumerate(zip(LAPS, hs)):
        x = ring * (i + 1)
        ax.add_patch(Rectangle((x, x), ROOM_FT - 2*x, ROOM_FT - 2*x, fill=True,
                               fc=colors[i % 4], ec="k", lw=1))
        ax.text(ROOM_FT/2, ROOM_FT - x - 0.5,
                f"{code}  ({' + '.join(subs)})  rail {h:.0f} in",
                ha="center", fontweight="bold", fontsize=9)
    ax.add_patch(Rectangle((ring, ring), 2.2, 1.0, fc="#888888", ec="k"))
    ax.text(ring + 0.2, ring + 0.55, "S staging\n(hidden)",
            fontsize=8, va="center")
    for i in range(1, len(LAPS)):
        ax.add_patch(FancyArrowPatch((ROOM_FT - ring*(i+1) - 0.3, ROOM_FT/2),
                                     (ROOM_FT - ring*i - 0.3, ROOM_FT/2),
                                     arrowstyle="-|>", mutation_scale=12, lw=1.5))
    ax.set_title("Footprint: three climbing laps around the walls")
    ax.legend(loc="lower right", fontsize=7)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(RENDER, "cpr_nolix_footprint.png"), dpi=130)
    plt.close()

    # Cross-section: front elevation of one wall, levels + clearances + storage
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.add_patch(Rectangle((0, 0), 12, RAIL_TOP_MIN, fc="#eeeeee", ec="k", lw=1))
    ax.text(6, RAIL_TOP_MIN/2, "STORAGE below 4 ft\n(buckets, boxes)",
            ha="center", va="center", fontsize=9)
    all_h = [RAIL_TOP_MIN - LEVEL_IN] + hs
    labels = ["S staging (8 trk, hidden)"] + \
             [f"{code}  {' + '.join(subs)}" for code, subs, _ in LAPS]
    cols = ["#888888", "#c9d8f0", "#b8e0b8", "#f0d0c0"]
    for i, (h, lab, col) in enumerate(zip(all_h, labels, cols)):
        ax.add_patch(Rectangle((0, h), 12, LEVEL_IN, fc=col, ec="k", lw=1))
        ax.text(12.3, h + LEVEL_IN/2, f"{lab}  (rail {h:.0f} in)",
                va="center", fontsize=8)
        if i > 0:
            ax.annotate("", xy=(12, h), xytext=(12, h - LEVEL_IN),
                        arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.text(1, RAIL_TOP_MIN - LEVEL_IN + 1.5,
            f"clearance {CLEAR_IN:.0f} in min for\n2-stack / hi-cube / 2-deck",
            fontsize=7, va="top")
    ax.set_xlim(0, 30); ax.set_ylim(0, hs[-1] + 6)
    ax.axis("off")
    ax.set_title("Wall elevation: staging below, three visible laps at 8-in steps")
    plt.tight_layout()
    plt.savefig(os.path.join(RENDER, "cpr_nolix_section.png"), dpi=130)
    plt.close()
    print(f"wrote {RENDER}/cpr_nolix_footprint.png, {RENDER}/cpr_nolix_section.png")


if __name__ == "__main__":
    main()
