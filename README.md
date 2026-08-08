# cpr_gis — CP (CPKC) Mainline Vancouver → Calgary: Direction / Length / Grade / Curvature

Geospatial analysis of the Canadian Pacific (now CPKC) mainline between Vancouver, BC and Calgary, AB.

## Data sources
- **Route geometry**: OpenStreetMap `railway=rail` ways, `operator~Canadian Pacific` (queried via Overpass API, 2026-08-08). Mainline chain: Cascade → Yale → Ashcroft → Thompson → Shuswap → Mountain → Laggan subdivisions.
- **Elevation**: Natural Resources Canada **MRDEM-30** (CanElevation Series, successor to CDEM), 30 m, EPSG:3979, CGVD2013. DTM (`mrdem-30-dtm.tif`) sampled at each track vertex from the national COG on the NRCan data cube:
  `https://canelevation-dem.s3.ca-central-1.amazonaws.com/mrdem-30/mrdem-30-dtm.tif`

## Methodology
1. Query CP rail ways → build node graph → shortest path Vancouver→Calgary (Connaught Tunnel old line excluded; modern Rogers Pass **MacDonald Tunnel** main selected).
2. Verify path passes through North Bend, Kamloops, Revelstoke, Rogers Pass, Golden, Field (Kicking Horse), Lake Louise, Banff (all < 1.5 km).
3. Bilinear-sample MRDEM-30 DTM at all 13,418 track vertices.
4. Compute per-segment bearing (direction), grade, curvature; roll up per-subdivision summary.

## Directory layout
- `data/` — raw downloads (OSM Overpass JSON)
- `working/` — intermediate files (path nodes, elevation array)
- `output/` — final deliverables (profile CSV, GeoJSON, GPX, report)
- `scripts/` — analysis scripts

## Status
- [x] Track geometry acquired & mainline path built
- [x] Elevation sampled at all vertices (min 0.4 m, max 2490 m; Vancouver 6 m, Calgary 1021 m)
- [ ] Segment metrics (bearing/grade/curvature)
- [ ] Subdivision summary table + deliverables
