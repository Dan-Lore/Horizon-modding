# Horizon pin / pack roadmap (2026-11-19)

**Builds:** only when a real pin or mod-set change requires it. Prefer content-only / docs / texture work first.

## 1. Registry scan (today)

Local `horizon-index.json` (59 projects) + `mods search --source horizon`:

| Was (Batch A / TFG draft) | Registry now |
| --- | --- |
| `ae2`, `create`, `jade`, `jei` / `justenoughitems`, `appleskin`, `connected_textures` | **Not in public registry** (`playhorizon.dev/mods/ae2` etc. → “Not in the registry”) |
| TFC / GregTech / Firmalife / Greate keywords | **No** official ports listed |

**Still listed (possible TFG-adjacent):** `create_hypertube`, `industrialforegoing`, `pneumaticcraft`, `deepbore_quarry`, `factory_blocks`, `vastores` / Vast*, `voltz`, `botanypots`, `torchmaster`, Macaw’s set, `silentgems` / `silentgear`, `mysticalagriculture`.

**Watch script:** `tools/check-registry.ps1` correctly reports Batch A ids as missing. Do not treat that as “uninstall our copies” — our **pinned native** still carries AE2/Jade/JEI from the earlier install.

## 2. Pin move (`Nightly · dd67b76` “follows updates”)

| Pin | Role |
| --- | --- |
| **`native-fdc87ae-e0aa83869033`** (base `nightly-2026-11-08-fdc87ae`, hooks **411**) | **Keep.** Smoked working native: AE2 15.4.18 + GregTech 0.5.5 + TFC/Teams in binary; Firmalife/Quests/Ad Astra content-loaded. |
| **`nightly-2026-11-18-dd67b76`** | Tip / HDR / Tab-list fixes. **Do not move the pack here yet.** Public registry no longer lists AE2/Create/Jade; a rebuild on tip would drop Batch A unless those natives reappear with matching pins. |

**Decision:** “Актуальный пин” for TFG draft = **last smoked AE2-capable native (`e0aa`)**, not launcher “Новейшая”. Instances stay pinned; do not set `latest`.

Revisit tip only when: AE2 (or successor) is back on registry **and** notes say it builds on that Nightly, **or** we explicitly accept losing AE2.

## 3. Build capabilities (no native-build)

On hooks **411** / `fdc87ae` we already know (see `docs/dev-tips-native-content.md`):

- Content packs load; bad `properties.sounds` (non-block id) rejects **all** content.
- Mixin zip: only `.rs` / `.toml` / `.md` / `NOTICE` under `mixins/<id>/`.
- `hooks` key forces GitHub download of hook surface — prefer omit + pin.
- Create pin ≠ AE2 pin → Greate co-build parked.

`dd67b76` notes (HDR, Tab list name, world-open fix) do **not** claim new TFG-critical APIs (dimensions, BlockStateId mutate, animals). No capability win that justifies an expensive rebuild today.

## 4. Coverage toward “100% Horizon capabilities”

Clarify metrics:

| Metric | Meaning | Status |
| --- | --- | --- |
| **TFG feature catalog** | implementable rows done/partial | **100%** of implementable (`docs/tfg-feature-audit.md`); 13 still `horizon_blocked` |
| **Horizon engine surface** | every hook/API usable by our mods | **Not 100%** — blocked rows + Create/AE2 pin split |
| **Registry Batch A on tip** | play tip Nightly with AE2 | **Blocked** until registry returns those mods |

Next coverage work **without** rebuild: deepen `partial` behaviour (Firmalife ticks, GregTech covers/pipes), quest lines, glue tags; document blocked hooks for tip when notes list them.

## 5. Textures (license-first)

| Mod | License path | Action |
| --- | --- | --- |
| **Firmalife** | MIT | Done: `fetch_firmalife_textures.py` ← TFG jar |
| **TFC** | EUPL-1.2 | existing `fetch_tfc_textures.py` |
| **GregTech** | LGPL / GTM paths | existing GTM fetch scripts + NOTICE |
| **Ad Astra** | code MIT, **assets ARR** | Done: own procedural art `gen_workshop_textures.py` (no Ad Astra PNG) |
| **Quests / Teams** | FTB ARR | Done: own procedural art (book/board/crate/roster) |
| **Greate** | MIT (treat as) | can vendor from Greate jar when co-build unblocks |

Content-only texture swaps need **Play relaunch + content cache wipe**, not native-build.

## 6. Stub vs real ports (workshop)

Evidence pass 2026-11-19 ([Audit](ea4268c8-65dc-446b-8d69-95ea5c5948a6)): content counts from `data/**/horizon/{block,item}` + recipes; no native-build.

| Mod | Verdict | Evidence | Blockers |
| --- | --- | --- | --- |
| **GregTech 0.5.5** | **partial → real core** | EU/fluids/multis; ~497 blocks / ~983 items / ~1212 recipes | Conveyor/cover attach shallow; not full GTM |
| **TFC 0.2.0** | **partial** | Heat/crucible/anvil/knapping/crops; 63 blocks / 132 items | Animals deferred; worldgen / collapse / per-stack rot blocked |
| **Ad Astra 0.1.0** | **partial** | FE machines, oxygen/suit; 14 blocks / 24 items | Rocket = chat stub; dimensions blocked (hooks 411) |
| **Firmalife 0.1.2** | **partial** | Oven/vat/beehive/drying/sprinkler ticks; 7 blocks / 6 items | Cheese wheel / greenhouse panel content-only |
| **Quests 0.1.0** | **partial** | Commands, team progress, 21 quests / 7 chapters | Kill/adv via manual stub cmds; needs teams |
| **Teams 0.1.0** | **real (narrow)** | Commands + disk store; 1 item | Vanilla `/team` name collision |
| **Greate 0.1.0** | **stub / parked** | Tier math + 4 shafts; login only | Create pin ≠ AE2; no kinetic wiring |

Honesty: catalog “done/partial” ≠ TFG Absolute parity. Pack draft still has only gtceu `on = ["pack"]`; others workshop until intentional smoke.

## Build policy (this wave)

1. **No** `native-build` for tip migration or texture work.
2. One rebuild on `tfg-dev` only if: Firmalife/Quests/Ad Astra must enter the **native** binary (symlink/Developer Mode) **or** registry AE2 returns on a new Nightly we adopt.
3. After content/texture changes: wipe `instances/tfg-dev/.horizon-cache/mod-content/`, full quit, Play, `/give` smoke.

## Immediate next steps

1. Keep pins on `e0aa`; document tip as watch-only.
2. Vendor Firmalife MIT textures (script above).
3. Own/CC0 art pass for Ad Astra + Quests (no ARR).
4. Stub-audit follow-ups in behaviour checklists — Play when asked, not speculative rebuilds.
5. Registry watch ≤1×/day for AE2/Create/Jade return.
