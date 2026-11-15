# Mod transfer list (Minecraft / TFG → Horizon)

**Locked 2026-11-11.**

This is **not** “port TFG jars”. For each Minecraft-side need we either **adopt** a Horizon registry mod, **wait** for one, or **reimplement** later. Java code does not run.

**Build rule (locked):** one native-build for the whole batch. Broken mods go to `left_out`. One-mod builds only for blame/debug.

Source of truth for instance pins: `pack/draft-mods.toml`.  
Phases: `docs/mvp-tfg-plan.md`.

---

## Batch A — Nightly MVP (built 2026-11-12)

| Minecraft / TFG role | Horizon mod | id | How | Status |
| --- | --- | --- | --- | --- |
| JEI | JEI for Horizon | `jei` | Adopt registry | **built** |
| Jade / Waila-like | Jade | `jade` | Adopt registry | **built** |
| Applied Energistics 2 | AE2 | `ae2` | Adopt registry | **built** |
| AppleSkin | AppleSkin | `appleskin` | Soft adopt | **built** |
| Continuity / CTM | ContinuityHorizon | `connected_textures` | Soft adopt | **built** |
| GregTech (Steam Age slice) | Greglite 0.2 | `greglite` | Own `mods/greglite/` | **built** |
| Xaero-like map | World Map | `worldmap` | Adopt registry 0.7.1 | **installed** (rebuild pending) |

**Working base:** `nightly-2026-11-08-fdc87ae` → `native-fdc87ae-8837f1d46495` (instance `create-dev`). `left_out` empty. **Create** not on working.

**Instances (locked 2026-11-14):** exactly **two** — working `create-dev` + test `create-nightly-test`. See `docs/greglite-electric-plan.md`.

---

## Batch B — Create (on test, 2026-11-14)

| Minecraft / TFG role | Horizon mod | id | How | Status |
| --- | --- | --- | --- | --- |
| Create | Create for Horizon | `create` | GitHub 0.9.0 on Nightly ≥ `4e5296d` | **built on test** `native-4e5296d-649518ee8b9d` |

Promote Batch A + Create onto working only after intentional smoke — do not rebuild working casually.

---

## Post-MVP — own / rewrite (not registry yet)

| Minecraft / TFG role | Horizon plan | Notes |
| --- | --- | --- |
| TerraFirmaCraft | **TFC Horizon 0.2.0** in `mods/tfc/` | Clean-room core slice. Plan `docs/tfc-plan.md`. Not installed on `tfg-horizon` (`on = []`) |
| GregTech Modern | **Greglite** Steam → **Electric Age** | v0.2 Steam done. EU + all singleblock electrics: `docs/greglite-electric-plan.md` + `mods/greglite/tracker/catalog.json` |
| Greate / Create×GT | After Create on working + Greglite EU | |
| Ad Astra | Out of near-term list | |
| FTB Quests / quest book | Out of MVP | |
| Full TFG-Modern pack | Never as jar import | Separate public pack repo only when draft is worth sharing |

---

## Explicitly not transferring as gameplay

Launcher **content port** of TFG jars (assets/data only) is experimental reference — **not** the play stack. Original Forge/NeoForge/Fabric code stays on Java.

---

## Checklist (short)

- [x] QoL: JEI, Jade (+ AppleSkin, Continuity soft)
- [x] Tech early: AE2 on Nightly
- [x] Own Greglite v0.2 Steam Age slice in Batch A
- [x] Create on **test** instance (Nightly line / pin `4e5296d`)
- [ ] Promote Create + Batch A onto **working** after smoke
- [x] TFC Horizon 0.2.0 workshop slice (`mods/tfc/`, not on the AE2 pin)
- [ ] Greglite Electric Age (W0–W9) — `docs/greglite-electric-plan.md`
