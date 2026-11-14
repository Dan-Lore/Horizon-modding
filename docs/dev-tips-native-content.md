# Dev tips — native code + content registries

Practical notes from Greglite Batch A (2026-11-12). Not policy — reminders for the next machine/item slice.

## Symptom → cause

| What you see | Likely meaning |
| --- | --- |
| Chat tip / `player_logged_in` works | Native Hooks are in the binary |
| `/give @s mod:item` → **Unknown item** | Registries never loaded |
| No creative tab for your mod; AE2 tab is fine | AE2 can expose items from **native** registration — not proof your content pack loaded |
| JEI `@modid` empty | Same as above; prefer `/give` as the smoke test |
| `latest.log`: `content from N mod(s)` and your id never appears in creative/give | Your snapshot is missing or not on the active native version |

**Rule of thumb:** login message ≠ items exist. Always `/give` the block/item after join.

## Where content actually lives

- Combined mod ships as one **`.hmod`**: `horizon-mod.toml` + `assets/` + `data/` **and** `horizon-native.json` + `mixins/<id>/`.
- A successful native build should snapshot content into  
  `%AppData%\Roaming\horizon-launcher\versions\<native-…>\native-content\<id>\`.
- The game reads that snapshot (beside the native exe), not “whatever is in the zip on disk today”.
- Instance `horizon-mods/<id>/` (content-only folder or `.hmod`) is a useful **fallback** when the active native build has **no** `native-content/<id>`. If the snapshot *does* exist for that id, the game prefers it and ignores the loose copy.

After every native-build that includes a combined mod, check:

```text
versions\<native-hash>\native-content\<mod-id>\horizon-mod.toml
```

If that path is missing while Hooks clearly run — you will get exactly Greglite’s failure mode.

**Observed 2026-11-12:** even successful incremental builds that list `greglite` 0.2.0 in `native-mods.json` can still omit `native-content/` entirely. Treat the check as mandatory; restore by copying `horizon-mod.toml` + `assets/` + `data/` from the workshop (or unpacking the `.hmod`) into that folder before Play.

## Pack / zip pitfalls

- Zip entries must use **POSIX `/`**, not Windows `\`. Prefer Python `zipfile` (`tools/pack-greglite.ps1` pattern); .NET zip helpers on Windows have bitten us.
- Bump mod **version** (or change the packed hash) when the launcher claims “up to date” but you need a real rebuild.
- Keep `horizon-mod.toml` `id` == `horizon-native.json` / mixin `[mod] id`.

## Smoke checklist (new block/item slice)

1. Join world → expect your login tip (optional).
2. `/give @s <id>:<block_or_item>` — must succeed.
3. Creative: your tab on page 2+ (after vanilla), or search by English name.
4. Open machine UI / run the tick recipe once.
5. Skim `instances\<…>\logs\latest.log` for content-mod count and any refuse lines.

## Cheap fixes (before another full native-build)

Missing registries only (binary already has your Hooks):

1. Copy `horizon-mod.toml` + `assets/` + `data/` into  
   `versions\<active-native>\native-content\<id>\`.
2. Optionally mirror the same trio under `instances\<…>\horizon-mods\<id>\`.
3. Fully quit the client and **Play** again (so `native-content` is linked beside the exe).

Use a full native-build when the Rust Hooks change — not as the first response to Unknown item.

## Instance pin

`pack/draft-mods.toml` → `native_version` should match what the launcher actually plays (`instance_list` / Mods page). A rebuild can advance the hash (`native-fdc87ae-…`); old folders may still have content while the new active one does not.
