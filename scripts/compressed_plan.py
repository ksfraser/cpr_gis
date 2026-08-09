#!/usr/bin/env python3
"""
Compressed module plan for the CP mountain section (Revelstoke -> Field).

Applies the unified end-plate modular standard (Free-mo style) plus selective
compression to the -proto 1:1000 designs:

  - Yards: 5-7 modules each so the shortest yard track is the 12 ft design
    standard (12 ft usable = 3 of the yard's 4-ft modules).
  - Single-track runs: 18 km (15 modules) of plain mainline shrinks to 1-2
    scenic modules, which can be omitted via the common end plates.
  - Tunnels: one portal/scenic module each.
  - Module width is free (single track 12-18 in; yards within the 2-ft club
    standard) as long as the unified end plates and rail height are shared.

Grade rule: model grade <= 2.5% everywhere. Yards are built flat; runs and
tunnel/portal modules carry the scene's prototype ruling grade (capped at
2.5%), signed eastbound. The full Vancouver->Calgary climb is NOT reproduced;
only the mountain-section grades show.

Compressed module IDs carry a -C indicator (e.g. A-C01) to distinguish them
from the 1:1000 -proto module IDs (A01...). Documents use the -comp suffix.

Reads working/profile.csv and working/features.json. Produces
output/cpr_modular_standard-comp.md and output/cpr_module_plan-comp.md
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

MODULE_M = 4.0 * 0.3048  # 1.2192 m per 4-ft module
MAX_GRADE = 2.5          # model grade cap, %

# Per-module rows:
#   (mod id, n x 4-ft modules, kind, name, carries, width, grade-class)
# grade-class: "yard" (built flat), "run" / "tunnel" (carry scene ruling grade)
MODULES = {
    "A": [
        ("A-C01", 1, "FILLER", "Revelstoke west run", "single track, approach", "12-18 in", "run"),
        ("A-C02", 1, "CORE", "Revelstoke yard \u2014 west lead", "headshunt + ladder entry", "24 in", "yard"),
        ("A-C03", 1, "CORE", "Revelstoke yard \u2014 ladder", "#6 ladder turnouts", "24 in", "yard"),
        ("A-C04", 1, "CORE", "Revelstoke yard \u2014 body 1", "yard tracks (station)", "24 in", "yard"),
        ("A-C05", 1, "CORE", "Revelstoke yard \u2014 body 2", "yard tracks", "24 in", "yard"),
        ("A-C06", 1, "CORE", "Revelstoke yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in", "yard"),
        ("A-C07", 1, "CORE", "Revelstoke yard \u2014 east tail", "east clearance tail", "24 in", "yard"),
        ("A-C08", 1, "FILLER", "Revelstoke east run", "single track", "12-18 in", "run"),
        ("A-C09", 5, "OPTIONAL", "Revelstoke east yard (5 trk)", "satellite yard, 12 ft usable", "24 in", "yard"),
    ],
    "B": [
        ("B-C01", 1, "FILLER", "Eagle Pass run", "single track up the Illecillewaet valley", "12-18 in", "run"),
        ("B-C02", 1, "CORE", "Eagle Pass bore (585 m)", "tunnel portal \u2192 scenic mountain", "24 in", "tunnel"),
        ("B-C03", 1, "FILLER", "Eagle Pass \u2192 Rogers run", "single track", "12-18 in", "run"),
    ],
    "C": [
        ("C-C01", 1, "CORE", "MacDonald Tunnel (14.6 km)", "portal-to-portal scenic mountain", "24 in", "tunnel"),
        ("C-C02", 1, "CORE", "Rogers summit wye \u2014 west", "wye throat + main", "24 in", "yard"),
        ("C-C03", 1, "CORE", "Rogers summit wye \u2014 ladder", "#6 ladder turnouts", "24 in", "yard"),
        ("C-C04", 1, "CORE", "Rogers summit wye \u2014 body 1", "wye yard tracks", "24 in", "yard"),
        ("C-C05", 1, "CORE", "Rogers summit wye \u2014 body 2", "wye yard tracks", "24 in", "yard"),
        ("C-C06", 1, "CORE", "Rogers summit wye \u2014 body 3", "wye yard tracks (12 ft usable)", "24 in", "yard"),
        ("C-C07", 1, "CORE", "Rogers summit wye \u2014 east tail", "east clearance tail", "24 in", "yard"),
        ("C-C08", 1, "FILLER", "Rogers \u2192 Glacier run", "single track downhill", "12-18 in", "run"),
        ("C-C09", 1, "CORE", "Glacier yard \u2014 west lead", "headshunt + ladder entry", "24 in", "yard"),
        ("C-C10", 1, "CORE", "Glacier yard \u2014 ladder", "#6 ladder turnouts", "24 in", "yard"),
        ("C-C11", 1, "CORE", "Glacier yard \u2014 body 1", "yard tracks", "24 in", "yard"),
        ("C-C12", 1, "CORE", "Glacier yard \u2014 body 2", "yard tracks", "24 in", "yard"),
        ("C-C13", 1, "CORE", "Glacier yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in", "yard"),
        ("C-C14", 1, "CORE", "Glacier yard \u2014 east tail", "east clearance tail", "24 in", "yard"),
        ("C-C15", 1, "FILLER", "Glacier \u2192 Beavermouth run", "single track", "12-18 in", "run"),
        ("C-C16", 2, "OPTIONAL", "Stoney Creek / Glacier sidings", "two 12 ft sidings", "24 in", "yard"),
    ],
    "D": [
        ("D-C01", 1, "FILLER", "Beavermouth run", "single track, Beavermouth sidings vicinity", "12-18 in", "run"),
        ("D-C02", 1, "CORE", "Albert Canyon bore (619 m)", "tunnel portal \u2192 scenic mountain", "24 in", "tunnel"),
        ("D-C03", 1, "FILLER", "Albert Canyon \u2192 Golden run", "single track", "12-18 in", "run"),
    ],
    "E": [
        ("E-C01", 1, "FILLER", "Golden west run", "single track", "12-18 in", "run"),
        ("E-C02", 1, "CORE", "Golden yard \u2014 west lead", "headshunt + ladder entry", "24 in", "yard"),
        ("E-C03", 1, "CORE", "Golden yard \u2014 ladder", "#6 ladder turnouts", "24 in", "yard"),
        ("E-C04", 1, "CORE", "Golden yard \u2014 body 1", "yard tracks (station)", "24 in", "yard"),
        ("E-C05", 1, "CORE", "Golden yard \u2014 body 2", "yard tracks", "24 in", "yard"),
        ("E-C06", 1, "CORE", "Golden yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in", "yard"),
        ("E-C07", 1, "CORE", "Golden yard \u2014 east tail", "east clearance tail", "24 in", "yard"),
        ("E-C08", 1, "CORE", "Golden short bore (276 m)", "tunnel portal \u2192 scenic mountain", "24 in", "tunnel"),
        ("E-C09", 1, "OPTIONAL", "Hill siding", "12 ft siding", "24 in", "yard"),
        ("E-C10", 1, "FILLER", "Golden \u2192 Yoho run", "single track", "12-18 in", "run"),
    ],
    "F": [
        ("F-C01", 1, "FILLER", "Yoho run", "single track up the Yoho valley", "12-18 in", "run"),
        ("F-C02", 2, "OPTIONAL", "Leanchoil / Palliser sidings", "two 12 ft sidings", "24 in", "yard"),
        ("F-C03", 1, "FILLER", "Yoho \u2192 Field run", "single track", "12-18 in", "run"),
        ("F-C04", 1, "CORE", "Field yard \u2014 west lead", "headshunt + ladder entry", "24 in", "yard"),
        ("F-C05", 1, "CORE", "Field yard \u2014 ladder", "#6 ladder turnouts", "24 in", "yard"),
        ("F-C06", 1, "CORE", "Field yard \u2014 body 1", "yard tracks (station)", "24 in", "yard"),
        ("F-C07", 1, "CORE", "Field yard \u2014 body 2", "yard tracks", "24 in", "yard"),
        ("F-C08", 1, "CORE", "Field yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in", "yard"),
        ("F-C09", 1, "CORE", "Field yard \u2014 east tail", "east clearance tail", "24 in", "yard"),
        ("F-C10", 1, "CORE", "Kicking Horse portal", "start of spiral-tunnel scenery (optional add-on)", "24 in", "tunnel"),
    ],
}

STANDARD = """# CP Modular Standard (HO) \u2014 Revelstoke \u2192 Field  [-comp]

Applies to every compressed module in `cpr_module_plan-comp.md`. Built on the
unified end-plate convention used by North-American HO modular groups (Free-mo
style): one shared rail height and end-plate mounting pattern, with module
**width left free**. Because the track is centred and the rail height is fixed
at every end plate, modules of different widths still join cleanly \u2014 and any
module can be left out of a setup without breaking the mainline.

Compressed-build artifacts carry a **-comp** indicator (module IDs use **-C**,
e.g. `A-C01`) to distinguish them from the linear **-proto** 1:1000 designs.

## 1. Equipment design standard

- **Scale:** HO 1:87.
- **Train:** 12 ft = 2 \u00d7 5-well well-cars + 2 AC4400 + caboose
  (\u2248 1,200 prototype ft).
- **Siding/yard rule:** shortest yard/siding track \u2265 **12 ft usable**. A
  12 ft usable body sits on 3 \u00d7 4-ft modules; add a ladder and west lead +
  east tail and a yard is **5-7 modules** total.

## 2. Scale & compression

- The `*-proto` docs keep the pure **1:1000 run compression** (1 proto km =
  1 model m) as the linear reference.
- The compressed build (**this standard + `cpr_module_plan-comp.md`**) applies
  selective compression instead:
  - Yards: 5-7 modules so the shortest track is 12 ft.
  - Plain single-track runs (18 km = ~15 modules): 1-2 scenic modules, omittable.
  - Tunnels: one portal/scenic module.

## 3. Module geometry

- **Length:** 4 ft (1.2192 m) build module; yards are several 4-ft modules, not
  one long box.
- **Width:** free. Recommended:
  - Single-track scenic modules: **12-18 in** (no need for 2 ft).
  - Yard modules: **\u2264 24 in** so they match the 2-ft club/Free-mo width.
  - Big-city terminals (Calgary, Vancouver, Kamloops, outside this section):
    may be wider than 24 in.
- **Frame:** dimensional lumber OK; legs built in, folding, self-supporting.

## 4. Unified end plates (Free-mo style)

- End plates: **3/4 in birch plywood** (or equivalent flat, warp-resistant),
  vertical, flat, parallel to each other and perpendicular to the track.
- **Rail head height: 50 in** above the floor, adjustable 49-51 in via leg
  feet. Grade modules allowed up to 62 in in 3/4 in steps (see \u00a77).
- **Track centred** on every end plate; the last **6 in of track is straight,
  level and square** at the ends; rails stop ~1 in short of the plate with ties
  and ballast to the edge.
- **Join:** C-clamps or 1/4-20 bolts through the plates; fitter rails with a
  metal joiner at each joint (insulated where a block gap is wanted).
- **Why widths can differ:** the mounting pattern, hole spacing, track centre
  and rail height are all shared; only the plate width varies.

## 5. Electrical (Free-mo style)

- **Track Bus:** 2 \u00d7 12-16 AWG, Anderson Powerpole PP15-45 (30 A) at each
  end, stacked vertically, hood up; top connector = left rail.
- **Accessory Bus:** PP15-45 stacked horizontally.
- **Booster Common:** single wire, one PP15-45.
- **DCC/LocoNet:** RJ12 (6-conductor) jack at each end, straight-through
  2-ft cables.
- Droppers (24 AWG, \u2264 6 in) on every rail section; rail joiners are not
  an electrical connection.

## 6. Selective omission

Modules are tagged in `cpr_module_plan-comp.md`:

- **CORE** \u2014 the minimum operating layout (yards, tunnels, portals).
- **FILLER** \u2014 omittable scenic single-track runs.
- **OPTIONAL** \u2014 sidings and satellite yards for prototype flavour.

Any FILLER/OPTIONAL module can be dropped and the neighbours still join on the
common end plates \u2014 skip them during a first build, add them later.

## 7. Grades

- **Model grade is capped at 2.5%** everywhere.
- Yards are built flat; runs and tunnel/portal modules carry the scene's
  prototype ruling grade (clamped to \u00b12.5%), signed eastbound. The full
  Vancouver\u2192Calgary climb is NOT reproduced; only mountain-section grades show.
- Per-module grades are listed in `cpr_module_plan-comp.md` and drawn in
  `render/cpr_elevation_profile.png`.
- If the prototype is flat in a scene, the modules are flat \u2014 no artificial
  grade is added.

## 8. Handling

- Prefer modules \u2264 6 ft long; the 4-ft module is the standard bay.
- Yards, tunnels and runs are built as multiple 4-ft modules that bolt together
  on the common plates.
"""


def _load_profile():
    rows = list(csv.DictReader(open(os.path.join(WORK, "profile.csv"))))
    dist = np.array([float(r["dist_km"]) for r in rows])
    elev = np.array([float(r["elev_m"]) for r in rows])
    grade = np.array([float(r["grade_1km_pct"])
                      if r["grade_1km_pct"].strip() else np.nan for r in rows])
    intun = np.array([int(r["in_tunnel"]) if r["in_tunnel"] else 0 for r in rows])
    return dist, elev, grade, intun


def scene_grade(code, a, b, dist, elev, grade, intun):
    """Signed model grade (%) for a scene: the 90th-percentile prototype grade
    (robust vs DEM noise) capped at MAX_GRADE, sign from eastbound net
    elevation change.  Flat if the prototype is flat."""
    e0 = float(np.interp(a, dist, elev))
    e1 = float(np.interp(b, dist, elev))
    net = e1 - e0
    mask = (dist >= a) & (dist <= b) & np.isfinite(grade) & (intun == 0)
    if mask.sum() == 0:
        return 0.0
    ruling = float(np.percentile(np.abs(grade[mask]), 90))
    if ruling < 0.5:            # proto effectively flat
        return 0.0
    mag = min(ruling, MAX_GRADE)
    if abs(net) < 1.0:          # proto grades cancel out (valley floor)
        return 0.0
    return mag if net > 0 else -mag


def proto_modules(a, b):
    return int((b - a) / MODULE_M) + 1


def compute_elevations():
    """Return ordered list of dicts: one per module with grade% and cm rise."""
    dist, elev, grade, intun = _load_profile()
    out = []
    cum = 0.0
    for code, _, a, b, _ in SCENES:
        sg = scene_grade(code, a, b, dist, elev, grade, intun)
        for mid, nbays, kind, name, carries, width, gclass in MODULES[code]:
            lm = nbays * MODULE_M
            pct = sg if gclass in ("run", "tunnel") else 0.0
            de_cm = pct / 100.0 * lm * 100.0   # %/100 * length(m) -> m, *100 -> cm
            cum += de_cm
            out.append(dict(code=code, mid=mid, bays=nbays, len_m=lm,
                            pct=pct, de_cm=de_cm, cum_cm=cum,
                            kind=kind, name=name, gclass=gclass))
    return out


def write_standard():
    with open(os.path.join(OUT, "cpr_modular_standard-comp.md"), "w") as fh:
        fh.write(STANDARD)
    print(f"wrote {OUT}/cpr_modular_standard-comp.md "
          f"({len(STANDARD.splitlines())} lines)")


def write_plan(elevs):
    L = []
    L.append("# CP Mountain Section \u2014 Compressed Module Plan  [-comp]")
    L.append("")
    L.append("Selective compression of the `-proto` 1:1000 designs, built on the "
             "unified end-plate standard (`cpr_modular_standard-comp.md`): yards "
             "shrink to 5-7 modules so the shortest yard track is the **12 ft** "
             "design standard; plain single-track runs shrink to 1-2 omittable "
             "scenic modules; tunnels are one portal module each. **Compressed "
             "module IDs carry the -C indicator** (e.g. `A-C01`) to keep them "
             "distinct from the 1:1000 `-proto` IDs.")
    L.append("")
    L.append("Diagrams (track + elevation) are in `render/` \u2014 see the scene "
             "images, `render/cpr_compressed_overview.png` and "
             "`render/cpr_elevation_profile.png`.")
    L.append("")

    L.append("| scene | proto km | proto mods | core mods | +optional | build ft |")
    L.append("|---|---|---|---|---|---|")
    tot_p = tot_c = tot_o = 0
    scene_rows = []
    for code, name, a, b, _ in SCENES:
        mods = MODULES[code]
        p = proto_modules(a, b)
        core = sum(n for _, n, k, *_ in mods if k == "CORE")
        opt = sum(n for _, n, k, *_ in mods if k == "OPTIONAL")
        tot_p += p
        tot_c += core
        tot_o += opt
        scene_rows.append((code, name, p, core, opt))
        L.append(f"| {code} | {name} | {b-a:.0f} | {p} | {core} | "
                 f"{core}+{opt} | {core*4}-{(core+opt)*4} |")
    L.append(f"|  | **total** | **206** | **{tot_p}** | **{tot_c}** | "
             f"**{tot_c}+{tot_o}** | **{tot_c*4}-{(tot_c+tot_o)*4}** |")
    L.append("")
    L.append(f"**Reduction:** {tot_p} \u2192 {tot_c} core modules "
             f"({100*(1-tot_c/tot_p):.0f}% fewer); "
             f"{tot_c*4}-{(tot_c+tot_o)*4} ft of bench vs "
             f"{tot_p*4} ft at full 1:1000 build.")
    L.append("")

    for code, name, p, core, opt in scene_rows:
        L.append(f"## Scene {code} \u2014 {name}  "
                 f"({p} proto \u2192 {core} core modules)")
        L.append("")
        L.append("| mod | 4-ft bays | type | name | carries | width |")
        L.append("|---|---|---|---|---|---|")
        for mid, n, kind, mname, carries, width, gclass in MODULES[code]:
            L.append(f"| {mid} | {n} | **{kind}** | {mname} | {carries} | {width} |")
        L.append("")
        L.append(f"Track diagram: `render/cpr_scene_{code}.png`")
        L.append("")

    L.append("## Grades & elevation (model)")
    L.append("")
    L.append(f"Model grade capped at **\u00b1{MAX_GRADE:.1f}%**; yards flat; runs/"
             "tunnels carry the scene ruling grade (clamped) signed eastbound. "
             "The full Vancouver\u2192Calgary climb is not reproduced. Rise is "
             "per 4-ft module bay.")
    L.append("")
    L.append("| mod | bays | grade % | len m | \u0394elev cm | elev cm |")
    L.append("|---|---|---|---|---|---|")
    for e in elevs:
        L.append(f"| {e['mid']} | {e['bays']} | {e['pct']:+.2f} | "
                 f"{e['len_m']:.2f} | {e['de_cm']:+.2f} | {e['cum_cm']:+.2f} |")
    L.append("")
    peaks = [e for e in elevs if abs(e["pct"]) > 0.05]
    maxabs = max((abs(e["pct"]) for e in elevs), default=0.0)
    total_len = sum(e["len_m"] for e in elevs)
    net_pct = elevs[-1]["cum_cm"] / total_len if total_len else 0.0
    L.append(f"Steepest model grade: **{maxabs:.2f}%**. Total model rise: "
             f"**{elevs[-1]['cum_cm']:+.1f} cm** over {total_len:.1f} m of layout "
             f"(net {net_pct:+.2f}%). Mount flat where shown; graded modules ride "
             "up/down the bench in the drawn profile.")
    L.append("")
    L.append("### Grade-carrying modules (where the proto has a grade)")
    L.append("")
    L.append("| scene | model grade | modules |")
    L.append("|---|---|---|")
    by_scene = {}
    for e in elevs:
        if abs(e["pct"]) > 0.05:
            by_scene.setdefault((e["code"], e["pct"]), []).append(e["mid"])
    for (code, pct), mids in by_scene.items():
        L.append(f"| {code} | {pct:+.2f}% | " + ", ".join(mids) + " |")
    L.append("")

    L.append("## Yard bodies (all scenes)")
    L.append("")
    L.append("Every modelled yard uses the same 6-module body so the shortest "
             "yard track is 12 ft usable:")
    L.append("")
    L.append("| bay | module | carries |")
    L.append("|---|---|---|")
    L.append("| 1 | west lead / headshunt | runaround, ladder entry |")
    L.append("| 2 | ladder | #6 turnouts (89-ft well-cars) |")
    L.append("| 3-5 | body | yard tracks, **12 ft usable** |")
    L.append("| 6 | east tail | clearance clear of the main |")
    L.append("")
    L.append("See `cpr_yard_plans-proto.md` for the turnout plans; the compressed "
             "yards use the identical ladder but on 6 modules instead of the "
             "1:1000 fan.")
    L.append("")
    L.append("## Minimum operating layout (core only)")
    L.append("")
    L.append(f"**{tot_c} modules, {tot_c*4} ft**, west to east:")
    L.append("")
    core_ids = [m[0] for c, *_ in SCENES for m in MODULES[c] if m[2] == "CORE"]
    L.append(" \u2014 ".join(core_ids))
    L.append("")

    with open(os.path.join(OUT, "cpr_module_plan-comp.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_module_plan-comp.md ({len(L)} lines)")


def main():
    json.load(open(os.path.join(WORK, "features.json")))
    elevs = compute_elevations()
    write_standard()
    write_plan(elevs)


if __name__ == "__main__":
    main()
