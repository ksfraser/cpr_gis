#!/usr/bin/env python3
"""
Find road/rail crossings and road-visible corridors along the CP mountain
section (km 605.7-812.0) from OSM highway data.

Reads working/profile.csv (rail polyline) and working/osm_highways_mtn.json
(cached Overpass result for highway=* in the mountain-section bbox).

Writes working/road_crossings.json and working/road_corridors.json.
"""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")

A0, B1 = 605.7, 812.0
LAT0 = math.radians(51.25)
LON0 = -117.3
M_PER_DEG_LAT = 110540.0
M_PER_DEG_LON = 111320.0 * math.cos(LAT0)

SEARCH_M = 25.0     # corridor width for "road visible from track"
GRID_M = 200.0


def proj(lat, lon):
    return ((lon - LON0) * M_PER_DEG_LON, (lat - LAT0) * M_PER_DEG_LAT)


def load_rail():
    rows = [r for r in csv.DictReader(open(os.path.join(WORK, "profile.csv")))
            if A0 <= float(r["dist_km"]) <= B1]
    pts = [(float(r["dist_km"]),) + proj(float(r["lat"]), float(r["lon"]))
           for r in rows]
    return pts  # (km, x, y)


def load_ways():
    d = json.load(open(os.path.join(WORK, "osm_highways_mtn.json")))
    ways = []
    for e in d.get("elements", []):
        if e.get("type") != "way" or "geometry" not in e:
            continue
        geom = [(p["lat"], p["lon"]) for p in e["geometry"]]
        if len(geom) < 2:
            continue
        segs = [(proj(a[0], a[1]), proj(b[0], b[1]))
                for a, b in zip(geom, geom[1:])]
        t = e.get("tags", {})
        ways.append(dict(segs=segs,
                         cls=t.get("highway", ""),
                         name=t.get("name", ""),
                         ref=t.get("ref", "")))
    return ways


def orient(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def seg_intersect(p1, p2, q1, q2):
    """Proper intersection point or None (projected coords)."""
    x1, y1 = p1; x2, y2 = p2
    x3, y3 = q1; x4, y4 = q2
    d1 = orient(x3, y3, x4, y4, x1, y1)
    d2 = orient(x3, y3, x4, y4, x2, y2)
    d3 = orient(x1, y1, x2, y2, x3, y3)
    d4 = orient(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if det == 0:
            return None
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) -
              (x1 - x2) * (x3 * y4 - y3 * x4)) / det
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) -
              (y1 - y2) * (x3 * y4 - y3 * x4)) / det
        return (px, py)
    return None


def pt_seg_dist(px, py, q1, q2):
    x1, y1 = q1; x2, y2 = q2
    vx, vy = x2 - x1, y2 - y1
    L2 = vx * vx + vy * vy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / L2))
    return math.hypot(px - (x1 + t * vx), py - (y1 + t * vy))


def main():
    rail = load_rail()
    ways = load_ways()

    # grid index of road segments
    grid = {}
    for wi, w in enumerate(ways):
        for si, (q1, q2) in enumerate(w["segs"]):
            x0, y0 = q1; x1, y1 = q2
            ix0 = int(min(x0, x1) / GRID_M); ix1 = int(max(x0, x1) / GRID_M)
            iy0 = int(min(y0, y1) / GRID_M); iy1 = int(max(y0, y1) / GRID_M)
            for ix in range(ix0, ix1 + 1):
                for iy in range(iy0, iy1 + 1):
                    grid.setdefault((ix, iy), []).append((wi, si))

    # 1) proper crossings
    crossings = []
    for i in range(len(rail) - 1):
        km, x1, y1 = rail[i]
        _, x2, y2 = rail[i + 1]
        ix0 = int(min(x1, x2) / GRID_M) - 1; ix1 = int(max(x1, x2) / GRID_M) + 1
        iy0 = int(min(y1, y2) / GRID_M) - 1; iy1 = int(max(y1, y2) / GRID_M) + 1
        for ix in range(ix0, ix1 + 1):
            for iy in range(iy0, iy1 + 1):
                for wi, si in grid.get((ix, iy), []):
                    q1, q2 = ways[wi]["segs"][si]
                    p = seg_intersect((x1, y1), (x2, y2), q1, q2)
                    if p is not None:
                        w = ways[wi]
                        crossings.append(dict(
                            km=km, lat=0.0, lon=0.0,
                            cls=w["cls"], name=w["name"], ref=w["ref"]))
    # dedupe & project back to lat/lon (approx via nearest rail point)
    crossings.sort(key=lambda c: c["km"])
    out = []
    for c in crossings:
        if out and abs(c["km"] - out[-1]["km"]) < 0.05 and \
                c["name"] == out[-1]["name"]:
            continue
        out.append(c)
    for c in out:
        r = min(rail, key=lambda r: abs(r[0] - c["km"]))
        km, x, y = r
        lat = LAT0 * 180.0 / math.pi + y / M_PER_DEG_LAT
        lon = LON0 + x / M_PER_DEG_LON
        c["lat"] = round(lat, 5)
        c["lon"] = round(lon, 5)
        c["km"] = round(km, 2)
    json.dump(out, open(os.path.join(WORK, "road_crossings.json"), "w"),
              indent=1)
    print(f"crossings: {len(out)}")
    for c in out:
        print(f"  km {c['km']:7.2f}  {c['cls']:14s} "
              f"{c['ref'] or '':8s} {c['name']}")

    # 2) road-visible corridors
    visible = []
    for i in range(len(rail) - 1):
        km, x1, y1 = rail[i]
        ix = int(x1 / GRID_M); iy = int(y1 / GRID_M)
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for wi, si in grid.get((ix + dx, iy + dy), []):
                    q1, q2 = ways[wi]["segs"][si]
                    d = pt_seg_dist(x1, y1, q1, q2)
                    if d < SEARCH_M and (best is None or d < best[0]):
                        best = (d, ways[wi]["cls"], ways[wi]["ref"],
                                ways[wi]["name"])
        visible.append((km, best))
    runs = []
    cur = None
    for km, best in visible:
        on = best is not None
        if on and cur and abs(km - cur[1]) < 0.15 and \
                cur[3] == best[1]:
            cur[1] = km
            cur[2] = min(cur[2], best[0])
        elif on:
            cur = [km, km, best[0], best[1], best[2], best[3]]
            runs.append(cur)
        else:
            cur = None
    json.dump([dict(km0=round(r[0], 2), km1=round(r[1], 2),
                    dist_m=round(r[2], 1), cls=r[3],
                    ref=r[4], name=r[5]) for r in runs],
              open(os.path.join(WORK, "road_corridors.json"), "w"), indent=1)
    print(f"road-visible corridors: {len(runs)}")
    for r in runs:
        print(f"  km {r[0]:7.2f}-{r[1]:7.2f}  {r[3]:14s} "
              f"{r[4] or '':8s} {r[5]} ({r[2]:.0f} m)")


if __name__ == "__main__":
    main()
