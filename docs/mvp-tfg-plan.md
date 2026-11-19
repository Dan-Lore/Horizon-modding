# MVP plan — TFG-inspired pack on Horizon

> **Status (2026-11-19): historical.** Batch A on Nightly `fdc87ae` is done.  
> Current instances / next work: **`AGENTS.md`**, `pack/draft-mods.toml`, **`docs/gtceu-continuation-plan.md`**.  
> Do not resurrect `create-dev` / single-instance wording below as live policy.

**Goal of MVP:** one playable Nightly-based draft instance that feels like the *start* of a TFG-style stack (QoL + early tech hooks), not TerraFirmaGreg parity.

**Non-goals for MVP:** full TFC, GregTech, Greate, Ad Astra, quest book, balance, public pack repo polish.

**Constraints (agreed):**

- One launcher instance only.
- Prefer **published Nightly** as the pack base.
- Existing good mods → use; ahead of Nightly → **wait** (no empty native rebuilds).
- Native builds only when the mod set or Nightly base actually changes.
- **One batch native-build** for the pack; `left_out` for failures; one-mod builds only for debug.
- Public modpack = separate repo later; this workshop stays draft.

**Locked mod list:** [`docs/mod-transfer-list.md`](mod-transfer-list.md) + `pack/draft-mods.toml`.

---

## MVP definition (done when…)

Player can:

1. Launch **one** draft instance on **current Nightly** (or the first Nightly that unlocks Create 0.9, if we explicitly roll the base forward once).
2. Use **JEI** + **Jade** in-world (smoke-tested).
3. Have a written list of **adopted registry mods** vs **waiting** vs **to build ourselves**.
4. See Create either **in the build** (Nightly ≥ Create pin) or clearly **Waiting** — not a second instance.
5. No second parallel native stack; obsolete instances deleted.

Optional stretch (only if cheap / already fits Nightly): AppleSkin, Continuity.

**Explicitly out of MVP:** Create (until Nightly catches up); any TFC/GT gameplay. AE2 **is** in MVP on Nightly (alone with QoL), not together with Create-ahead-of-Nightly.

---

## Pillars

| Pillar | MVP approach |
| --- | --- |
| **A. Platform** | Single instance; Nightly base; rare native builds |
| **B. Adopt** | JEI, Jade (+ soft QoL if they fit) |
| **C. Wait** | Create 0.9 until Nightly ≥ `4e5296d` (or successor pin) |
| **D. Tech on Nightly** | AE2 with the Nightly MVP batch (it already built on `fdc87ae`; only failed next to Create’s newer pin) |
| **E. Own work** | Only after MVP adopt/wait path is stable — tiny TFC-inspired slice (post-MVP phase 1) |

---

## Phase 0 — Housekeeping (no native build)

- [ ] Keep **one** pack instance; delete the spare (`tfg-horizon-draft` vs `TFG Horizon Draft`).
- [ ] Play/smoke on whatever is already built **without** rebuilding: confirm JEI/Jade if that instance still works; note Create as waiting if base ≠ pin.
- [ ] Manifest `pack/draft-mods.toml` = source of truth: `built` / `waiting` / `left_out`.
- [ ] Daily `tools/check-registry.ps1` (≤1×/day): Create, AE2, JEI, Jade, TFC/GT keywords.

**Exit:** one instance name, clear waiting list, no rebuild.

---

## Phase 1 — Next intentional native build (mod list)

Base: **latest published Nightly** (today: `fdc87ae`).  
**Do not include** Create until it fits that Nightly. AE2 **does** fit — include it.

### Build list (MVP batch)

| Include? | Mod | id | Why |
| --- | --- | --- | --- |
| **Yes** | JEI for Horizon | `jei` | Core MVP QoL |
| **Yes** | Jade | `jade` | Core MVP QoL |
| **Yes** | AE2 | `ae2` | Fits Nightly `fdc87ae` (was in `native-fdc87ae-…`); only clashed with Create’s newer pin `4e5296d` |
| Soft yes | AppleSkin | `appleskin` | Cheap HUD; drop if left out |
| Soft yes | Continuity | `connected_textures` | Cheap visuals; drop if left out |
| **Yes (own)** | GregTech | `gtceu` | Tiny GT-inspired alloy smelter (`mods/gtceu/`) |
| **No — wait** | Create | `create` | No build for our Nightly; 0.9 needs newer Horizon |

One `native-build` with that set (not one rebuild per soft mod).

**Exit:** JEI+Jade+AE2 in `native-mods.json` `mods` (not only `left_out`); Create stays documented as waiting.

### Build vs launch: where errors show

| Stage | What happens |
| --- | --- |
| **Native build** | Broken mixin/compile for **one** mod usually **does not kill the whole stack**: launcher **leaves that mod out** (and its dependents), retries (up to a few compiles), writes `left_out` in `native-mods.json`. Hard failures (tooling/Cargo lock / shared crash) can still abort the build. |
| **Game launch / play** | Catch runtime bugs (UI, crashes in-world). Left-out mods simply won’t be there — check Mods page / `native-mods.json` after build. |

**Cheaper strategy**

- **Default:** one batch = MVP list above (JEI+Jade+AE2 ± soft). Isolation already tells you who was left out.
- **One-mod builds:** only when debugging a **new / suspicious** mod or a failed batch where blame is unclear — not for every registry install (full Horizon compile each time is the expensive part).
- **Never** add Create “to see” while it’s known incompatible with our Nightly — empty long build.

---

## Phase 2 — Unlock Create (event-driven, one rebuild)

Trigger (daily watch or manual):

- New Nightly includes Create’s pin (today: ≥ `4e5296d`), **or** registry publishes Create that builds on our Nightly.

Then **one** rebuild: Nightly + JEI + Jade + AE2 + Create (+ soft QoL), if AE2 still applies on that Nightly.

**Exit:** Create playable in the **same** instance as JEI/Jade/AE2.

---

## Phase 3 — Post-MVP (not started in MVP)

Only after Phase 1–2 are green:

1. **Own content:** first small TFC-inspired `.hmod`/`.hnmod` (one mechanic), with attribution — not “TFG”.
2. Later: Greg-like machines only when Horizon mod API / upstream work makes it sane.
3. Spin **public pack repo** when the draft stack is worth sharing.

---

## Decision cheatsheet

| Situation | Do |
| --- | --- |
| Mod good, fits Nightly | Use it |
| Mod good, needs newer Horizon | Wait for Nightly; note in manifest |
| Older mod fits Nightly | Prefer that over waiting only if usable; Create has **no** such build on `fdc87ae` |
| Nothing usable | Own mod / contrib — **after** MVP adopt path |
| Urge to “just rebuild and see” | **No** |

---

## Current snapshot (2026-11-12)

| Item | State |
| --- | --- |
| Nightly / play | `fdc87ae` → `native-fdc87ae-0b62c5b257f2` |
| Batch A | JEI, Jade, AE2, AppleSkin, Continuity, **GregTech 0.1.1** — `left_out` empty |
| Create | removed from instance / waiting (≥ `4e5296d`) |
| GregTech | `mods/gtceu/` → `gtceu.hmod` 0.2 — Steam Age (boiler + 3 machines) |
| TFC | still post-MVP |

---

## Success metrics

- ≤ 1 pack instance.
- ≤ 1 intentional native rebuild per real stack change (Nightly bump or mod unlock).
- MVP playable QoL without pretending Create/TFC are done.
- Manifest always says what’s waiting and why.
