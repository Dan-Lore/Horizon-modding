# Dev tips — native code + content registries

**Locked 2026-11-15:** detailed smoke / failure tip sheet. Short mandatory rule: `.cursor/rules/horizon-native-build-smoke.mdc`. Assets/licenses: `.cursor/rules/tfg-horizon-porting.mdc` + `docs/asset-license-table.md`.

## Symptom → cause

| What you see | Likely meaning |
| --- | --- |
| Chat tip, action bar, or HUD (`TFC winter… thirst`) | Native Hooks are in the binary. Items may still be missing |
| `/give` → **Unknown item** | Registries never loaded |
| JEI `@ae2` **and** `@tfc` both red; ~1658 items | Whole content pack rejected. Look for `content mods not loaded:` |
| `content mods not loaded: … sounds minecraft:metal is not a block` | `properties.sounds` must be a block id. `minecraft:metal` and `minecraft:wood` are not. Use `minecraft:iron_block`, `minecraft:stone`, or `minecraft:oak_planks`. One bad block drops **every** content mod, including AE2 |
| No creative tab; AE2 tab is fine | AE2 ≠ proof your content loaded. `the JEI kit in use is ae2's copy` is the embedded JEI, not AE2 items |
| JEI `@greg` / `@gre_` red | Wrong id. The query is `@greglite` |
| Log `content from 1 mod(s)` and ids file is `["ae2"]` | Snapshots not in the prepare cache — restore content, **wipe** `mod-content`, relaunch |
| `left_out` `other-version` / “made for another Horizon version” | Often a **rustc** error, not a pin mismatch. Read `%AppData%\Roaming\horizon-launcher\native\build.log` |
| `unexpected native source: mixins/…json` | The `.hmod` mixin tree may contain only `.rs`, `.toml`, `.md`, and `NOTICE`. No `tables/*.json`, including under `api/` |
| `doesn't have the native hook points` while local `NATIVE_HOOKS_API` is 411 | Launcher downloaded `native_hooks.rs` from GitHub and the TLS read failed. A `hooks` field triggers that download. `--ignore-pins` does not skip it |
| `native-build` “Up to date” after dropping new `.hnmod` | Stale native reused; remove that native tag or force a real rebuild |

**Rule:** login message ≠ items exist. **`/give` is the smoke test.** Creative/JEI only after `/give` works.

## Truth ladder (stop early if a step fails)

1. Instance plays the **active** `native-…` hash you built.
2. That version’s `native-mods.json` lists the mod in `mods[]` (not only files on disk / `left_out`).
3. `versions\<native>\native-content\<id>\` has `horizon-mod.toml` + `assets/` + `data/`.
4. After Play: `instances\<id>\logs\latest.log` → `content from N mod(s)`.
5. `instances\<id>\.horizon-cache\mod-content\<hash>\horizon-mod-ids.json` includes your id(s).
6. `/give <id>:<item>` succeeds; then JEI `@<id>`.

## Where content actually lives

- Combined mod = `.hmod` with content **and** native bits.
- Runtime prepare builds  
  `instances\<id>\.horizon-cache\mod-content\<hash>\`  
  from snapshots under the **played** native’s `native-content\` (and/or `horizon-mods\<id>\`).
- Manually restoring `native-content` **without** deleting `mod-content` often leaves a stale cache that still only has `["ae2"]`.

### Restore recipe (content missing, Hooks already in binary)

1. Unpack `.hmod` with **ZipFile / Python** (not PowerShell `Expand-Archive` — it rejects `.hmod`).
2. Copy **only** `horizon-mod.toml`, `assets/`, `data/` →  
   `versions\<active-native>\native-content\<id>\`.
3. Mirror the same trio → `instances\<id>\horizon-mods\<id>\`.
4. Delete `instances\<id>\.horizon-cache\mod-content\`.
5. Full quit → Play → re-check `horizon-mod-ids.json` → `/give`.

## Instances

| Instance | Play version | Do |
| --- | --- | --- |
| `tfg-horizon` | pinned `native-fdc87ae-428278da87c5` | Last working save. Do not native-build. Re-pin with `instance version tfg-horizon native-fdc87ae-428278da87c5` if it starts following updates |
| `tfg-dev` | `native-fdc87ae-01abd5b2b6a6` | Combined dev native (profile `dev`). This is the only instance to rebuild |

`prune-old-versions` stays off. `tools/pack-greglite.ps1` without `-Out` overwrites `tfg-horizon\horizon-native-mods\greglite.hmod`.

Build command that matches the 2026-11-15 dev native:

```text
horizon-launcher native-build --instance tfg-dev --version nightly-2026-11-08-fdc87ae --trust-native-code --ignore-pins
```

## Pack pins

| Want | Use |
| --- | --- |
| AE2 **15.4.18** + Greglite + JEI/Jade/… + own mods | Nightly `fdc87ae` |
| Create | Separate pin — cannot co-build with AE2 today |
| Tip `9f42064` | No AE2 15.4.18 |

`horizon-mods.txt` must have `mod.<id>:true` for mods you expect.

## Own `.hmod` (learned while building tfg-dev)

- `horizon-native.json` → `mixins` = horizon-mixins `5a64af938ec86b00d53d16a408aabc0038fb3e57`, not the game revision `fdc87ae`.
- Do not put JSON under `mixins/<id>/`. Inline TFC tables into the `.rs` that used `include_str!`. Quests stay in `baked.rs`.
- A `hooks` number makes the launcher fetch `crates/horizon-client/src/game/native_hooks.rs` from GitHub. A failed download is reported as “doesn't have the native hook points” even when the local tree says `NATIVE_HOOKS_API = 411`.
- On this pin's rustc, `static` cannot call `HashMap::new()` (`LazyLock`), event types take one lifetime, item counts are `u32`, `host.level` is `Option<LevelRef>`, and NBT keys are `JavaString` via `From<&str>` only.
- Block `sounds` must name a real block. `minecraft:iron_block` / `minecraft:stone` / `minecraft:oak_planks` load. `minecraft:metal` aborts the entire content prepare.
- Textures: TFC EUPL-1.2 may be fetched. Ad Astra PNG (Terrarium License) and FTB Quests PNG are All Rights Reserved — placeholders stay.

## Smoke checklist

1. `latest.log` contains `content from N mod(s)` and does **not** contain `content mods not loaded`.
2. `horizon-mod-ids.json` lists every own content mod.
3. `/give greglite:coke`, `/give tfc:crucible`, `/give adastra:desh_ingot`, `/give quests:quest_book`.
4. JEI `@greglite` `@tfc` `@ae2` `@adastra` return items (`@greg` does not).
5. Creative tab only after those succeed. Flat colored icons on Ad Astra / Quests are the allowed placeholders, not a failed load.
