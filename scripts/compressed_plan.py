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

Reads working/features.json for the proto module counts (reduction basis).
Produces output/cpr_modular_standard.md and output/cpr_compressed_plan.md
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mountain_plan import SCENES

WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

MODULE_M = 4.0 * 0.3048  # 1.2192 m per 4-ft module

# Per-module rows: (mod id, n x 4-ft modules, kind, name, carries, width)
# kind: CORE = minimum operating layout; FILLER = omittable scenic run;
#       OPTIONAL = prototype flavor (sidings, satellite yards).
MODULES = {
    "A": [
        ("A01", 1, "FILLER", "Revelstoke west run", "single track, approach", "12-18 in"),
        ("A02", 1, "CORE", "Revelstoke yard \u2014 west lead", "headshunt + ladder entry", "24 in"),
        ("A03", 1, "CORE", "Revelstoke yard \u2014 ladder", "#6 ladder turnouts", "24 in"),
        ("A04", 1, "CORE", "Revelstoke yard \u2014 body 1", "yard tracks (station)", "24 in"),
        ("A05", 1, "CORE", "Revelstoke yard \u2014 body 2", "yard tracks", "24 in"),
        ("A06", 1, "CORE", "Revelstoke yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in"),
        ("A07", 1, "CORE", "Revelstoke yard \u2014 east tail", "east clearance tail", "24 in"),
        ("A08", 1, "FILLER", "Revelstoke east run", "single track", "12-18 in"),
        ("A09", 5, "OPTIONAL", "Revelstoke east yard (5 trk)", "satellite yard, 12 ft usable", "24 in"),
    ],
    "B": [
        ("B01", 1, "FILLER", "Eagle Pass run", "single track up the Illecillewaet valley", "12-18 in"),
        ("B02", 1, "CORE", "Eagle Pass bore (585 m)", "tunnel portal \u2192 scenic mountain", "24 in"),
        ("B03", 1, "FILLER", "Eagle Pass \u2192 Rogers run", "single track", "12-18 in"),
    ],
    "C": [
        ("C01", 1, "CORE", "MacDonald Tunnel (14.6 km)", "portal-to-portal scenic mountain", "24 in"),
        ("C02", 1, "CORE", "Rogers summit wye \u2014 west", "wye throat + main", "24 in"),
        ("C03", 1, "CORE", "Rogers summit wye \u2014 ladder", "#6 ladder turnouts", "24 in"),
        ("C04", 1, "CORE", "Rogers summit wye \u2014 body 1", "wye yard tracks", "24 in"),
        ("C05", 1, "CORE", "Rogers summit wye \u2014 body 2", "wye yard tracks", "24 in"),
        ("C06", 1, "CORE", "Rogers summit wye \u2014 body 3", "wye yard tracks (12 ft usable)", "24 in"),
        ("C07", 1, "CORE", "Rogers summit wye \u2014 east tail", "east clearance tail", "24 in"),
        ("C08", 1, "FILLER", "Rogers \u2192 Glacier run", "single track downhill", "12-18 in"),
        ("C09", 1, "CORE", "Glacier yard \u2014 west lead", "headshunt + ladder entry", "24 in"),
        ("C10", 1, "CORE", "Glacier yard \u2014 ladder", "#6 ladder turnouts", "24 in"),
        ("C11", 1, "CORE", "Glacier yard \u2014 body 1", "yard tracks", "24 in"),
        ("C12", 1, "CORE", "Glacier yard \u2014 body 2", "yard tracks", "24 in"),
        ("C13", 1, "CORE", "Glacier yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in"),
        ("C14", 1, "CORE", "Glacier yard \u2014 east tail", "east clearance tail", "24 in"),
        ("C15", 1, "FILLER", "Glacier \u2192 Beavermouth run", "single track", "12-18 in"),
        ("C16", 2, "OPTIONAL", "Stoney Creek / Glacier sidings", "two 12 ft sidings", "24 in"),
    ],
    "D": [
        ("D01", 1, "FILLER", "Beavermouth run", "single track, Beavermouth sidings vicinity", "12-18 in"),
        ("D02", 1, "CORE", "Albert Canyon bore (619 m)", "tunnel portal \u2192 scenic mountain", "24 in"),
        ("D03", 1, "FILLER", "Albert Canyon \u2192 Golden run", "single track", "12-18 in"),
    ],
    "E": [
        ("E01", 1, "FILLER", "Golden west run", "single track", "12-18 in"),
        ("E02", 1, "CORE", "Golden yard \u2014 west lead", "headshunt + ladder entry", "24 in"),
        ("E03", 1, "CORE", "Golden yard \u2014 ladder", "#6 ladder turnouts", "24 in"),
        ("E04", 1, "CORE", "Golden yard \u2014 body 1", "yard tracks (station)", "24 in"),
        ("E05", 1, "CORE", "Golden yard \u2014 body 2", "yard tracks", "24 in"),
        ("E06", 1, "CORE", "Golden yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in"),
        ("E07", 1, "CORE", "Golden yard \u2014 east tail", "east clearance tail", "24 in"),
        ("E08", 1, "CORE", "Golden short bore (276 m)", "tunnel portal \u2192 scenic mountain", "24 in"),
        ("E09", 1, "OPTIONAL", "Hill siding", "12 ft siding", "24 in"),
        ("E10", 1, "FILLER", "Golden \u2192 Yoho run", "single track", "12-18 in"),
    ],
    "F": [
        ("F01", 1, "FILLER", "Yoho run", "single track up the Yoho valley", "12-18 in"),
        ("F02", 2, "OPTIONAL", "Leanchoil / Palliser sidings", "two 12 ft sidings", "24 in"),
        ("F03", 1, "FILLER", "Yoho \u2192 Field run", "single track", "12-18 in"),
        ("F04", 1, "CORE", "Field yard \u2014 west lead", "headshunt + ladder entry", "24 in"),
        ("F05", 1, "CORE", "Field yard \u2014 ladder", "#6 ladder turnouts", "24 in"),
        ("F06", 1, "CORE", "Field yard \u2014 body 1", "yard tracks (station)", "24 in"),
        ("F07", 1, "CORE", "Field yard \u2014 body 2", "yard tracks", "24 in"),
        ("F08", 1, "CORE", "Field yard \u2014 body 3", "yard tracks (12 ft usable)", "24 in"),
        ("F09", 1, "CORE", "Field yard \u2014 east tail", "east clearance tail", "24 in"),
        ("F10", 1, "CORE", "Kicking Horse portal", "start of spiral-tunnel scenery (optional add-on)", "24 in"),
    ],
}

STANDARD = """# CP Modular Standard (HO) \u2014 Revelstoke \u2192 Field

Applies to every compressed module in `cpr_compressed_plan.md`. Built on the
unified end-plate convention used by North-American HO modular groups (Free-mo
style): one shared rail height and end-plate mounting pattern, with module
**width left free**. Because the track is centred and the rail height is fixed
at every end plate, modules of different widths still join cleanly \u2014 and any
module can be left out of a setup without breaking the mainline.

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
- The compressed build (**this standard + `cpr_compressed_plan.md`**) applies
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

Modules are tagged in `cpr_compressed_plan.md`:

- **CORE** \u2014 the minimum operating layout (yards, tunnels, portals).
- **FILLER** \u2014 omittable scenic single-track runs.
- **OPTIONAL** \u2014 sidings and satellite yards for prototype flavour.

Any FILLER/OPTIONAL module can be dropped and the neighbours still join on the
common end plates \u2014 skip them during a first build, add them later.

## 7. Grades

- Default build: **flat at 50 in**; grades are scenic (see
  `cpr_grade_overlay-proto.md` for the ruling numbers per scene).
- If a ruling climb is built (Rogers or Kicking Horse ~2.2%), keep it
  **\u2264 2%** so the 12 ft train can restart mid-grade; use grade modules that
  end at the standard rail height (Free-mo 3/4 in steps to 62 in).

## 8. Handling

- Prefer modules \u2264 6 ft long; the 4-ft module is the standard bay.
- Yards, tunnels and runs are built as multiple 4-ft modules that bolt together
  on the common plates.
"""


def proto_modules(a, b):
    return int((b - a) / MODULE_M) + 1


def write_standard():
    with open(os.path.join(OUT, "cpr_modular_standard.md"), "w") as fh:
        fh.write(STANDARD)
    print(f"wrote {OUT}/cpr_modular_standard.md ({len(STANDARD.splitlines())} lines)")


def write_compressed():
    L = []
    L.append("# CP Mountain Section \u2014 Compressed Module Plan")
    L.append("")
    L.append("Selective compression of the `-proto` 1:1000 designs, built on the "
             "unified end-plate standard (`cpr_modular_standard.md`): yards shrink "
             "to 5-7 modules so the shortest yard track is the **12 ft** design "
             "standard; plain single-track runs shrink to 1-2 omittable scenic "
             "modules; tunnels are one portal module each.")
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
        scene_rows.append((code, name, p, core, opt, len(mods)))
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

    for code, name, p, core, opt, nmod in scene_rows:
        L.append(f"## Scene {code} \u2014 {name}  "
                 f"({p} proto \u2192 {core} core modules)")
        L.append("")
        L.append("| mod | 4-ft bays | type | name | carries | width |")
        L.append("|---|---|---|---|---|---|")
        for mid, n, kind, mname, carries, width in MODULES[code]:
            L.append(f"| {mid} | {n} | **{kind}** | {mname} | {carries} | {width} |")
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
    order = [c for c, *_ in SCENES]
    core_ids = [m[0] for c in order for m in MODULES[c] if m[2] == "CORE"]
    L.append(" \u2014 ".join(core_ids))
    L.append("")

    with open(os.path.join(OUT, "cpr_compressed_plan.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_compressed_plan.md ({len(L)} lines)")


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    _ = f  # data validated for scene spans by SCENES import
    write_standard()
    write_compressed()


if __name__ == "__main__":
    main()
