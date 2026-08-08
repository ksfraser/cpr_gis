#!/usr/bin/env python3
"""Elevation / grade / curvature profile plot for the CP mainline."""
import csv
import json
import math
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "working")
OUT = os.path.join(ROOT, "output")

rows = list(csv.DictReader(open(os.path.join(WORK, "profile.csv"))))
km = np.array([float(r["dist_km"]) for r in rows])
elev = np.array([float(r["elev_m"]) for r in rows])
g1 = np.array([float(r["grade_1km_pct"] or 0) for r in rows])
curv = np.array([float(r["curv_deg_km"] or 0) for r in rows])
subdiv = [r["subdivision"] for r in rows]
tunnel = np.array([float(r["in_tunnel"] or 0) for r in rows])

towns = {
    "Vancouver": (49.286, -123.113),
    "Hope": (49.384, -121.441),
    "Kamloops": (50.68, -120.33),
    "Revelstoke": (50.99, -118.19),
    "Rogers Pass": (51.30, -117.45),
    "Golden": (51.30, -116.96),
    "Field": (51.40, -116.49),
    "Lake Louise": (51.43, -116.18),
    "Banff": (51.18, -115.57),
    "Calgary": (51.044, -114.062),
}

def nearest_km(lat, lon):
    best, bk = 1e9, None
    for r in rows:
        d = (float(r["lat"]) - lat) ** 2 + (float(r["lon"]) - lon) ** 2
        if d < best:
            best, bk = d, float(r["dist_km"])
    return bk

# subdivision band boundaries
bnds = [0.0]
prev = subdiv[0]
for i, s in enumerate(subdiv):
    if s != prev:
        bnds.append(km[i])
        prev = s
bnds.append(km[-1])
cmap = plt.get_cmap("tab20")
subnames = []
for i in range(len(bnds) - 1):
    if round(bnds[i + 1] - bnds[i], 1) > 0.5:
        subnames.append((subdiv[int(np.argmin(np.abs(km - (bnds[i] + bnds[i + 1]) / 2)))],
                         (bnds[i] + bnds[i + 1]) / 2))

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                         gridspec_kw={"height_ratios": [3, 1, 1]})
ax = axes[0]
for i in range(len(bnds) - 1):
    x0, x1 = bnds[i], bnds[i + 1]
    if x1 - x0 < 0.5:
        continue
    ax.axvspan(x0, x1, color=cmap(len(subnames) * 3 % 20), alpha=0.06)
ax.plot(km, elev, lw=1.2, color="tab:blue")
tkm = km[tunnel > 0.5]
te = elev[tunnel > 0.5]
if len(tkm):
    ax.scatter(tkm, te, s=6, color="tab:red", label="tunnel section", zorder=5)
ax.set_ylabel("Elevation (m, MRDEM-30 DTM)")
ax.set_title("CPKC mainline Vancouver → Calgary: elevation profile (1029 km)")
ax.grid(alpha=0.3)
for name, (la, lo) in towns.items():
    k = nearest_km(la, lo)
    ax.annotate(name, (k, elev[np.argmin(np.abs(km - k))]), textcoords="offset points",
                xytext=(0, 8), fontsize=7, ha="center", color="black", alpha=0.8)
ax.legend(loc="upper right", fontsize=7)

ax2 = axes[1]
ax2.plot(km, g1, lw=0.5, color="tab:green")
ax2.axhline(0, color="grey", lw=0.5)
ax2.set_ylabel("Grade (%) / 1 km")
ax2.grid(alpha=0.3)
ax2.set_ylim(-6, 6)

ax3 = axes[2]
ax3.plot(km, np.abs(curv), lw=0.5, color="tab:purple")
ax3.set_ylabel("|Curvature| (deg/km)")
ax3.set_xlabel("Distance from Vancouver (km)")
ax3.grid(alpha=0.3)
ax3.set_ylim(0, 300)

for name, k in subnames:
    if 0 < k < km[-1]:
        pass
plt.tight_layout()
plt.savefig(os.path.join(OUT, "cpr_profile.png"), dpi=120)
print("wrote", os.path.join(OUT, "cpr_profile.png"))
print("town km positions:")
for name, (la, lo) in towns.items():
    print(f"  {name:<12} {nearest_km(la, lo):7.1f} km")
