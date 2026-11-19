# Mod transfer list (Minecraft / TFG → Horizon)

**Locked 2026-11-11 · refreshed 2026-11-19.**

This is **not** “run TFG jars on Horizon”. For each Minecraft-side need we **adopt** a registry mod, **wait**, or **reimplement** in `mods/<id>/` (reading upstream/TFG sources is allowed — see porting rule + `docs/asset-license-table.md`).

**Build rule:** native-build batches on **`tfg-dev` only**; keep **`tfg-horizon`** pinned. Broken mods → `left_out`.

Source of truth for pins: `pack/draft-mods.toml`.  
MVP history: `docs/mvp-tfg-plan.md`. GregTech next: `docs/gtceu-continuation-plan.md`.

---

## Batch A — Nightly MVP (built 2026-11-12)

| Minecraft / TFG role | Horizon mod | id | How | Status |
| --- | --- | --- | --- | --- |
| JEI | JEI for Horizon | `jei` | Adopt registry | **built** |
| Jade / Waila-like | Jade | `jade` | Adopt registry | **built** |
| Applied Energistics 2 | AE2 | `ae2` | Adopt registry | **built** |
| AppleSkin | AppleSkin | `appleskin` | Soft adopt | **built** |
| Continuity / CTM | ContinuityHorizon | `connected_textures` | Soft adopt | **built** |
| GregTech (Steam → Electric) | GregTech **0.5.0** | `gtceu` | Own `mods/gtceu/` | **built** (behaviour: `gtceu-behavior.md`) |
| Xaero-like map | World Map | `worldmap` | Adopt registry 0.7.1 | **installed** on pack; rebuild policy per AGENTS |

**Working base:** `nightly-2026-11-08-fdc87ae`.  
**Instances (2026-11-15+):** `tfg-horizon` (pinned) + `tfg-dev` (rebuild). Retired: `create-dev`, `create-nightly-test`.

---

## Batch B — Create (parked)

| Minecraft / TFG role | Horizon mod | id | How | Status |
| --- | --- | --- | --- | --- |
| Create | Create for Horizon | `create` | Needs pin `4e5296d` / `9c7f9b2` | **parked** — cannot co-build with AE2 on `fdc87ae` |

Do not promote Create onto the AE2 pack native until pins converge.

---

## Post-MVP — own / rewrite (not registry yet)

| Minecraft / TFG role | Horizon plan | Notes |
| --- | --- | --- |
| TerraFirmaCraft | **TFC Horizon 0.2.0** in `mods/tfc/` | Rewrite from TFC/TFG sources. Plan `docs/tfc-plan.md`. On `tfg-dev`; `on = []` for pinned pack |
| GregTech Modern | **GregTech 0.5.0** + N-waves | Checklist closed: `gtceu-electric-plan.md`. **Next:** `gtceu-continuation-plan.md` |
| Greate / Create×GT | After Create pin + GregTech EU | Parked with Create |
| Ad Astra | **Ad Astra Horizon 0.1.0** in `mods/adastra/` | Overworld slice. Code MIT / assets ARR — `asset-license-table.md` |
| FTB Teams | **Horizon Teams** in `mods/teams/` | Own rewrite. `on = []` on pack pin |
| FTB Quests / quest book | **Horizon Quests** in `mods/quests/` | Own JSON; no FTB SNBT/ARR art |
| Full TFG-Modern as jars | Never | Incremental Horizon rewrite; public pack = separate repo later |

---

## Explicitly not transferring as gameplay

Launcher **content port** of TFG jars (assets/data only) is experimental reference — **not** the play stack. Original Forge/NeoForge/Fabric code stays on Java.

---

## Checklist (short)

- [x] QoL: JEI, Jade (+ AppleSkin, Continuity soft)
- [x] Tech early: AE2 on Nightly
- [x] Own GregTech through Electric Age content checklist (0.5.0)
- [x] Create built once on old test pin — now **parked** (AE2 clash)
- [ ] Create + AE2 on one native (blocked on upstream pin)
- [x] TFC / Teams / Quests / Ad Astra workshop slices (live on `tfg-dev` when built there)
- [ ] GregTech N-waves behaviour verification / next after N6 — `gtceu-continuation-plan.md`
