#!/usr/bin/env python3
"""
Analyze CP (CPKC) mainline Vancouver -> Calgary.

Computes per-vertex and per-subdivision metrics:
  direction (bearing), length (km), grade (%), curvature (deg/km + radius).

Sources:
  - data/cp_ways.json   (OpenStreetMap CP rail ways, Overpass)
  - working/path_nodes.json  (shortest-path mainline, (lat,lon) per vertex)
  - working/elev.npy    (MRDEM-30 DTM bilinear samples per vertex)

Tunnel handling: vertices inside tunnel-tagged ways are replaced by linear
interpolation between portal vertices (DEM shows mountain surface, not railbed).
"""
import json
import math
import numpy as np
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

R = 6371000.0


def haversine(a, b):
    p1, l1 = math.radians(a[0]), math.radians(a[1])
    p2, l2 = math.radians(b[0]), math.radians(b[1])
    dp, dl = p2 - p1, l2 - l1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def initial_bearing(a, b):
    p1, l1 = math.radians(a[0]), math.radians(a[1])
    p2, l2 = math.radians(b[0]), math.radians(b[1])
    y = math.sin(l2 - l1) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(l2 - l1)
    return math.degrees(math.atan2(y, x)) % 360.0


def compass(bearing):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((bearing + 22.5) // 45) % 8]


def signed_angle_diff(b1, b2):
    d = (b2 - b1 + 180) % 360 - 180
    return d


def main():
    path = [tuple(p) for p in json.load(open(os.path.join(WORK, "path_nodes.json")))]
    elev = np.load(os.path.join(WORK, "elev.npy")).astype(float)
    n = len(path)
    assert len(elev) == n, (len(elev), n)

    # ---- rebuild edge -> ways mapping from raw OSM -------------------------
    import glob
    ways = []
    for fp in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        ways.extend(json.load(open(fp))["elements"])
    edge_ways = {}
    winfo = {}
    for w in ways:
        if "geometry" not in w:
            continue
        t = w.get("tags", {})
        nm = t.get("name", "")
        if "connaught" in nm.lower():
            continue
        g = w["geometry"]
        if len(g) < 2:
            continue
        winfo[w["id"]] = {
            "name": nm,
            "operator": t.get("operator", ""),
            "incline": t.get("incline", ""),
            "tunnel": t.get("tunnel", "") == "yes",
            "maxspeed": t.get("maxspeed", ""),
        }
        for a, b in zip(g, g[1:]):
            ka = (round(a["lat"], 7), round(a["lon"], 7))
            kb = (round(b["lat"], 7), round(b["lon"], 7))
            edge_ways.setdefault(frozenset((ka, kb)), set()).add(w["id"])

    # ---- per-edge distance, bearing, tunnel flag, subdivision --------------
    dists = np.array([haversine(path[i], path[i + 1]) for i in range(n - 1)])
    cum = np.concatenate([[0.0], np.cumsum(dists)]) / 1000.0  # km
    bear = np.array([initial_bearing(path[i], path[i + 1]) for i in range(n - 1)])

    subdiv = np.empty(n, dtype=object)
    tunnel_edge = np.zeros(n - 1, dtype=bool)
    incline_map = {}
    for i in range(n - 1):
        key = frozenset((path[i], path[i + 1]))
        wids = edge_ways.get(key, set())
        if not wids:
            continue
        names = [winfo[w]["name"] for w in wids]
        tunnels = [winfo[w]["tunnel"] for w in wids]
        tunnel_edge[i] = any(tunnels)
        # pick mainline subdivision name: longest / first non-empty
        cand = [x for x in names if "subdivision" in x.lower()]
        subdiv[i] = max(cand, key=len) if cand else next((x for x in names if x), "")
        for w in wids:
            if winfo[w]["incline"]:
                incline_map[i] = winfo[w]["incline"]
    # last vertex inherits from previous edge
    subdiv[n - 1] = subdiv[n - 2]
    # fill any unnamed connectors with the nearest named subdivision
    for i in range(n):
        if not subdiv[i]:
            subdiv[i] = subdiv[i - 1] if i > 0 else ""
    for i in range(n - 1, -1, -1):
        if not subdiv[i]:
            subdiv[i] = subdiv[i + 1] if i < n - 1 else ""

    # ---- tunnel interior -> portal-to-portal linear elevation --------------
    in_tunnel = np.zeros(n, dtype=bool)
    i = 0
    while i < n - 1:
        if not tunnel_edge[i]:
            i += 1
            continue
        s = i
        while i < n - 1 and tunnel_edge[i]:
            i += 1
        e = i  # first non-tunnel edge index
        # portals: vertex s (start) and vertex e (end)
        pe = e if e < n else n - 1
        z0 = elev[s]
        z1 = elev[pe]
        d0 = cum[s]
        d1 = cum[pe]
        for v in range(s + 1, min(e, n - 1) + 1):
            if d1 > d0:
                elev[v] = z0 + (z1 - z0) * (cum[v] - d0) / (d1 - d0)
            in_tunnel[v] = True
    # portal vertices are considered boundary, not interior
    for v in range(1, n - 1):
        in_tunnel[v] = in_tunnel[v] and not (
            (v > 0 and not tunnel_edge[v - 1]) or (v < n - 1 and not tunnel_edge[v])
        )

    # ---- grades ------------------------------------------------------------
    grade_raw = np.zeros(n - 1)
    grade_sm = np.zeros(n - 1)
    grade_1km = np.zeros(n - 1)
    W = 8  # ~600 m smoothing window
    padded = np.pad(elev, (W // 2, W - 1 - W // 2), mode="edge")
    sm = np.convolve(padded, np.ones(W) / W, "valid")
    for i in range(n - 1):
        grade_raw[i] = (elev[i + 1] - elev[i]) / dists[i] * 100.0
        grade_sm[i] = (sm[i + 1] - sm[i]) / dists[i] * 100.0
    # ruling grade: elevation change over ~1 km baseline
    for i in range(n - 1):
        j = i
        acc = 0.0
        while j < n - 2 and acc < 900.0:
            acc += dists[j]
            j += 1
        if j > i and acc > 300.0:
            grade_1km[i] = (elev[j] - elev[i]) / acc * 100.0
        else:
            grade_1km[i] = grade_sm[i]

    # ---- curvature ----------------------------------------------------------
    curv_deg_km = np.zeros(n - 1)
    radius = np.full(n - 1, np.nan)
    MIN_EDGE = 40.0  # ignore sub-noise edges (duplicate/offset vertices)
    for i in range(1, n - 1):
        if dists[i] < MIN_EDGE:
            continue
        diff = signed_angle_diff(bear[i - 1], bear[i])
        dkm = dists[i] / 1000.0
        if dkm > 0:
            curv_deg_km[i] = diff / dkm
        if abs(diff) > 0.01:
            radius[i] = dists[i] / math.radians(abs(diff))

    # ---- subdivision segmentation ------------------------------------------
    seg = []
    start = 0
    cur = subdiv[0]
    for v in range(1, n):
        if subdiv[v] != cur:
            seg.append((cur, start, v - 1))
            start = v
            cur = subdiv[v]
    seg.append((cur, start, n - 1))

    rows = []
    for name, s, e in seg:
        L = cum[e] - cum[s]
        if L < 0.1:
            continue
        zs, ze = elev[s], elev[e]
        net = ze - zs
        avg_g = np.nanmean(grade_1km[s:e]) if e > s else 0
        mx = float(np.nanmax(grade_1km[s:e])) if e > s else 0
        mn = float(np.nanmin(grade_1km[s:e])) if e > s else 0
        curv = curv_deg_km[s:e]
        curv = curv[np.isfinite(curv)]
        maxc = float(np.nanmax(np.abs(curv))) if len(curv) else 0
        rad = radius[s:e]
        rad = rad[np.isfinite(rad)]
        minr = float(np.min(rad)) if len(rad) else np.nan
        net_bearing = initial_bearing(path[s], path[e])
        rows.append(
            {
                "subdivision": name,
                "start_km": round(float(cum[s]), 2),
                "end_km": round(float(cum[e]), 2),
                "length_km": round(L, 2),
                "elev_start_m": round(float(zs), 0),
                "elev_end_m": round(float(ze), 0),
                "elev_change_m": round(net, 0),
                "min_elev_m": round(float(np.nanmin(elev[s:e + 1])), 0),
                "max_elev_m": round(float(np.nanmax(elev[s:e + 1])), 0),
                "avg_grade_pct": round(avg_g, 2),
                "max_up_pct": round(mx, 2),
                "max_dn_pct": round(mn, 2),
                "max_curv_deg_km": round(maxc, 2),
                "min_radius_m": round(minr, 0) if not math.isnan(minr) else "",
                "bearing_deg": round(net_bearing, 1),
                "direction": compass(net_bearing),
            }
        )

    # ---- outputs -------------------------------------------------------------
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(WORK, "profile.csv"), "w") as f:
        f.write("dist_km,lat,lon,elev_m,grade_raw_pct,grade_sm_pct,grade_1km_pct,bearing_deg,curv_deg_km,radius_m,subdivision,in_tunnel\n")
        for v in range(n - 1):
            f.write(
                f"{cum[v]:.4f},{path[v][0]:.7f},{path[v][1]:.7f},{elev[v]:.1f},"
                f"{grade_raw[v]:.3f},{grade_sm[v]:.3f},{grade_1km[v]:.3f},"
                f"{bear[v]:.1f},{curv_deg_km[v]:.3f},"
                f"{radius[v]:.0f},{subdiv[v]},{int(in_tunnel[v])}\n"
            )
        v = n - 1
        f.write(f"{cum[v]:.4f},{path[v][0]:.7f},{path[v][1]:.7f},{elev[v]:.1f},,,,{subdiv[v]},{int(in_tunnel[v])}\n")

    import csv
    with open(os.path.join(OUT, "cpr_segments.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # GeoJSON
    gj = {
        "type": "FeatureCollection",
        "name": "CPKC mainline Vancouver-Calgary",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "subdivision": subdiv[v],
                    "dist_km": round(float(cum[v]), 3),
                    "elev_m": round(float(elev[v]), 1),
                    "grade_1km_pct": round(float(grade_1km[v]), 3) if v < n - 1 else "",
                    "in_tunnel": bool(in_tunnel[v]),
                },
                "geometry": {"type": "Point", "coordinates": [path[v][1], path[v][0]]},
            }
            for v in range(n)
        ],
    }
    json.dump(gj, open(os.path.join(OUT, "cpr_mainline.geojson"), "w"))

    # GPX
    with open(os.path.join(OUT, "cpr_mainline.gpx"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="cpr_gis" xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write("<trk><name>CPKC mainline Vancouver-Calgary</name><trkseg>\n")
        for v in range(n):
            f.write(
                f'<trkpt lat="{path[v][0]:.7f}" lon="{path[v][1]:.7f}">'
                f"<ele>{elev[v]:.1f}</ele>"
                f"<desc>{subdiv[v]}</desc></trkpt>\n"
            )
        f.write("</trkseg></trk></gpx>\n")

    # print summary
    print(f"route length: {cum[-1]:.1f} km, vertices {n}")
    print(f"elev min {elev.min():.0f} m  max {elev.max():.0f} m  start {elev[0]:.0f}  end {elev[-1]:.0f}")
    print("tunnel vertices:", int(in_tunnel.sum()))
    tot_tun = cum[-1] - (cum[-1])
    # tunnel length
    tun_km = 0.0
    for i in range(n - 1):
        if in_tunnel[i] or in_tunnel[i + 1]:
            if tunnel_edge[i]:
                tun_km += dists[i] / 1000.0
    print(f"tunnel track length: {tun_km:.1f} km")
    print("\nsegments:")
    for r in rows:
        print(
            f"  {r['subdivision']:<28} {r['start_km']:7.1f}-{r['end_km']:7.1f} km  "
            f"len {r['length_km']:6.1f}  {r['direction']} {r['bearing_deg']:5.1f}  "
            f"elev {r['elev_start_m']:5.0f}->{r['elev_end_m']:5.0f}  "
            f"grade avg {r['avg_grade_pct']:5.2f}%  max+ {r['max_up_pct']:4.2f}  max- {r['max_dn_pct']:5.2f}  "
            f"maxcurv {r['max_curv_deg_km']:5.1f} deg/km  minR {r['min_radius_m']}"
        )
    print("\nincline tags found on path edges:", len(incline_map))
    for i, tag in list(incline_map.items())[:20]:
        print(f"   km {cum[i]:7.1f}  {tag:>8}  (edge {i})")


if __name__ == "__main__":
    main()
