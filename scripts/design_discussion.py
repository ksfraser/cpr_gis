#!/usr/bin/env python3
"""
Design discussion document for the CP mountain-section model railroad
(Revelstoke -> Field, scenes A-F).

Explains the 1:1000 "-proto" reference build and the selective-compression
philosophy, tabulates river crossings, mountain/tunnel features and road/rail
interactions (with the Revelstoke lake buffer), and defines the 45-degree
nesting storage module.

Reads working/features.json, profile.csv, road_crossings.json,
road_corridors.json.  Produces output/cpr_design_discussion.md
"""
import csv
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from mountain_plan import SCENES, FT_PER_KM
from compressed_plan import MODULES, MODULE_M

WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

# Significant river/stream crossings: rail bridge centre km -> water body
RIVERS = {
    605.9: "Columbia River (Revelstoke west approach, 412 m crossing)",
    606.6: "Columbia River arm / Revelstoke Lake (Revelstoke)",
    614.1: "Illecillewaet River (Revelstoke east)",
    627.9: "Illecillewaet River",
    650.3: "Illecillewaet River (upper Eagle Pass)",
    652.9: "Illecillewaet tributary (Eagle Pass)",
    658.2: "Illecillewaet headwaters (Rogers summit)",
    683.8: "Stoney Creek (east of Connaught/MacDonald)",
    687.9: "Stoney Creek (323 m trestle)",
    696.5: "Asulkan / Illecillewaet (Glacier)",
    704.1: "Beaver River (Beavermouth)",
    725.8: "Beaver River / Albert Canyon",
    738.1: "Blaeberry River (Golden west)",
    766.5: "Kicking Horse River (Glenogle)",
}

MOUNTAINS = {
    "A": "Columbia Valley floor at Revelstoke; the west approach rides the "
         "Columbia River / Revelstoke Lake shoreline into town.",
    "B": "Monashee Mountains \u2014 the Illecillewaet valley climbing to Eagle "
         "Pass; the tightest curves in the section (16 deg/100 ft at km 654). "
         "The Trans-Canada Highway climbs the parallel route.",
    "C": "Selkirk Mountains \u2014 Rogers Pass summit (1,330 m). Mount MacDonald "
         "and the 14.6 km MacDonald Tunnel (1988) replace the 1916 Connaught "
         "Tunnel; Stoney Creek and its long trestle; Glacier area.",
    "D": "Descent to the Columbia Valley \u2014 Beavermouth, Albert Canyon bore, "
         "and the gorge above Donald.",
    "E": "Columbia Valley floor at Golden \u2014 the widest open scene; the "
         "Purcell/Kootenay foothills beyond the river.",
    "F": "Kicking Horse Pass \u2014 Cathedral Mountain, Mount Stephen, Yoho "
         "Valley. The railway and the Trans-Canada Highway fight over the same "
         "canyon wall (old 4.5% Big Hill vs the modern spiral tunnels).",
}


def load_rail_mask():
    rows = [r for r in csv.DictReader(open(os.path.join(WORK, "profile.csv")))
            if 605.7 <= float(r["dist_km"]) <= 812.0]
    km = np.array([float(r["dist_km"]) for r in rows])
    tun = np.array([int(r["in_tunnel"]) if r["in_tunnel"] else 0 for r in rows])
    return km, tun


def in_tunnel_at(km, rail_km, rail_tun):
    i = int(np.searchsorted(rail_km, km))
    i = min(max(i, 0), len(rail_km) - 1)
    return rail_tun[i]


def classify(km, cls, name, tun, bridges):
    near = any(abs(b[0] - km) < 0.3 or (b[0] <= km <= b[1])
               for b in bridges)
    if tun:
        return "road passes over tunnel (grade-separated)"
    if cls in ("trunk", "primary", "trunk_link", "primary_link"):
        return "grade-separated (road bridge/tunnel over track)"
    if cls in ("secondary", "tertiary"):
        return "at-grade street (town)"
    if near:
        return "at-grade, near rail bridge (verify)"
    return "minor at-grade crossing"


def compression_table():
    f = json.load(open(os.path.join(WORK, "features.json")))
    rows = []
    # yards
    yards = [y for y in f["yards"] if y["km0"] <= 812.0 and y["km1"] >= 605.7]
    for y in yards:
        model = 6 * MODULE_M
        rows.append((f"yard km {y['km0']:.1f}-{y['km1']:.1f} ({y['max_tracks']} trk)",
                     f"{y['len_km']*1000:.0f} m", f"{model:.1f} m (6 mods)",
                     f"{y['len_km']*1000/model:.0f}x"))
    # sidings (representative)
    seen = set()
    for s in f["sidings"]:
        if 605.7 <= s["km"] <= 812.0:
            model = 4 * MODULE_M
            key = (s["name"], round(s["km"], 1))
            tag = "" if key not in seen else f" (trk {s['way']})"
            seen.add(key)
            rows.append((f"siding {s['name']} km {s['km']:.1f}{tag}",
                         f"{s['len_km']*1000:.0f} m", f"{model:.1f} m (4 mods)",
                         f"{s['len_km']*1000/model:.0f}x"))
    # tunnels
    for t in f["tunnels"]:
        if t["km0"] <= 812.0 and t["km1"] >= 605.7:
            model = 1 * MODULE_M
            rows.append((f"tunnel km {t['km0']:.1f} ({t['len_km']*1000:.0f} m)",
                         f"{t['len_km']*1000:.0f} m", f"{model:.1f} m (1 mod)",
                         f"{t['len_km']*1000/model:.0f}x"))
    return rows


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    crossings = json.load(open(os.path.join(WORK, "road_crossings.json")))
    corridors = json.load(open(os.path.join(WORK, "road_corridors.json")))
    rail_km, rail_tun = load_rail_mask()
    bridges = [(b["km0"], b["km1"]) for b in f["bridges"]
               if b["km0"] <= 812.0 and b["km1"] >= 605.7]

    L = []
    L.append("# CP Mountain Section \u2014 Design Discussion")
    L.append("")
    L.append("How the Revelstoke \u2192 Field mountain section goes from the "
             "full 1:1000 prototype to a buildable, storable modular layout. "
             "Companion docs: `cpr_module_plan-comp.md` (the compressed plan), "
             "`cpr_modular_standard-comp.md` (end plates & electrical), the "
             "`-proto` 1:1000 reference set, and the `render/` diagrams.")
    L.append("")

    # ---- 1. the 1000 m of modules
    L.append("## 1. The 1:1000 idea \u2014 1,000 m of modules")
    L.append("")
    L.append("The straightforward way to model 1,029 km of CP mainline is a "
             "**1:1000 run compression**: one prototype km becomes one model "
             "metre. That gives **\u2248 1,030 m (0.64 mi) of bench** for "
             "Vancouver\u2013Calgary \u2014 roughly **845 four-foot modules** \u2014 "
             "and even just the mountain section (km 606-812, 206 km) is "
             "**206 m / 169 modules**. Every real yard and siding comes out at "
             "its true relative length:")
    L.append("")
    L.append("- Field yard (2.1 km) = 2.1 m / 2 modules")
    L.append("- Golden yard (2.2 km) = 2.2 m / 2 modules")
    L.append("- A 9,000-ft siding = 2.7 m / 2 modules")
    L.append("- 18 km of single track (Scene A) = 18 m / 15 modules")
    L.append("")
    L.append("That is a faithful scale model and an impractical build. The "
             "`-proto` docs keep it as the **reference truth**; the compressed "
             "plan is what we build.")
    L.append("")

    # ---- 2. yards
    L.append("## 2. Yards: multi-kilometre fans \u2192 12-ft train pockets")
    L.append("")
    L.append("Our equipment standard is a **12 ft train** \u2014 two 5-well "
             "well-car units, two AC4400s and a caboose \u2014 about 1,200 "
             "prototype feet at HO. A yard only needs to hold that train, so "
             "every yard is re-designed around a **12 ft usable track** instead "
             "of its prototype length:")
    L.append("")
    L.append("| bay | purpose |")
    L.append("|---|---|")
    L.append("| 1 | west lead / headshunt (runaround) |")
    L.append("| 2 | #6 ladder |")
    L.append("| 3-5 | yard body \u2014 **12 ft usable** |")
    L.append("| 6 | east tail |")
    L.append("")
    L.append("A 2.1 km prototype yard therefore becomes **6 modules (7.3 m)**. "
             "Some prototype yards are actually *shorter* than our train and "
             "are lengthened to fit it. The compression factor varies yard to "
             "yard:")
    L.append("")
    L.append("| feature | prototype | model | factor |")
    L.append("|---|---|---|---|")
    for name, proto, model, fac in compression_table():
        if name.startswith("yard"):
            L.append(f"| {name} | {proto} | {model} | {fac} |")
    L.append("")

    # ---- 3. sidings and runs
    L.append("## 3. Sidings & single-track runs: variable compression")
    L.append("")
    L.append("Not everything compresses the same. **Different element types get "
             "different compression factors**, chosen so each keeps the scenery "
             "that matters:")
    L.append("")
    L.append("| element | prototype | model | factor |")
    L.append("|---|---|---|---|")
    for name, proto, model, fac in compression_table():
        if name.startswith(("siding", "tunnel")):
            L.append(f"| {name} | {proto} | {model} | {fac} |")
    L.append("| plain single-track run (Scene B) | 33 km | 1-3 scenic modules | "
             "\u2248 9,000-27,000\u00d7 |")
    L.append("| plain single-track run (Scene F) | 51 km | 1-3 scenic modules | "
             "\u2248 14,000-42,000\u00d7 |")
    L.append("")
    L.append("- **Sidings:** every prototype siding (5,000-11,000 ft) becomes a "
             "**12 ft usable siding** on 4 modules \u2014 a 300-700\u00d7 "
             "compression. All sidings interchange with the same 12 ft train.")
    L.append("- **Runs:** a run is scenery, not railroad. 18 km of single track "
             "drops to **1-2 omittable modules**; the end plates let you skip "
             "them entirely (Section 6).")
    L.append("- **Tunnels:** one portal/scenic module each \u2014 MacDonald "
             "14.6 km compresses \u2248 12,000\u00d7; the 585 m Eagle Pass and "
             "619 m Albert Canyon bores \u2248 500\u00d7.")
    L.append("")
    L.append("Net result: **169 modules \u2192 35 core modules (140 ft)**, plus "
             "optional sidings and satellite yards.")
    L.append("")

    # ---- 4. rivers
    L.append("## 4. Water \u2014 rivers, lakes, bridges")
    L.append("")
    L.append("River crossings are the strongest scenic anchors. Every one is a "
             "**bridge module** in the scene:")
    L.append("")
    L.append("| scene | km | water body | rail bridge |")
    L.append("|---|---|---|---|")
    for code, _, a, b, _ in SCENES:
        for km, name in sorted(RIVERS.items()):
            if a <= km <= b:
                br = [bb for bb in bridges if bb[0] <= km <= bb[1]]
                ln = f"{(br[0][1]-br[0][0])*1000:.0f} m" if br else "see scene"
                L.append(f"| {code} | {km:.1f} | {name} | {ln} |")
    L.append("")
    L.append("Note the **Columbia River trestle at Golden** (\u2248 km 748) is "
             "under-mapped in OSM; verify and add it as a hero bridge in "
             "Scene E. **Revelstoke Lake**: the Columbia north arm widens into "
             "a reservoir between the track and the Trans-Canada Highway \u2014 "
             "see Section 6.")
    L.append("")

    # ---- 5. mountains & tunnels
    L.append("## 5. Mountains \u2014 what the scenery is")
    L.append("")
    for code, name, a, b, _ in SCENES:
        L.append(f"**Scene {code} \u2014 {name}:** {MOUNTAINS[code]}")
    L.append("")
    L.append("| tunnel | km | length | module |")
    L.append("|---|---|---|---|")
    for t in f["tunnels"]:
        if t["km0"] <= 812.0 and t["km1"] >= 605.7:
            L.append(f"| km {t['km0']:.1f} | {t['km0']:.1f}-{t['km1']:.1f} | "
                     f"{t['len_km']*1000:.0f} m | 1 scenic portal module |")
    L.append("")

    # ---- 6. roads
    L.append("## 6. Roads \u2014 grade-separated, not at-grade")
    L.append("")
    L.append("Outside town there are almost **no at-grade road/rail crossings** "
             "on the major highways: the Trans-Canada Highway mostly rides "
             "bridges and tunnels over (or beside) the track. The OSM-derived "
             "crossing list confirms the pattern:")
    L.append("")
    L.append("| km | road | class | type |")
    L.append("|---|---|---|---|")
    for c in crossings:
        tun = in_tunnel_at(c["km"], rail_km, rail_tun)
        typ = classify(c["km"], c["cls"], c["name"], tun, bridges)
        L.append(f"| {c['km']:.1f} | {c['name'] or c['cls']} | {c['cls']} | "
                 f"{typ} |")
    L.append("")
    L.append("**Design rule:** in the model, treat road crossings as scenery \u2014 "
             "a road bridge arching over the track or a road tucking into a "
             "tunnel above the rail. Build at-grade crossings only in the town "
             "scenes (Revelstoke streets, Golden's 14th St / BC 95, Field "
             "access).")
    L.append("")
    L.append("### Revelstoke \u2014 the lake buffer")
    L.append("")
    L.append("At Revelstoke the **Columbia River / Revelstoke Lake sits between "
             "the highway and the railway**, so the road is *not* visible from "
             "the track at all. Scene A is built accordingly:")
    L.append("")
    L.append("- The west approach rides the **lake shoreline**; the 412 m "
             "Columbia crossing dominates the module's foreground.")
    L.append("- The Trans-Canada Highway appears only as a **far-shore ribbon** "
             "across the water (a painted/flat backdrop), never at track level.")
    L.append("- No road/rail interaction in Scene A \u2014 the water is the "
             "separation. This is a rare case where scenery *hides* the road.")
    L.append("")
    L.append("### Where the road and rail do run together")
    L.append("")
    L.append("The TCH and track share the same canyon wall in the Kicking Horse "
             "corridor and near the tunnel portals \u2014 those are the spots to "
             "show a road glimpsed through the trees. Measured corridors "
             "(< 25 m apart):")
    L.append("")
    L.append("| km | road | gap |")
    L.append("|---|---|---|")
    for r in corridors:
        if r["cls"] in ("trunk", "primary") and r["name"]:
            L.append(f"| {r['km0']:.1f}-{r['km1']:.1f} | {r['name']} "
                     f"({r['ref']}) | {r['dist_m']:.0f} m |")
    L.append("")
    L.append("Scene F (762-767, 783, 799, 807) and the MacDonald tunnel zone "
             "(673-684) carry most of these road-visible moments.")
    L.append("")

    # ---- 7. storage
    L.append("## 7. Storage \u2014 a mountain that packs flat")
    L.append("")
    L.append("Free-mo modules are flat plates, easy to stack. Our modules carry "
             "mountains, so we design the mountain cross-section to **nest "
             "when inverted**.")
    L.append("")
    L.append("Each 4-ft module is a **2-ft-wide box whose back rises at 45\u00b0 "
             "to up to 2 ft** \u2014 a wedge, not a cliff:")
    L.append("")
    L.append("```")
    L.append("  track side          back (sky) side")
    L.append("       |                       /")
    L.append("       |   permanent trees    / 45 deg")
    L.append("       |   & groundform      /")
    L.append("  base  +--------------------/   2 ft tall")
    L.append("        <--------- 2 ft --------->")
    L.append("```")
    L.append("")
    L.append("Store two modules as a pair: one normal, one **rolled upside down "
             "and set on the other**. The two 45\u00b0 slopes nest into each "
             "other, the flat bases meet, and the pair packs as a "
             "**\u2248 2 ft \u00d7 2 ft \u00d7 4 ft box** \u2014 scenery on the "
             "inside, protected, no separate lids or crates:")
    L.append("")
    L.append("```")
    L.append("  box: [ module B upside down ]")
    L.append("       [ module A normal       ]  2 x 2 x 4 ft")
    L.append("```")
    L.append("")
    L.append("- Yard modules and tunnel modules use the same 2-ft base and 45\u00b0 "
             "back slope so any two modules pair up for storage.")
    L.append("- Keep the slope at a true 45\u00b0 so the inverted wedge seats "
             "squarely; add thin foam pads on the inside faces.")
    L.append("- Low-relief structures (stations, houses) sit in the flat "
             "foreground band and are removable if delicate.")
    L.append("- Scenery height above the base is capped at 2 ft; keep the track "
             "side flat at the 50-in rail height (see "
             "`cpr_modular_standard-comp.md`).")
    L.append("")

    L.append("## 8. Bottom line")
    L.append("")
    L.append("- **Build:** 35 core modules (140 ft), optionally 51 (204 ft).")
    L.append("- **Compression:** yards to 12-ft pockets (55-300\u00d7), sidings "
             "to 12 ft (300-700\u00d7), runs to 1-2 modules, tunnels to one "
             "portal module.")
    L.append("- **Grade:** max 2.5% model grade, only where the prototype "
             "climbs \u2014 never the full 1,000 m Vancouver\u2013Calgary rise.")
    L.append("- **Scenery anchors:** 15 river bridges, 5 tunnel portals, the "
             "Revelstoke lake buffer, and road-visible canyon walls at "
             "Kicking Horse and the tunnel zone.")
    L.append("- **Storage:** 2 ft wide, 45\u00b0 back slope, modules nest in "
             "2\u00d72\u00d74 ft pairs.")
    L.append("")

    with open(os.path.join(OUT, "cpr_design_discussion.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_design_discussion.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
