# CPKC Mainline Vancouver → Calgary — Route Summary
Computed from OpenStreetMap rail geometry + Natural Resources Canada MRDEM-30 DTM (30 m). Produced 2026-08-08 by the `cpr_gis` pipeline.

## 1. Sources
| Item | Source |
|---|---|
| Track geometry | OpenStreetMap `railway=rail`, `operator~Canadian Pacific|CP` (Overpass API, 2026-08-08) |
| Elevation | NRCan MRDEM-30 (CanElevation Series), DTM, 30 m, EPSG:3979, CGVD2013 — `mrdem-30-dtm.tif` national COG |
| Method | Node-graph shortest path, waypoint-verified; bilinear DEM sampling at every track vertex |

## 2. Overall stats
| Metric | Value |
|---|---|
| Route length | **1,029.3 km** |
| Track vertices | 13,172 (avg spacing 78 m) |
| Start (Vancouver) | 6 m |
| End (Calgary station) | 1048 m |
| Net rise | +1042 m |
| Total climbing | 11,804 m |
| Total descending | -10,763 m |
| Min elevation | 0 m |
| Max elevation (terrain) | 1624 m at km 834 (Kicking Horse Pass divide) |
| Tunnel track (approx.) | 21.2 km (incl. 14.7 km Rogers Pass/MacDonald, Kicking Horse spirals, canyon tunnels) |
| Steepest 1-km upgrade | +6.01% at km 186 (Fraser Canyon) |
| Steepest 1-km downgrade | -5.93% at km 187 (Fraser Canyon) |
| Sharpest curve (min radius) | 124 m (Fraser Canyon); tightest elsewhere ~107–160 m |

## 3. Route direction by leg (west → east)
| Leg | km range | Net bearing | Compass |
|---|---|---|---|
| Vancouver → Fraser Canyon (Fraser Valley) | 0–143 | 93°→66° | E then NE |
| Fraser Canyon (Hope → Ashcroft) | 143–209 | ~352° | N |
| Thompson River (Ashcroft → Kamloops) | 209–403 | ~0°–88° | N → E |
| Shuswap (Kamloops → Revelstoke) | 404–609 | ~68° | E |
| Mountain (Revelstoke → Rogers Pass → Golden) | 609–754 | ~55°–125° | NE → SE |
| Laggan (Golden → Kicking Horse → Lake Louise → Banff → Calgary) | 754–1029 | ~102° | E |

## 4. Subdivision breakdown
| Subdivision | km range | Length (km) | Dir | Elev start→end (m) | Avg grade % | Max up % | Max dn % | Max curv deg/km | Min radius (m) |
|---|---|---|---|---|---|---|---|---|---|---|
| Cascade Subdivision | 0.0–209.21 | 209.21 | NE | 6.0→141.0 | 0.1 | 6.01 | -5.93 | 461.13 | 124.0 |
| Thompson Subdivision | 209.25–222.54 | 13.29 | NW | 142.0→155.0 | 0.01 | 2.85 | -2.93 | 381.01 | 150.0 |
| Siding Keefers | 222.62–225.24 | 2.61 | N | 163.0→174.0 | 0.27 | 2.15 | -2.3 | 62.87 | 911.0 |
| Thompson Subdivision | 225.28–247.94 | 22.66 | N | 170.0→226.0 | 0.26 | 4.37 | -3.38 | 413.05 | 139.0 |
| Siding Lytton | 248.0–250.5 | 2.5 | N | 225.0→224.0 | -0.03 | 1.31 | -1.64 | 215.67 | 266.0 |
| Thompson Subdivision | 250.53–308.15 | 57.62 | NE | 221.0→278.0 | 0.01 | 4.08 | -3.27 | 416.73 | 137.0 |
| CPKC Thompson Subdivision | 308.21–317.84 | 9.63 | N | 280.0→301.0 | 0.37 | 4.44 | -1.43 | 375.88 | 152.0 |
| Thompson Subdivision | 317.89–403.16 | 85.28 | E | 312.0→355.0 | 0.03 | 4.57 | -4.03 | 534.55 | 107.0 |
| Shuswap Subdivision | 403.66–466.88 | 63.22 | E | 352.0→383.0 | -0.04 | 2.46 | -4.15 | 415.44 | 138.0 |
| Chum Creek Siding | 466.96–469.43 | 2.47 | NE | 378.0→411.0 | 0.94 | 2.2 | -1.0 | 72.78 | 787.0 |
| Shuswap Subdivision | 469.44–506.73 | 37.29 | SE | 409.0→353.0 | 0.07 | 2.39 | -2.12 | 314.9 | 182.0 |
| Salmon Arm Siding | 506.8–510.57 | 3.77 | NE | 354.0→350.0 | -0.18 | 0.95 | -1.42 | 97.53 | 587.0 |
| Shuswap Subdivision | 510.59–608.62 | 98.04 | E | 349.0→457.0 | 0.05 | 3.64 | -2.75 | 372.12 | 154.0 |
| Mountain Subdivision | 608.73–658.42 | 49.69 | NE | 459.0→924.0 | 1.01 | 4.69 | -2.25 | 530.01 | 108.0 |
| Mountain Subdivision | 658.59–667.01 | 8.43 | NE | 930.0→1051.0 | 1.39 | 2.89 | -1.8 | 296.62 | 193.0 |
| Mountain Subdivision MacDonald Track | 667.1–700.27 | 33.18 | N | 1056.0→795.0 | -0.88 | 1.32 | -2.92 | 35.74 | 1603.0 |
| Mountain Subdivision | 700.35–708.87 | 8.52 | NE | 794.0→774.0 | -0.06 | 2.54 | -3.68 | 50.07 | 1144.0 |
| Beavermouth Siding | 708.96–712.17 | 3.21 | E | 786.0→790.0 | 0.26 | 2.75 | -1.77 | 28.39 | 2018.0 |
| Mountain Subdivision | 712.18–763.41 | 51.23 | SE | 790.0→901.0 | 0.33 | 3.48 | -2.92 | 133.71 | 429.0 |
| Glenogle Siding | 763.43–766.3 | 2.88 | SE | 901.0→929.0 | 0.92 | 2.52 | -0.62 | 23.75 | 2412.0 |
| Mountain Subdivision | 766.32–775.43 | 9.11 | E | 928.0→1010.0 | 0.9 | 3.02 | -1.73 | 356.88 | 161.0 |
| Mountain Subdivision | 775.52–810.28 | 34.76 | NE | 1013.0→1247.0 | 0.81 | 3.41 | -2.41 | 56.51 | 1014.0 |
| Laggan Subdivision | 810.55–1029.33 | 218.77 | E | 1254.0→1048.0 | 0.17 | 5.07 | -2.5 | 357.98 | 160.0 |

## 5. Grade and curvature highlights
- **Fraser Canyon (km 143–209):** line climbs ~140 m over 66 km; steepest terrain sections ~6.0% (DEM-sampled; rail ruling grade in the canyon ≈ 1.4–2.2%). Numerous short tunnels; sharpest curves on the whole route (min radius ≈ 124 m).
- **Thompson Sub (km 209–403):** long gentle grades (~0.0–0.3% average), net rise only ~215 m.
- **Shuswap Sub (km 404–609):** low grades along lakes; the climb toward Revelstoke begins at km ~608.
- **Mountain Sub (km 609–754):** sustained ascent to Rogers Pass. DEM-sampled grades reach ~4.7% on approach; actual rail ruling grade was 2.2% (old Connaught line) and ~1% through the 14.7 km **MacDonald Tunnel** (2007). MacDonald Track computed grade ≈ −0.9% (descending eastbound portal-to-portal), min radius ~1600 m.
- **Laggan / Kicking Horse Pass (km 754–842):** climb to the Continental Divide (terrain max 1,624 m at km 834). East slope (Banff side) grades ≈ +2.2% actual; the two **spiral tunnels** (1909) cut the old 4.5% Big Hill to 2.2%. DEM-sampled max ≈ 5.1%.
- **Banff → Calgary (km 898–1029):** steady descent from ~1,400 m to ~1,050 m, average ≈ −0.5%.

## 6. Limitations / caveats
- **Grades are DEM-derived**, not survey railbed data. The MRDEM-30 DTM is sampled at the track vertices, so in canyons and on mountain slopes it reflects **terrain**, which is generally steeper than the actual railbed. Treat all grade figures as approximations; ruling-grade values ~2.2% (Kicking Horse/Rogers) and ~1% (MacDonald Tunnel) are the authoritative rail figures.
- **Tunnels:** interior vertices were re-elevated by portal-to-portal linear interpolation, so tunnel grades are estimates of a uniform bore grade, not measurements.
- **Curvature** is computed from OSM vertex bearings; very short (<40 m) edges were discarded to remove noise.
- Length and geometry derive from OpenStreetMap (community-mapped, approximate); the 1,029 km total matches the published CP figure (~1,025 km) within expected mapping variance.

## 7. Deliverable files
- `output/cpr_segments.csv` — per-subdivision summary table
- `working/profile.csv` — per-vertex profile (13,172 rows: km, lat, lon, elev, grades, bearing, curvature, subdivision, tunnel)
- `output/cpr_mainline.geojson` — point features with elev/grade/subdivision attributes (open in QGIS/ArcGIS)
- `output/cpr_mainline.gpx` — track for GPS/app display
- `output/cpr_profile.png` — elevation / grade / curvature profile chart
