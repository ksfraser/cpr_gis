# CP Mountain Section — Design Discussion

How the Revelstoke → Field mountain section goes from the full 1:1000 prototype to a buildable, storable modular layout. Companion docs: `cpr_module_plan-comp.md` (the compressed plan), `cpr_modular_standard-comp.md` (end plates & electrical), the `-proto` 1:1000 reference set, and the `render/` diagrams.

## 1. The 1:1000 idea — 1,000 m of modules

The straightforward way to model 1,029 km of CP mainline is a **1:1000 run compression**: one prototype km becomes one model metre. That gives **≈ 1,030 m (0.64 mi) of bench** for Vancouver–Calgary — roughly **845 four-foot modules** — and even just the mountain section (km 606-812, 206 km) is **206 m / 169 modules**. Every real yard and siding comes out at its true relative length:

- Field yard (2.1 km) = 2.1 m / 2 modules
- Golden yard (2.2 km) = 2.2 m / 2 modules
- A 9,000-ft siding = 2.7 m / 2 modules
- 18 km of single track (Scene A) = 18 m / 15 modules

That is a faithful scale model and an impractical build. The `-proto` docs keep it as the **reference truth**; the compressed plan is what we build.

## 2. Yards: multi-kilometre fans → 12-ft train pockets

Our equipment standard is a **12 ft train** — two 5-well well-car units, two AC4400s and a caboose — about 1,200 prototype feet at HO. A yard only needs to hold that train, so every yard is re-designed around a **12 ft usable track** instead of its prototype length:

| bay | purpose |
|---|---|
| 1 | west lead / headshunt (runaround) |
| 2 | #6 ladder |
| 3-5 | yard body — **12 ft usable** |
| 6 | east tail |

A 2.1 km prototype yard therefore becomes **6 modules (7.3 m)**. Some prototype yards are actually *shorter* than our train and are lengthened to fit it. The compression factor varies yard to yard:

| feature | prototype | model | factor |
|---|---|---|---|
| yard km 606.3-606.9 (9 trk) | 535 m | 7.3 m (6 mods) | 73x |
| yard km 613.8-614.3 (6 trk) | 438 m | 7.3 m (6 mods) | 60x |
| yard km 619.4-619.9 (6 trk) | 444 m | 7.3 m (6 mods) | 61x |
| yard km 658.2-658.7 (8 trk) | 481 m | 7.3 m (6 mods) | 66x |
| yard km 696.3-696.7 (8 trk) | 432 m | 7.3 m (6 mods) | 59x |
| yard km 700.1-700.8 (10 trk) | 635 m | 7.3 m (6 mods) | 87x |
| yard km 702.5-703.0 (5 trk) | 560 m | 7.3 m (6 mods) | 77x |
| yard km 737.9-738.3 (6 trk) | 422 m | 7.3 m (6 mods) | 58x |
| yard km 744.9-745.7 (8 trk) | 756 m | 7.3 m (6 mods) | 103x |
| yard km 750.5-752.7 (10 trk) | 2203 m | 7.3 m (6 mods) | 301x |
| yard km 754.0-755.0 (6 trk) | 1003 m | 7.3 m (6 mods) | 137x |
| yard km 775.3-775.8 (7 trk) | 411 m | 7.3 m (6 mods) | 56x |
| yard km 808.0-810.1 (7 trk) | 2136 m | 7.3 m (6 mods) | 292x |

## 3. Sidings & single-track runs: variable compression

Not everything compresses the same. **Different element types get different compression factors**, chosen so each keeps the scenery that matters:

| element | prototype | model | factor |
|---|---|---|---|
| siding Glacier Siding km 670.8 | 24 m | 4.9 m (4 mods) | 5x |
| siding Glacier Siding km 670.8 (trk 579773342) | 244 m | 4.9 m (4 mods) | 50x |
| siding Glacier Siding km 672.4 | 1996 m | 4.9 m (4 mods) | 409x |
| siding Stoney Creek Siding km 685.7 | 2755 m | 4.9 m (4 mods) | 565x |
| siding Wakely Siding km 688.5 | 333 m | 4.9 m (4 mods) | 68x |
| siding Wakely Siding km 689.5 | 2919 m | 4.9 m (4 mods) | 598x |
| siding Griffith Siding km 694.2 | 562 m | 4.9 m (4 mods) | 115x |
| siding Griffith Siding km 695.7 | 1543 m | 4.9 m (4 mods) | 316x |
| siding Rogers Siding km 700.8 | 719 m | 4.9 m (4 mods) | 147x |
| siding Rogers Siding km 701.7 | 386 m | 4.9 m (4 mods) | 79x |
| siding Beavermouth Siding km 710.0 | 2217 m | 4.9 m (4 mods) | 455x |
| siding Beavermouth Siding km 712.0 | 1005 m | 4.9 m (4 mods) | 206x |
| siding CPKC—Hill Siding (Mountain Main—Golden) km 751.7 | 611 m | 4.9 m (4 mods) | 125x |
| siding CPKC—Hill Siding (Mountain Main—Golden) km 752.2 | 138 m | 4.9 m (4 mods) | 28x |
| siding CPKC—Hill Siding (Mountain Main—Golden) km 754.3 | 2639 m | 4.9 m (4 mods) | 541x |
| siding Glenogle Siding km 764.8 | 2891 m | 4.9 m (4 mods) | 593x |
| siding Glenogle Siding km 765.3 | 355 m | 4.9 m (4 mods) | 73x |
| siding Palliser Siding km 774.0 | 573 m | 4.9 m (4 mods) | 117x |
| siding Palliser Siding km 774.3 | 2894 m | 4.9 m (4 mods) | 593x |
| siding Leanchoil Siding km 781.3 | 837 m | 4.9 m (4 mods) | 172x |
| siding Leanchoil Siding km 782.2 | 330 m | 4.9 m (4 mods) | 68x |
| siding Leanchoil Siding km 783.1 | 2189 m | 4.9 m (4 mods) | 449x |
| siding Ottertail Siding km 796.7 | 2668 m | 4.9 m (4 mods) | 547x |
| siding Ottertail Siding km 797.0 | 353 m | 4.9 m (4 mods) | 72x |
| tunnel km 655.8 (585 m) | 585 m | 1.2 m (1 mod) | 480x |
| tunnel km 668.0 (14636 m) | 14636 m | 1.2 m (1 mod) | 12005x |
| tunnel km 683.9 (1885 m) | 1885 m | 1.2 m (1 mod) | 1546x |
| tunnel km 715.9 (619 m) | 619 m | 1.2 m (1 mod) | 507x |
| tunnel km 759.5 (276 m) | 276 m | 1.2 m (1 mod) | 226x |
| plain single-track run (Scene B) | 33 km | 1-3 scenic modules | ≈ 9,000-27,000× |
| plain single-track run (Scene F) | 51 km | 1-3 scenic modules | ≈ 14,000-42,000× |

- **Sidings:** every prototype siding (5,000-11,000 ft) becomes a **12 ft usable siding** on 4 modules — a 300-700× compression. All sidings interchange with the same 12 ft train.
- **Runs:** a run is scenery, not railroad. 18 km of single track drops to **1-2 omittable modules**; the end plates let you skip them entirely (Section 6).
- **Tunnels:** one portal/scenic module each — MacDonald 14.6 km compresses ≈ 12,000×; the 585 m Eagle Pass and 619 m Albert Canyon bores ≈ 500×.

Net result: **169 modules → 35 core modules (140 ft)**, plus optional sidings and satellite yards.

## 4. Water — rivers, lakes, bridges

River crossings are the strongest scenic anchors. Every one is a **bridge module** in the scene:

| scene | km | water body | rail bridge |
|---|---|---|---|
| A | 605.9 | Columbia River (Revelstoke west approach, 412 m crossing) | 412 m |
| A | 606.6 | Columbia River arm / Revelstoke Lake (Revelstoke) | 134 m |
| A | 614.1 | Illecillewaet River (Revelstoke east) | 136 m |
| B | 627.9 | Illecillewaet River | 127 m |
| B | 650.3 | Illecillewaet River (upper Eagle Pass) | 101 m |
| B | 652.9 | Illecillewaet tributary (Eagle Pass) | 94 m |
| C | 658.2 | Illecillewaet headwaters (Rogers summit) | 88 m |
| C | 683.8 | Stoney Creek (east of Connaught/MacDonald) | 106 m |
| C | 687.9 | Stoney Creek (323 m trestle) | 323 m |
| C | 696.5 | Asulkan / Illecillewaet (Glacier) | 188 m |
| C | 704.1 | Beaver River (Beavermouth) | 172 m |
| D | 725.8 | Beaver River / Albert Canyon | 192 m |
| E | 738.1 | Blaeberry River (Golden west) | 75 m |
| F | 766.5 | Kicking Horse River (Glenogle) | 60 m |

Note the **Columbia River trestle at Golden** (≈ km 748) is under-mapped in OSM; verify and add it as a hero bridge in Scene E. **Revelstoke Lake**: the Columbia north arm widens into a reservoir between the track and the Trans-Canada Highway — see Section 6.

## 5. Mountains — what the scenery is

**Scene A — Revelstoke yard:** Columbia Valley floor at Revelstoke; the west approach rides the Columbia River / Revelstoke Lake shoreline into town.
**Scene B — Eagle Pass (Monashee):** Monashee Mountains — the Illecillewaet valley climbing to Eagle Pass; the tightest curves in the section (16 deg/100 ft at km 654). The Trans-Canada Highway climbs the parallel route.
**Scene C — Rogers Pass summit:** Selkirk Mountains — Rogers Pass summit (1,330 m). Mount MacDonald and the 14.6 km MacDonald Tunnel (1988) replace the 1916 Connaught Tunnel; Stoney Creek and its long trestle; Glacier area.
**Scene D — Beavermouth / Albert Canyon:** Descent to the Columbia Valley — Beavermouth, Albert Canyon bore, and the gorge above Donald.
**Scene E — Golden:** Columbia Valley floor at Golden — the widest open scene; the Purcell/Kootenay foothills beyond the river.
**Scene F — Yoho Valley to Field:** Kicking Horse Pass — Cathedral Mountain, Mount Stephen, Yoho Valley. The railway and the Trans-Canada Highway fight over the same canyon wall (old 4.5% Big Hill vs the modern spiral tunnels).

| tunnel | km | length | module |
|---|---|---|---|
| km 655.8 | 655.8-656.4 | 585 m | 1 scenic portal module |
| km 668.0 | 668.0-682.6 | 14636 m | 1 scenic portal module |
| km 683.9 | 683.9-685.8 | 1885 m | 1 scenic portal module |
| km 715.9 | 715.9-716.5 | 619 m | 1 scenic portal module |
| km 759.5 | 759.5-759.8 | 276 m | 1 scenic portal module |

## 6. Roads — grade-separated, not at-grade

Outside town there are almost **no at-grade road/rail crossings** on the major highways: the Trans-Canada Highway mostly rides bridges and tunnels over (or beside) the track. The OSM-derived crossing list confirms the pattern:

| km | road | class | type |
|---|---|---|---|
| 606.6 | Victoria Street West | secondary | at-grade street (town) |
| 609.7 | Townley Street | secondary | at-grade street (town) |
| 619.4 | Twin Mainline | unclassified | minor at-grade crossing |
| 620.5 | unclassified | unclassified | minor at-grade crossing |
| 668.0 | Trans-Canada Highway | trunk | road passes over tunnel (grade-separated) |
| 672.4 | Trans-Canada Highway | trunk | road passes over tunnel (grade-separated) |
| 683.9 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 700.5 | unclassified | unclassified | minor at-grade crossing |
| 706.7 | Columbia West Forest Service Road | unclassified | minor at-grade crossing |
| 727.9 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 739.0 | Blaeberry River Road | unclassified | minor at-grade crossing |
| 751.7 | 14th Street North | tertiary | at-grade street (town) |
| 752.7 | Kootenay-Columbia Highway | primary | grade-separated (road bridge/tunnel over track) |
| 762.7 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 766.7 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 779.3 | Beaverfoot Road | unclassified | minor at-grade crossing |
| 783.1 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 799.1 | unclassified | unclassified | minor at-grade crossing |
| 807.3 | Trans-Canada Highway | trunk | grade-separated (road bridge/tunnel over track) |
| 810.3 | Field Access Road | tertiary | at-grade street (town) |

**Design rule:** in the model, treat road crossings as scenery — a road bridge arching over the track or a road tucking into a tunnel above the rail. Build at-grade crossings only in the town scenes (Revelstoke streets, Golden's 14th St / BC 95, Field access).

### Revelstoke — the lake buffer

At Revelstoke the **Columbia River / Revelstoke Lake sits between the highway and the railway**, so the road is *not* visible from the track at all. Scene A is built accordingly:

- The west approach rides the **lake shoreline**; the 412 m Columbia crossing dominates the module's foreground.
- The Trans-Canada Highway appears only as a **far-shore ribbon** across the water (a painted/flat backdrop), never at track level.
- No road/rail interaction in Scene A — the water is the separation. This is a rare case where scenery *hides* the road.

### Where the road and rail do run together

The TCH and track share the same canyon wall in the Kicking Horse corridor and near the tunnel portals — those are the spots to show a road glimpsed through the trees. Measured corridors (< 25 m apart):

| km | road | gap |
|---|---|---|
| 673.9-673.9 | Trans-Canada Highway (TCH 1) | 4 m |
| 727.9-727.9 | Trans-Canada Highway (TCH 1) | 21 m |
| 762.7-762.8 | Trans-Canada Highway (TCH 1) | 2 m |
| 766.7-766.8 | Trans-Canada Highway (TCH 1) | 2 m |
| 783.6-783.6 | Trans-Canada Highway (TCH 1) | 9 m |
| 807.3-807.4 | Trans-Canada Highway (TCH 1) | 12 m |

Scene F (762-767, 783, 799, 807) and the MacDonald tunnel zone (673-684) carry most of these road-visible moments.

## 7. Storage — a mountain that packs flat

Free-mo modules are flat plates, easy to stack. Our modules carry mountains, so we design the mountain cross-section to **nest when inverted**.

Each 4-ft module is a **2-ft-wide box whose back rises at 45° to up to 2 ft** — a wedge, not a cliff:

```
  track side          back (sky) side
       |                       /
       |   permanent trees    / 45 deg
       |   & groundform      /
  base  +--------------------/   2 ft tall
        <--------- 2 ft --------->
```

Store two modules as a pair: one normal, one **rolled upside down and set on the other**. The two 45° slopes nest into each other, the flat bases meet, and the pair packs as a **≈ 2 ft × 2 ft × 4 ft box** — scenery on the inside, protected, no separate lids or crates:

```
  box: [ module B upside down ]
       [ module A normal       ]  2 x 2 x 4 ft
```

- Yard modules and tunnel modules use the same 2-ft base and 45° back slope so any two modules pair up for storage.
- Keep the slope at a true 45° so the inverted wedge seats squarely; add thin foam pads on the inside faces.
- Low-relief structures (stations, houses) sit in the flat foreground band and are removable if delicate.
- Scenery height above the base is capped at 2 ft; keep the track side flat at the 50-in rail height (see `cpr_modular_standard-comp.md`).

## 8. Bottom line

- **Build:** 35 core modules (140 ft), optionally 51 (204 ft).
- **Compression:** yards to 12-ft pockets (55-300×), sidings to 12 ft (300-700×), runs to 1-2 modules, tunnels to one portal module.
- **Grade:** max 2.5% model grade, only where the prototype climbs — never the full 1,000 m Vancouver–Calgary rise.
- **Scenery anchors:** 15 river bridges, 5 tunnel portals, the Revelstoke lake buffer, and road-visible canyon walls at Kicking Horse and the tunnel zone.
- **Storage:** 2 ft wide, 45° back slope, modules nest in 2×2×4 ft pairs.
