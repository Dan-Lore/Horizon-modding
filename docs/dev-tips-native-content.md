# Dev tips — native code + content registries

**Locked 2026-11-15:** this is the mandatory smoke path after Greglite “in native-mods but JEI empty” / AE2-only creative. Also mirrored in `.cursor/rules/horizon-native-build-smoke.mdc`.

## Symptom → cause

| What you see | Likely meaning |
| --- | --- |
| Chat tip / `player_logged_in` works | Native Hooks are in the binary |
| `/give` → **Unknown item** | Registries never loaded |
| No creative tab; AE2 tab is fine | AE2 ≠ proof your content loaded |
| JEI `@gre_` red / empty | Wrong query **or** content cache missing your id — check `@greglite` and `horizon-mod-ids.json` |
| Log `content from 1 mod(s)` and ids file is `["ae2"]` | Greglite/TFC snapshots not in prepare cache — restore content, **wipe** `mod-content` cache, relaunch |
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

## Pack pins

| Want | Use |
| --- | --- |
| AE2 **15.4.18** + Greglite + JEI/Jade/… | `fdc87ae` (hooks 411) |
| Create | Separate pin — cannot co-build with AE2 today |
| Tip `9f42064` | No AE2 15.4.18 |

`horizon-mods.txt` must have `mod.<id>:true` for mods you expect.

## Own mods (TFC)

- `horizon-native.json` → `mixins` = **horizon-mixins** commit, not the game revision.
- Keep pack `on = []` until `/give` smoke; content-only without Hooks is still not “TFC playable”.

## Smoke checklist

1. `horizon-mod-ids.json` lists every own content mod.
2. `/give greglite:steam_macerator` (or current id) OK.
3. JEI `@greglite` returns items (not `@gre_`).
4. Creative tab / page only as a convenience check after that.
