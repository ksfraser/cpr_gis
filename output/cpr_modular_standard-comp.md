# CP Modular Standard (HO) — Revelstoke → Field  [-comp]

Applies to every compressed module in `cpr_module_plan-comp.md`. Built on the
unified end-plate convention used by North-American HO modular groups (Free-mo
style): one shared rail height and end-plate mounting pattern, with module
**width left free**. Because the track is centred and the rail height is fixed
at every end plate, modules of different widths still join cleanly — and any
module can be left out of a setup without breaking the mainline.

Compressed-build artifacts carry a **-comp** indicator (module IDs use **-C**,
e.g. `A-C01`) to distinguish them from the linear **-proto** 1:1000 designs.

## 1. Equipment design standard

- **Scale:** HO 1:87.
- **Train:** 12 ft = 2 × 5-well well-cars + 2 AC4400 + caboose
  (≈ 1,200 prototype ft).
- **Siding/yard rule:** shortest yard/siding track ≥ **12 ft usable**. A
  12 ft usable body sits on 3 × 4-ft modules; add a ladder and west lead +
  east tail and a yard is **5-7 modules** total.

## 2. Scale & compression

- The `*-proto` docs keep the pure **1:1000 run compression** (1 proto km =
  1 model m) as the linear reference.
- The compressed build (**this standard + `cpr_module_plan-comp.md`**) applies
  selective compression instead:
  - Yards: 5-7 modules so the shortest track is 12 ft.
  - Plain single-track runs (18 km = ~15 modules): 1-2 scenic modules, omittable.
  - Tunnels: one portal/scenic module.

## 3. Module geometry

- **Length:** 4 ft (1.2192 m) build module; yards are several 4-ft modules, not
  one long box.
- **Width:** free. Recommended:
  - Single-track scenic modules: **12-18 in** (no need for 2 ft).
  - Yard modules: **≤ 24 in** so they match the 2-ft club/Free-mo width.
  - Big-city terminals (Calgary, Vancouver, Kamloops, outside this section):
    may be wider than 24 in.
- **Frame:** dimensional lumber OK; legs built in, folding, self-supporting.

## 4. Unified end plates (Free-mo style)

- End plates: **3/4 in birch plywood** (or equivalent flat, warp-resistant),
  vertical, flat, parallel to each other and perpendicular to the track.
- **Rail head height: 50 in** above the floor, adjustable 49-51 in via leg
  feet. Grade modules allowed up to 62 in in 3/4 in steps (see §7).
- **Track centred** on every end plate; the last **6 in of track is straight,
  level and square** at the ends; rails stop ~1 in short of the plate with ties
  and ballast to the edge.
- **Join:** C-clamps or 1/4-20 bolts through the plates; fitter rails with a
  metal joiner at each joint (insulated where a block gap is wanted).
- **Why widths can differ:** the mounting pattern, hole spacing, track centre
  and rail height are all shared; only the plate width varies.

## 5. Electrical (Free-mo style)

- **Track Bus:** 2 × 12-16 AWG, Anderson Powerpole PP15-45 (30 A) at each
  end, stacked vertically, hood up; top connector = left rail.
- **Accessory Bus:** PP15-45 stacked horizontally.
- **Booster Common:** single wire, one PP15-45.
- **DCC/LocoNet:** RJ12 (6-conductor) jack at each end, straight-through
  2-ft cables.
- Droppers (24 AWG, ≤ 6 in) on every rail section; rail joiners are not
  an electrical connection.

## 6. Selective omission

Modules are tagged in `cpr_module_plan-comp.md`:

- **CORE** — the minimum operating layout (yards, tunnels, portals).
- **FILLER** — omittable scenic single-track runs.
- **OPTIONAL** — sidings and satellite yards for prototype flavour.

Any FILLER/OPTIONAL module can be dropped and the neighbours still join on the
common end plates — skip them during a first build, add them later.

## 7. Grades

- **Model grade is capped at 2.5%** everywhere.
- Yards are built flat; runs and tunnel/portal modules carry the scene's
  prototype ruling grade (clamped to ±2.5%), signed eastbound. The full
  Vancouver→Calgary climb is NOT reproduced; only mountain-section grades show.
- Per-module grades are listed in `cpr_module_plan-comp.md` and drawn in
  `render/cpr_elevation_profile.png`.
- If the prototype is flat in a scene, the modules are flat — no artificial
  grade is added.

## 8. Handling

- Prefer modules ≤ 6 ft long; the 4-ft module is the standard bay.
- Yards, tunnels and runs are built as multiple 4-ft modules that bolt together
  on the common plates.
