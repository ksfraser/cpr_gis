#!/usr/bin/env python3
"""
Inventory of mainline features for the CP Vancouver->Calgary route:
  yards (track density), sidings (named), multi-track spans, tunnels, bridges,
  stations/towns, and curve/straight runs.

Produces working/features.json and output/cpr_track_chart.csv
"""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

R = 6371000.0


def hav(a, b):
    p1, l1 = math.radians(a[0]), math.radians(a[1])
    p2, l2 = math.radians(b[0]), math.radians(b[1])
    dp, dl = p2 - p1, l2 - l1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def to_m(lat):
    return 111320.0 * math.cos(math.radians(lat))  # m per deg lon


def main():
    import glob
    import numpy as np

    path = [tuple(p) for p in json.load(open(os.path.join(WORK, "path_nodes.json")))]
    n = len(path)
    elev = np.load(os.path.join(WORK, "elev.npy")).astype(float)
    dists = np.array([hav(path[i], path[i + 1]) for i in range(n - 1)])
    cum = np.concatenate([[0.0], np.cumsum(dists)]) / 1000.0

    ways = []
    for fp in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        d = json.load(open(fp))
        if "elements" in d:
            ways.extend(d["elements"])
    wgeom = []
    winfo = {}
    for w in ways:
        if "geometry" not in w or len(w["geometry"]) < 1:
            continue
        g = w["geometry"]
        pts = [(round(p["lat"], 7), round(p["lon"], 7)) for p in g]
        lat0 = min(p[0] for p in pts)
        lat1 = max(p[0] for p in pts)
        lon0 = min(p[1] for p in pts)
        lon1 = max(p[1] for p in pts)
        t = w.get("tags", {})
        winfo[w["id"]] = {
            "name": t.get("name", ""),
            "tunnel": t.get("tunnel", "") == "yes",
            "bridge": t.get("bridge", "") == "yes",
            "ele": t.get("ele", ""),
        }
        wgeom.append((w["id"], pts, (lat0, lat1, lon0, lon1)))
    print("ways loaded:", len(wgeom))

    def near_ways(vertex, buf_m):
        lat, lon = vertex
        dlat = buf_m / 111320.0
        dlon = buf_m / to_m(lat)
        ids = []
        for wid, pts, (la0, la1, lo0, lo1) in wgeom:
            if lat - dlat > la1 or lat + dlat < la0 or lon - dlon > lo1 or lon + dlon < lo0:
                continue
            if any(hav(vertex, p) <= buf_m for p in pts):
                ids.append(wid)
        return ids

    # per-vertex parallel-track count (every vertex; buffer 150 m)
    par = np.zeros(n, dtype=int)
    for v in range(n):
        par[v] = len(set(near_ways(path[v], 150)))
    # yard density (buffer 250 m, weighted to catch dense clusters)
    dens = np.zeros(n, dtype=int)
    for v in range(n):
        dens[v] = len(set(near_ways(path[v], 250)))

    def spans_of(mask):
        out = []
        s = None
        for i in range(len(mask)):
            if mask[i]:
                if s is None:
                    s = i
            elif s is not None:
                out.append((s, i - 1))
                s = None
        if s is not None:
            out.append((s, len(mask) - 1))
        return out

    # multi-track spans (2+ tracks within 150 m)
    multitrack = []
    for a, b in spans_of(par >= 2):
        if cum[b] - cum[a] >= 0.3:
            multitrack.append({"km0": float(cum[a]), "km1": float(cum[b]),
                               "len_km": float(cum[b] - cum[a]),
                               "max_tracks": int(par[a:b + 1].max())})
    # yard spans (>=5 distinct tracks within 250 m)
    yards = []
    for a, b in spans_of(dens >= 5):
        if cum[b] - cum[a] >= 0.4:
            yards.append({"km0": float(cum[a]), "km1": float(cum[b]),
                          "len_km": float(cum[b] - cum[a]),
                          "max_tracks": int(dens[a:b + 1].max())})

    # named sidings (project onto path)
    sidings = []
    for wid, pts, bb in wgeom:
        name = winfo[wid]["name"]
        if not name:
            continue
        if ("siding" in name.lower() or "passing track" in name.lower()
                or "passing loop" in name.lower()):
            mid = pts[len(pts) // 2]
            # nearest path vertex to midpoint
            j = min(range(n), key=lambda k: (path[k][0] - mid[0]) ** 2 + (path[k][1] - mid[1]) ** 2)
            if hav(mid, path[j]) > 2000:
                continue
            slen = sum(hav(a, b) for a, b in zip(pts, pts[1:]))
            sidings.append({"name": name, "km": float(cum[j]),
                            "len_km": slen / 1000.0, "way": wid})
    sidings.sort(key=lambda s: s["km"])

    # tunnels along path
    tun = np.zeros(n, dtype=bool)
    # re-use tunnel flag from edge mapping (recompute simply from way names proximity)
    for v in range(n):
        ids = near_ways(path[v], 60)
        tun[v] = any(winfo[i].get("tunnel") for i in ids)
    tunnels = []
    for a, b in spans_of(tun):
        if cum[b] - cum[a] >= 0.2:
            tunnels.append({"km0": float(cum[a]), "km1": float(cum[b]),
                            "len_km": float(cum[b] - cum[a])})

    # bridges along path
    br = np.zeros(n, dtype=bool)
    for v in range(n):
        ids = near_ways(path[v], 60)
        br[v] = any(winfo[i].get("bridge") for i in ids)
    bridges = []
    for a, b in spans_of(br):
        if cum[b] - cum[a] >= 0.05:
            bridges.append({"km0": float(cum[a]), "km1": float(cum[b]),
                            "len_km": float(cum[b] - cum[a])})

    # stations/towns near path (from known POIs)
    pois = [
        ("Vancouver (Rocky Mountaineer term.)", 49.2686, -123.0859),
        ("Port Coquitlam", 49.2615, -122.7741),
        ("Mission", 49.1338, -122.3038),
        ("Chilliwack", 49.1645, -121.9491),
        ("Hope", 49.3792, -121.4363),
        ("Boston Bar", 49.8695, -121.4445),
        ("Ashcroft", 50.7298, -121.2757),
        ("Kamloops", 50.6788, -120.3254),
        ("Revelstoke", 50.99, -118.19),
        ("Rogers Pass", 51.30, -117.45),
        ("Golden", 51.30, -116.96),
        ("Field", 51.40, -116.49),
        ("Lake Louise", 51.43, -116.18),
        ("Banff", 51.18, -115.57),
        ("Calgary (downtown)", 51.044, -114.062),
    ]
    stations = []
    for name, la, lo in pois:
        j = min(range(n), key=lambda k: (path[k][0] - la) ** 2 + (path[k][1] - lo) ** 2)
        stations.append({"name": name, "km": float(cum[j])})

    # ---- curve / straight runs ---------------------------------------------
    # recompute curvature per edge (deg/km) with noise floor
    bear = np.array([0.0] * (n - 1))
    for i in range(n - 1):
        p1, p2 = path[i], path[i + 1]
        b = math.degrees(math.atan2(
            math.sin(math.radians(p2[1] - p1[1])) * math.cos(math.radians(p2[0])),
            math.cos(math.radians(p1[0])) * math.sin(math.radians(p2[0]))
            - math.sin(math.radians(p1[0])) * math.cos(math.radians(p2[0]))
            * math.cos(math.radians(p2[1] - p1[1])))) % 360
        bear[i] = b
    curv = np.zeros(n - 1)  # signed deg/km
    for i in range(1, n - 1):
        if dists[i] < 40:
            continue
        d = (bear[i] - bear[i - 1] + 180) % 360 - 180
        curv[i] = d / (dists[i] / 1000.0)

    # classify edges -> runs
    STRAIGHT_DEG_KM = 6.0  # |curv| below this => tangent (<~0.18 deg/100ft)
    runs = []
    kind = None
    s = None
    tot = 0.0
    acc = []
    for i in range(n - 1):
        k = "STRAIGHT" if abs(curv[i]) < STRAIGHT_DEG_KM else "CURVE"
        if k == kind:
            acc.append(curv[i])
            tot += dists[i] / 1000.0
        else:
            if kind is not None and tot >= 0.15:
                runs.append((kind, s, i, tot, acc))
            kind = k
            s = i
            tot = dists[i] / 1000.0
            acc = [curv[i]]
    if kind is not None and tot >= 0.15:
        runs.append((kind, s, n - 1, tot, acc))
    run_rows = []
    for kind, s, e, ln, acc in runs:
        row = {"kind": kind, "km0": float(cum[s]), "km1": float(cum[e]),
               "len_km": round(ln, 2)}
        if kind == "CURVE":
            a = np.array(acc)
            a = a[np.isfinite(a)]
            row["avg_deg_per100ft"] = round(float(np.mean(a)) / 32.8084, 2)
            row["max_deg_per100ft"] = round(float(np.max(np.abs(a))) / 32.8084, 2)
            row["dir"] = "R" if float(np.mean(a)) > 0 else "L"
        run_rows.append(row)

    features = {
        "yards": yards, "sidings": sidings, "multitrack": multitrack,
        "tunnels": tunnels, "bridges": bridges, "stations": stations,
        "runs": run_rows,
    }
    json.dump(features, open(os.path.join(WORK, "features.json"), "w"), indent=1)

    def ft(km):
        return round(km * 3280.84, 0)

    rows = []
    for r in run_rows:
        detail = ""
        if r["kind"] == "CURVE":
            detail = f"{r['dir']} avg {r['avg_deg_per100ft']:+.2f} max {r['max_deg_per100ft']:.2f} deg/100ft"
        rows.append(["RUN " + r["kind"], r["km0"], r["km1"], r["len_km"], detail])
    for y in yards:
        rows.append(["YARD", y["km0"], y["km1"], y["len_km"], f"{y['max_tracks']} tracks"])
    for m in multitrack:
        rows.append(["MULTITRACK", m["km0"], m["km1"], m["len_km"], f"{m['max_tracks']} tracks"])
    for s in sidings:
        rows.append(["SIDING", s["km"], s["km"], s["len_km"], f"{s['name']}  {ft(s['len_km']):.0f} ft"])
    for t in tunnels:
        rows.append(["TUNNEL", t["km0"], t["km1"], t["len_km"], ""])
    for b in bridges:
        rows.append(["BRIDGE", b["km0"], b["km1"], b["len_km"], ""])
    for s in stations:
        rows.append(["STATION", s["km"], s["km"], 0.0, s["name"]])
    rows.sort(key=lambda r: r[1])
    with open(os.path.join(OUT, "cpr_track_chart.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["type", "km0", "km1", "len_km", "detail"])
        for r in rows:
            w.writerow(r)

    print("\nYARDS (track density >= 5):")
    for y in yards:
        print(f"  km {y['km0']:7.1f}-{y['km1']:7.1f}  len {y['len_km']:5.1f}  max_tracks {y['max_tracks']}")
    print("\nSIDINGS:")
    for s in sidings:
        print(f"  km {s['km']:7.1f}  {s['name']:<24} len {s['len_km']:5.2f} km ({s['len_km']*3280.84:.0f} ft)")
    print("\nMULTI-TRACK spans (>=2 tracks, >=0.3 km):")
    for m in multitrack:
        print(f"  km {m['km0']:7.1f}-{m['km1']:7.1f}  len {m['len_km']:5.1f}  max_tracks {m['max_tracks']}")
    print("\nTUNNELS (>=0.2 km):")
    for t in tunnels:
        print(f"  km {t['km0']:7.1f}-{t['km1']:7.1f}  len {t['len_km']:5.1f} km")
    print("\nBRIDGES:")
    for b in bridges:
        print(f"  km {b['km0']:7.1f}-{b['km1']:7.1f}  len {b['len_km']:5.2f} km")
    print("\nSTATIONS/TOWNS:")
    for s in stations:
        print(f"  km {s['km']:7.1f}  {s['name']}")
    print("\nRUNS total:", len(run_rows),
          "curves:", sum(1 for r in run_rows if r["kind"] == "CURVE"),
          "straights:", sum(1 for r in run_rows if r["kind"] == "STRAIGHT"))
    # longest straights
    st = sorted((r for r in run_rows if r["kind"] == "STRAIGHT"), key=lambda r: -r["len_km"])[:8]
    print("\nlongest straights:")
    for r in st:
        print(f"  km {r['km0']:7.1f}-{r['km1']:7.1f}  len {r['len_km']:6.2f} km")


if __name__ == "__main__":
    main()
