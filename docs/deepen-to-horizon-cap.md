# Deepen to Horizon capability (point 4 debt)

**Policy:** [`horizon-capability-policy.md`](horizon-capability-policy.md)  
**Updated:** 2026-11-20  
**Pin:** `fdc87ae` / hooks 411 / smoked `native-fdc87ae-8a627f102c73`  
**Builds:** `tools/tfg-dev-native-build.ps1` on **`tfg-dev` only**.

## Verdict

**Engine-headroom catalog** (this doc / feature catalog): implementable rows cleared of #4 stubs.  
**Pack content vs TFG** is a different number — see [`tfg-content-coverage.md`](tfg-content-coverage.md) (~10% blend as of 2026-11-20). Do not tell the player “100% GregTech.”

| Blocker | Examples |
| --- | --- |
| **#1** | Ad Astra planet travel / rocket dimension; TFC animals, chunk worldgen, powderkeg fuse (`explode` / schedule) |
| **#2** | All `cr_*` Create / Greate rows (pin `4e5296d` ≠ AE2 `fdc87ae`) |
| **#3** | Tip Nightly with public AE2/Create/Jade (watch `dd67b76`) |

## Inventory — cleared #4 (this workshop)

| ID | Mod | Status | Notes |
| --- | --- | --- | --- |
| `gl_covers` / pipes / world miner-pump | gtceu | **done** | attach, transfer, `destroy_block` / water absorb |
| `gl_tool_electric` | gtceu | **done** | `lv_drill` + `break_speed` ×8 |
| Firmalife ticks / recipes | firmalife | **done** | cheese, greenhouse panel, multi-input oven/vat/drying |
| Quests kill / adv / UI | quests | **done** | `living_death`, `mob_killed`, `player_advancement_done`, book UI |
| Teams `/hteam` | teams | **done** | |
| Ad Astra FE / O₂ / refinery | adastra | **done** | rocket travel stays **#1** |
| TFC heat/barrel/crops/quern | tfc | **done** | animals/worldgen/powderkeg **#1** |

### Assets

| Mod | Textures | Sounds |
| --- | --- | --- |
| gtceu | GTM LGPL/MIT via fetch | ogg + `sounds.json`; block sounds = valid block ids |
| firmalife | MIT jar fetch | MIT/vanilla refs |
| tfc | EUPL fetch | vanilla event refs (NOTICE) |
| adastra / quests / teams | workshop procedural (ARR upstream) | vanilla refs / silent-by-design (NOTICE) |

## Helper

```text
powershell -NoProfile -File tools\tfg-dev-native-build.ps1 -RepinHorizon -RemoveOldNatives
```

Smoke ladder: active native → `horizon-mod-ids.json` → `/give` per mod — not login tips alone.
