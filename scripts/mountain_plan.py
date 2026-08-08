#!/usr/bin/env python3
"""
Mountain section (Revelstoke -> Field) module plan for the CP Vancouver->Calgary
model railroad.

Scales (sliding, per user design):
  - Equipment: HO 1:87 (train ~12 ft = ~1,000-1,200 proto ft; real sidings dwarf it)
  - Single-track runs: compressed ~1:1000 (1 proto km -> 1 model m)
  - Sidings: compressed to a 12 ft usable standard (4 x 4 ft modules)
  - Yards: modelled only long enough for the 12 ft train to fit
  - Tunnels: compressed (MacDonald 14.6 km -> short scenic section)

Reads working/features.json. Produces output/cpr_mountain_modules.md
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

FT_PER_KM = 3280.84

SCENES = [
    ("A", "Revelstoke yard", 605.7, 623.2,
     "West approach yard (9 trk) + Revelstoke yard (6 trk) + town; main stays 1-track "
     "with yard leads. Prototype shop tracks not in OSM (under-mapped)."),
    ("B", "Eagle Pass (Monashee)", 623.2, 655.8,
     "Single-track CTC climbing the Illecillewaet valley; the long curve cluster through "
     "the pass, sharpest 16.2 deg/100ft near km 654. 585 m bore tunnel at km 655.8."),
    ("C", "Rogers Pass summit", 655.8, 704.3,
     "Rogers summit wye (8 trk, km 658); MacDonald tunnel (14.6 km) replaced Connaught; "
     "west-to-east downhill sidings Glacier 6,548 / Stoney Creek 9,040 / Wakely 9,575 / "
     "Griffith 5,064 / Rogers 2,358; Glacier yard cluster (10 trk, km 696-703)."),
    ("D", "Beavermouth / Albert Canyon", 704.3, 727.2,
     "Beavermouth sidings 7,275 + 3,299 (km 710/712); Albert Canyon bore (619 m, km 715.9); "
     "5-track span km 716.7-719.7."),
    ("E", "Golden", 727.2, 761.0,
     "Long tangent 7.6 km into Golden; Golden yard cluster (9-10 trk, km 739-755) + Hill "
     "siding 8,659 (km 754.3); short bore 759.5. Columbia River crossing."),
    ("F", "Yoho Valley to Field", 761.0, 812.0,
     "Glenogle 9,486 / Palliser 9,496 / Leanchoil 7,180 / Ottertail 8,754 sidings; long "
     "tangent 10.0 km (km 781-791); Field yard (7 trk, km 807.3-810.6) at Kicking Horse "
     "Portal. Spiral tunnels 1-2 start km 817.6 east of Field (optional add-on)."),
]


def ho_radius_ft(deg_per100ft):
    # R_ft = 5730 / deg; model = R_ft / 87. Design value from avg (max is noisy).
    if not deg_per100ft:
        return None
    return 5730.0 / deg_per100ft / 87.0


def main():
    f = json.load(open(os.path.join(WORK, "features.json")))
    runs = f["runs"]
    sidings = f["sidings"]
    tunnels = f["tunnels"]
    yards = f["yards"]
    multitrack = f["multitrack"]

    L = []
    L.append("# CP Mountain Section \u2014 Revelstoke \u2192 Rogers Pass \u2192 Golden \u2192 Field")
    L.append("")
    L.append("Prototype ~206 km (km 606-812). Model length at 1:1000 run-compression "
             "~206 m (676 ft).")
    L.append("")
    L.append("## Design basis (sliding scale)")
    L.append("")
    L.append("- **Equipment:** HO 1:87. 12 ft train = ~1,000-1,200 proto ft (10 well-cars "
             "+ 2 AC4400 + caboose). Fits any real CP siding (5,000-11,000 ft).")
    L.append("- **Runs:** 1 proto km = 1 model m (1:1000 compression on single track).")
    L.append("- **Sidings:** compressed to **12 ft usable** (4 x 4-ft modules) + ~1 ft "
             "turnouts each end + short single-track tails \u2248 **16 ft / 4 modules** per siding.")
    L.append("- **Yards:** modelled long enough for the 12 ft train (shortest yard track "
             "\u2265 12 ft); full prototype track count not required.")
    L.append("- **Tunnels:** compressed; MacDonald 14.6 km becomes a short scenic "
             "portal/mountain module.")
    L.append("- **Curves:** all prototype curves are gentle in HO (true-scale radius "
             "\u2265 24 in); you may run tighter for space.")
    L.append("")

    L.append("## Section total at 1:1000")
    L.append("")
    L.append("| scene | feature | proto km | model m | 4-ft modules (full build) |")
    L.append("|---|---|---|---|---|")
    tot_m = 0
    for code, name, a, b, _ in SCENES:
        m = b - a
        tot_m += m
        L.append(f"| {code} | {name} | {a:.1f}-{b:.1f} | {m:.0f} | {int(m/1.2192)} |")
    L.append(f"|  | **total** | **606-812** | **{tot_m:.0f}** | **{int(tot_m/1.2192)}** |")
    L.append("")

    for code, name, a, b, desc in SCENES:
        L.append(f"## Scene {code} \u2014 {name}  (km {a:.1f}-{b:.1f}, {b-a:.0f} m at 1:1000)")
        L.append("")
        L.append(desc)
        L.append("")
        L.append("### Track")
        L.append("")
        # multi-track in scene
        mts = [m for m in multitrack if m["km0"] <= b and m["km1"] >= a]
        if mts:
            L.append("Multi-track spans: " + "; ".join(
                f"km {m['km0']:.1f}-{m['km1']:.1f} ({m['max_tracks']} trk)" for m in mts))
            L.append("")
        # sidings in scene
        ss = [s for s in sidings if a <= s["km"] <= b]
        if ss:
            L.append("Sidings: " + "; ".join(
                f"{s['name']} km {s['km']:.1f} ({s['len_km']*FT_PER_KM:.0f} proto ft)" for s in ss))
            L.append("")
        # tunnels
        ts = [t for t in tunnels if t["km0"] <= b and t["km1"] >= a]
        if ts:
            L.append("Tunnels: " + "; ".join(
                f"km {t['km0']:.1f}-{t['km1']:.1f} ({t['len_km']*1000:.0f} proto m)" for t in ts))
            L.append("")
        # yard clusters
        ys = [y for y in yards if y["km0"] <= b and y["km1"] >= a]
        if ys:
            L.append("Yard clusters: " + "; ".join(
                f"km {y['km0']:.1f}-{y['km1']:.1f} ({y['max_tracks']} trk)" for y in ys))
            L.append("")
        L.append("| km | track | model | detail |")
        L.append("|---|---|---|---|")
        for r in runs:
            if r["km1"] < a or r["km0"] > b or r["len_km"] < 0.15:
                continue
            m0, m1 = r["km0"] - a, r["km1"] - a
            mm = m1 - m0
            if r["kind"] == "CURVE":
                rft = ho_radius_ft(abs(r["avg_deg_per100ft"]))
                detail = (f"{r['dir']} {r['avg_deg_per100ft']:+.2f} avg / "
                          f"{r['max_deg_per100ft']:.2f} max deg/100ft "
                          f"(R\u2248{rft:.0f} ft HO @ avg)")
            else:
                detail = ""
            L.append(f"| {r['km0']:.1f}-{r['km1']:.1f} | {r['kind'][0]} | "
                     f"{mm:.1f} m | {detail} |")
        L.append("")

    with open(os.path.join(OUT, "cpr_mountain_modules.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_mountain_modules.md ({len(L)} lines)")


if __name__ == "__main__":
    main()
