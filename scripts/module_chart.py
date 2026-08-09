#!/usr/bin/env python3
"""
Build a model-railroad module track chart from working/features.json.

Converts prototype km to model units at a chosen scale (default 1:1000,
i.e. 1 model m = 1000 prototype m, 1 model ft = 1000 prototype ft).

Produces output/cpr_module_chart-proto.md
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

FT_PER_KM = 3280.84


def model_m(km, scale):
    return km * 1000.0 / scale


def merge_multitrack(spans, gap_km=2.0):
    if not spans:
        return []
    out = [dict(spans[0])]
    for s in spans[1:]:
        if s["km0"] - out[-1]["km1"] <= gap_km:
            out[-1]["km1"] = s["km1"]
            out[-1]["max_tracks"] = max(out[-1]["max_tracks"], s["max_tracks"])
            out[-1]["len_km"] = out[-1]["km1"] - out[-1]["km0"]
        else:
            out.append(dict(s))
    return out


# interval -> label for merged parallel-track spans
MT_LABELS = [
    (0.0, 3.0, "Vancouver terminal (RM + yards)"),
    (7.0, 25.0, "Burnaby / New Westminster (Thornton Yard)"),
    (24.0, 40.0, "Coquitlam / Pitt Meadows"),
    (40.0, 125.0, "DOUBLE TRACK Vancouver\u2192Ruby Creek (real)"),
    (163.0, 200.0, "Fraser Canyon passing (single-track CTC)"),
    (203.0, 210.0, "North Bend / Boston Bar yard"),
    (214.0, 217.0, "Chaumox siding"),
    (222.0, 226.0, "Keefers siding"),
    (234.0, 241.0, "Kanaka siding"),
    (247.0, 251.0, "Lytton"),
    (257.0, 258.5, "siding (unmapped name)"),
    (266.0, 269.0, "siding (unmapped name)"),
    (387.0, 425.0, "Kamloops yard / Hundac"),
    (466.0, 498.0, "Chum Creek\u2013Sicamous sidings"),
    (506.0, 523.0, "Salmon Arm / Canoe sidings"),
    (525.0, 526.0, "siding (unmapped name)"),
    (533.0, 538.0, "siding (unmapped name)"),
    (593.0, 601.0, "siding (unmapped name)"),
    (604.0, 623.0, "Revelstoke yard area"),
    (655.0, 705.0, "Rogers / Glacier"),
    (708.0, 720.0, "Beavermouth / Albert Canyon"),
    (726.0, 761.0, "Golden yard area"),
    (763.0, 767.0, "Glenogle siding"),
    (768.0, 770.0, "siding (unmapped name)"),
    (772.0, 776.0, "Palliser siding"),
    (781.0, 785.0, "Leanchoil siding"),
    (793.0, 800.0, "Ottertail siding"),
    (807.0, 811.0, "Field yard"),
    (817.0, 823.5, "twin tunnels 1-2"),
    (828.0, 839.0, "Kicking Horse loop"),
    (857.0, 860.0, "siding (unmapped name)"),
    (897.0, 902.0, "Banff"),
    (937.0, 940.0, "siding (unmapped name)"),
    (974.0, 978.0, "siding (unmapped name)"),
    (1026.0, 1029.5, "Calgary / Alyth yard"),
]


def mt_label(km0, km1):
    hits = [lab for a, b, lab in MT_LABELS if a <= km1 and km0 <= b]
    if not hits:
        return ""
    if len(hits) == 1:
        return hits[0]
    if hits == ["Burnaby / New Westminster (Thornton Yard)",
                "Coquitlam / Pitt Meadows"]:
        return "Burnaby / Coquitlam / Pitt Meadows"
    if hits == ["Rogers / Glacier", "Beavermouth / Albert Canyon"]:
        return "Rogers / Glacier / Beavermouth"
    return " / ".join(dict.fromkeys(hits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1000.0,
                    help="model scale divisor (default 1000 = 1:1000)")
    ap.add_argument("--train-ft", type=float, default=12.0,
                    help="model train length in feet (default 12)")
    args = ap.parse_args()

    f = json.load(open(os.path.join(WORK, "features.json")))
    scale = args.scale
    train_m = args.train_ft / 3.28084

    L = []
    L.append(f"# CP Vancouver\u2192Calgary \u2014 Module Track Chart (scale 1:{scale:g})")
    L.append("")
    L.append(f"- Train: {args.train_ft:g} ft ({train_m:.2f} m) = 2x five-well cars + 2 AC4400 + caboose")
    L.append(f"- Scale rule: 1 model m = {scale:g} prototype m; 1 model ft = {scale:g} prototype ft")
    L.append(f"- Prototype 14,000 ft siding = {14000.0/scale:.1f} ft / {14000.0/scale*0.3048:.2f} m model")
    L.append(f"- Prototype 1.0 km = {model_m(1.0, scale):.2f} m model")
    L.append("")

    # ---- yards -------------------------------------------------------------
    L.append("## Yards (detected \u2265 5 tracks within 250 m)")
    L.append("")
    L.append("| km | model m | tracks | notes |")
    L.append("|---|---|---|---|")
    yard_names = {
        "24.7": "Burnaby / New Westminster (CP Thornton Yard)", "26.0": "Burnaby / Coquitlam",
        "30.2": "Coquitlam / Fraser Mills", "36.4": "Pitt Meadows", "44.0": "Pitt Meadows east",
        "56.9": "Hatzic / Deroche", "67.1": "Mission", "92.3": "Agassiz",
        "206.8": "North Bend / Boston Bar (crew-change)", "249.0": "Lytton",
        "395.7": "Kamloops yard (east)", "398.6": "Kamloops", "401.7": "Kamloops yard (west)",
        "405.0": "Kamloops west", "411.9": "Kamloops Jct / Hundac", "420.2": "Hundac / Peterson",
        "421.5": "Hundac",
        "606.3": "Revelstoke west approach", "613.8": "Revelstoke yard", "619.4": "Revelstoke east",
        "658.2": "Rogers summit", "696.3": "Glacier west portal area", "700.1": "Glacier",
        "702.5": "Glacier east",
        "737.9": "Golden west", "744.9": "Golden", "750.5": "Golden yard",
        "754.0": "Golden east", "775.3": "Leanchoil", "808.0": "Field yard",
        "834.5": "Kicking Horse summit", "897.3": "Banff", "1026.8": "Calgary west",
        "1027.8": "Calgary / Alyth yard",
    }
    for y in f["yards"]:
        note = yard_names.get(f"{y['km0']:.1f}", "")
        L.append(f"| {y['km0']:.1f}\u2013{y['km1']:.1f} | {model_m(y['len_km'], scale):.1f} | "
                 f"{y['max_tracks']} | {note} |")
    L.append("")

    # ---- multi-track spans -------------------------------------------------
    mt = merge_multitrack(f["multitrack"])
    L.append("## Parallel-track spans (merged; 2+ tracks)")
    L.append("")
    L.append("| km | model m | tracks | section |")
    L.append("|---|---|---|---|")
    for s in mt:
        L.append(f"| {s['km0']:.1f}\u2013{s['km1']:.1f} | {model_m(s['len_km'], scale):.1f} | "
                 f"{s['max_tracks']} | {mt_label(s['km0'], s['km1'])} |")
    L.append("")

    # ---- sidings -----------------------------------------------------------
    L.append("## Sidings (named)")
    L.append("")
    L.append(f"| km | name | proto ft | model ft | fits {args.train_ft:g} ft train? |")
    L.append("|---|---|---|---|---|")
    for s in f["sidings"]:
        pf = s["len_km"] * FT_PER_KM
        mf = pf / scale
        ok = "YES" if mf >= args.train_ft * 1.05 else "no"
        L.append(f"| {s['km']:.1f} | {s['name']} | {pf:.0f} | {mf:.1f} | {ok} |")
    L.append("")

    # ---- tunnels & long straights ------------------------------------------
    L.append("## Tunnels (>= 0.2 km)")
    L.append("")
    L.append("| km | proto m | model m |")
    L.append("|---|---|---|")
    for t in f["tunnels"]:
        L.append(f"| {t['km0']:.1f}\u2013{t['km1']:.1f} | {t['len_km']*1000:.0f} | "
                 f"{model_m(t['len_km'], scale):.1f} |")
    L.append("")

    straights = sorted((r for r in f["runs"] if r["kind"] == "STRAIGHT"),
                       key=lambda r: -r["len_km"])
    L.append("## Longest straights (tangent candidates)")
    L.append("")
    L.append("| km | proto km | model m |")
    L.append("|---|---|---|")
    for r in straights[:12]:
        L.append(f"| {r['km0']:.1f}\u2013{r['km1']:.1f} | {r['len_km']:.1f} | "
                 f"{model_m(r['len_km'], scale):.1f} |")
    L.append("")

    # ---- curve character ----------------------------------------------------
    L.append("## Curve / straight character by section")
    L.append("")
    cur = [r for r in f["runs"] if r["kind"] == "CURVE"]
    if cur:
        L.append(f"- Total runs: {len(f['runs'])}; curves {len(cur)}; straights "
                 f"{len(f['runs'])-len(cur)}")
        sharpest = max(cur, key=lambda r: r["max_deg_per100ft"])
        longest = max(cur, key=lambda r: r["len_km"])
        L.append(f"- Sharpest curve: {sharpest['max_deg_per100ft']} deg/100ft "
                 f"at km {sharpest['km0']:.1f}")
        L.append(f"- Longest curve: {longest['len_km']:.2f} km at km {longest['km0']:.1f}")
    L.append("")

    # ---- chronological stream (condensed) -----------------------------------
    L.append("## Track chart (chronological; runs >= 0.5 km shown)")
    L.append("")
    L.append("```")
    for r in f["runs"]:
        if r["len_km"] < 0.5:
            continue
        if r["kind"] == "CURVE":
            L.append(f"  km {r['km0']:7.1f}  curve {r['dir']} "
                     f"{r['avg_deg_per100ft']:+.2f} avg / {r['max_deg_per100ft']:.2f} max "
                     f"deg/100ft over {r['len_km']:5.2f} km ({model_m(r['len_km'], scale):5.1f} m)")
        else:
            L.append(f"  km {r['km0']:7.1f}  straight {r['len_km']:6.2f} km "
                     f"({model_m(r['len_km'], scale):6.1f} m)")
    L.append("```")
    L.append("")

    with open(os.path.join(OUT, "cpr_module_chart-proto.md"), "w") as fh:
        fh.write("\n".join(L))
    print(f"wrote {OUT}/cpr_module_chart-proto.md ({len(L)} lines, scale 1:{scale:g})")
    print(f"yards: {len(f['yards'])}  sidings: {len(f['sidings'])}  "
          f"multitrack(merged): {len(mt)}  tunnels: {len(f['tunnels'])}")


if __name__ == "__main__":
    main()
