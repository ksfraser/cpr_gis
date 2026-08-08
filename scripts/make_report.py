#!/usr/bin/env python3
"""Generate the markdown route report from computed metrics."""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

segs = list(csv.DictReader(open(os.path.join(OUT, "cpr_segments.csv"))))
prof = list(csv.DictReader(open(os.path.join(WORK, "profile.csv"))))

km = [float(r["dist_km"]) for r in prof]
elev = [float(r["elev_m"]) for r in prof]
g1 = [float(r["grade_1km_pct"] or 0) for r in prof]
length = km[-1]
total_up = sum(max(elev[i] - elev[i - 1], 0) for i in range(1, len(prof)))
total_dn = sum(min(elev[i] - elev[i - 1], 0) for i in range(1, len(prof)))
tunnel_len = sum(
    float(prof[i]["dist_km"]) - float(prof[i - 1]["dist_km"])
    for i in range(1, len(prof))
    if int(float(prof[i - 1]["in_tunnel"] or 0)) + int(float(prof[i]["in_tunnel"] or 0)) > 0
)
maxe = max(elev)
maxe_km = km[elev.index(maxe)]
min_g = min(g1)
max_g = max(g1)
min_g_km = km[g1.index(min_g)]
max_g_km = km[g1.index(max_g)]

towns = {"Vancouver": 0.0, "Hope": 143.8, "Kamloops": 402.6, "Revelstoke": 608.9,
         "Rogers Pass": 678.8, "Golden": 754.4, "Field": 810.2, "Lake Louise": 842.7,
         "Banff": 898.2, "Calgary": 1029.3}

L = []
A = L.append
A("# CPKC Mainline Vancouver → Calgary — Route Summary\n")
A("Computed from OpenStreetMap rail geometry + Natural Resources Canada MRDEM-30 DTM (30 m). "
  "Produced 2026-08-08 by the `cpr_gis` pipeline.\n")
A("\n## 1. Sources\n")
A("| Item | Source |\n|---|---|\n")
A("| Track geometry | OpenStreetMap `railway=rail`, `operator~Canadian Pacific|CP` (Overpass API, 2026-08-08) |\n")
A("| Elevation | NRCan MRDEM-30 (CanElevation Series), DTM, 30 m, EPSG:3979, CGVD2013 — `mrdem-30-dtm.tif` national COG |\n")
A("| Method | Node-graph shortest path, waypoint-verified; bilinear DEM sampling at every track vertex |\n")

A("\n## 2. Overall stats\n")
A("| Metric | Value |\n|---|---|\n")
A(f"| Route length | **{length:,.1f} km** |\n")
A(f"| Track vertices | {len(prof):,} (avg spacing {length*1000/(len(prof)-1):.0f} m) |\n")
A(f"| Start (Vancouver) | {elev[0]:.0f} m |\n")
A(f"| End (Calgary station) | {elev[-1]:.0f} m |\n")
A(f"| Net rise | {elev[-1]-elev[0]:+.0f} m |\n")
A(f"| Total climbing | {total_up:,.0f} m |\n")
A(f"| Total descending | {total_dn:,.0f} m |\n")
A(f"| Min elevation | {min(elev):.0f} m |\n")
A(f"| Max elevation (terrain) | {maxe:.0f} m at km {maxe_km:.0f} (Kicking Horse Pass divide) |\n")
A(f"| Tunnel track (approx.) | {tunnel_len:.1f} km (incl. 14.7 km Rogers Pass/MacDonald, Kicking Horse spirals, canyon tunnels) |\n")
A(f"| Steepest 1-km upgrade | {max_g:+.2f}% at km {max_g_km:.0f} (Fraser Canyon) |\n")
A(f"| Steepest 1-km downgrade | {min_g:+.2f}% at km {min_g_km:.0f} (Fraser Canyon) |\n")
A(f"| Sharpest curve (min radius) | 124 m (Fraser Canyon); tightest elsewhere ~107–160 m |\n")

A("\n## 3. Route direction by leg (west → east)\n")
A("| Leg | km range | Net bearing | Compass |\n|---|---|---|---|\n")
A("| Vancouver → Fraser Canyon (Fraser Valley) | 0–143 | 93°→66° | E then NE |\n")
A("| Fraser Canyon (Hope → Ashcroft) | 143–209 | ~352° | N |\n")
A("| Thompson River (Ashcroft → Kamloops) | 209–403 | ~0°–88° | N → E |\n")
A("| Shuswap (Kamloops → Revelstoke) | 404–609 | ~68° | E |\n")
A("| Mountain (Revelstoke → Rogers Pass → Golden) | 609–754 | ~55°–125° | NE → SE |\n")
A("| Laggan (Golden → Kicking Horse → Lake Louise → Banff → Calgary) | 754–1029 | ~102° | E |\n")

A("\n## 4. Subdivision breakdown\n")
A("| Subdivision | km range | Length (km) | Dir | Elev start→end (m) | Avg grade % | Max up % | Max dn % | Max curv deg/km | Min radius (m) |\n")
A("|---|---|---|---|---|---|---|---|---|---|---|\n")
for s in segs:
    A(f"| {s['subdivision']} | {s['start_km']}–{s['end_km']} | {s['length_km']} | {s['direction']} "
      f"| {s['elev_start_m']}→{s['elev_end_m']} | {s['avg_grade_pct']} | {s['max_up_pct']} | {s['max_dn_pct']} "
      f"| {s['max_curv_deg_km']} | {s['min_radius_m']} |\n")

A("\n## 5. Grade and curvature highlights\n")
A("- **Fraser Canyon (km 143–209):** line climbs ~140 m over 66 km; steepest terrain sections ~6.0% (DEM-sampled; "
  "rail ruling grade in the canyon ≈ 1.4–2.2%). Numerous short tunnels; sharpest curves on the whole route (min radius ≈ 124 m).\n")
A("- **Thompson Sub (km 209–403):** long gentle grades (~0.0–0.3% average), net rise only ~215 m.\n")
A("- **Shuswap Sub (km 404–609):** low grades along lakes; the climb toward Revelstoke begins at km ~608.\n")
A("- **Mountain Sub (km 609–754):** sustained ascent to Rogers Pass. DEM-sampled grades reach ~4.7% on approach; "
  "actual rail ruling grade was 2.2% (old Connaught line) and ~1% through the 14.7 km **MacDonald Tunnel** (2007). "
  "MacDonald Track computed grade ≈ −0.9% (descending eastbound portal-to-portal), min radius ~1600 m.\n")
A("- **Laggan / Kicking Horse Pass (km 754–842):** climb to the Continental Divide (terrain max 1,624 m at km 834). "
  "East slope (Banff side) grades ≈ +2.2% actual; the two **spiral tunnels** (1909) cut the old 4.5% Big Hill to 2.2%. "
  "DEM-sampled max ≈ 5.1%.\n")
A("- **Banff → Calgary (km 898–1029):** steady descent from ~1,400 m to ~1,050 m, average ≈ −0.5%.\n")

A("\n## 6. Limitations / caveats\n")
A("- **Grades are DEM-derived**, not survey railbed data. The MRDEM-30 DTM is sampled at the track vertices, so in "
  "canyons and on mountain slopes it reflects **terrain**, which is generally steeper than the actual railbed. Treat "
  "all grade figures as approximations; ruling-grade values ~2.2% (Kicking Horse/Rogers) and ~1% (MacDonald Tunnel) "
  "are the authoritative rail figures.\n")
A("- **Tunnels:** interior vertices were re-elevated by portal-to-portal linear interpolation, so tunnel grades are "
  "estimates of a uniform bore grade, not measurements.\n")
A("- **Curvature** is computed from OSM vertex bearings; very short (<40 m) edges were discarded to remove noise.\n")
A("- Length and geometry derive from OpenStreetMap (community-mapped, approximate); the 1,029 km total matches the "
  "published CP figure (~1,025 km) within expected mapping variance.\n")

A("\n## 7. Deliverable files\n")
A("- `output/cpr_segments.csv` — per-subdivision summary table\n")
A("- `working/profile.csv` — per-vertex profile (13,172 rows: km, lat, lon, elev, grades, bearing, curvature, subdivision, tunnel)\n")
A("- `output/cpr_mainline.geojson` — point features with elev/grade/subdivision attributes (open in QGIS/ArcGIS)\n")
A("- `output/cpr_mainline.gpx` — track for GPS/app display\n")
A("- `output/cpr_profile.png` — elevation / grade / curvature profile chart\n")

with open(os.path.join(OUT, "cpr_report.md"), "w") as f:
    f.write("".join(L))
print("wrote", os.path.join(OUT, "cpr_report.md"))
