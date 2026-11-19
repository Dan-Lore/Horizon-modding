# Horizon capability policy (locked 2026-11-19)

## What “100% Horizon” means here (internal)

**Not** “100% of GregTech / TFG Absolute.” For pack completeness quote  
[`tfg-content-coverage.md`](tfg-content-coverage.md) instead.

This doc only means: use **everything Horizon already allows** on the pack pin (`fdc87ae` / hooks **411**).  
A feature may stay unfinished **only** for blockers **1–3**. Our own shortcuts (**4**) are **not** an allowed end state.

### The four points (from workshop dialog)

| # | Blocker | Allowed to leave unfinished? | Examples |
| --- | --- | --- | --- |
| **1** | **Horizon API / engine** on this pin | **Yes** | Custom dimensions, some worldgen/mutate, animals spawn systems still missing |
| **2** | **Mod pin clash** (different Horizon commits) | **Yes** | Create (`4e5296d`) ≠ AE2 (`fdc87ae`) → Greate/Create co-build parked |
| **3** | **Registry / upstream availability** | **Yes** | AE2/Create/Jade delisted from public registry (2026-11-19); tip `dd67b76` unsafe for Batch A |
| **4** | **Our slice / stub / “good enough partial”** | **No — must deepen** | Chat-only rocket, manual `/quests kill`, shallow covers, content-only Firmalife blocks, missing sounds, placeholder art where license allows real assets |

### Explicitly rejected metric

The old catalog line *“done + partial / implementable = 100%”* counted **partial** (including self-limited stubs) as success.  
That satisfied “something in the repo,” **not** “100% of what Horizon permits.”

### New metric (target)

**Horizon-capable completeness** = among features where blockers 1–3 do **not** apply:

- status must be **`done`** (full behaviour + content + license-ok assets: textures, models, sounds, lang, loot, recipes as the upstream slice needs);
- **`partial`** / **`stub`** are **debt**, not done;
- **`horizon_blocked`** only for true **#1** (optionally annotated `#2` / `#3`).

TFG Absolute parity remains a longer horizon; this policy is about **not leaving free Horizon headroom unused**.

## Scope of a “full” port (not code-only)

For each workshop mod, “done” under this policy means, as far as 1–3 allow:

1. **Mechanics** — hooks wired to real gameplay (not login tips / chat theater).
2. **Data** — blocks/items/recipes/loot/tags/menus.
3. **Assets** — textures, models, blockstates, **sounds** (`sounds.json` + ogg where license allows), lang.
4. **Attribution** — `NOTICE` + fetch scripts for vendored open assets; ARR → own/CC0 art, never silent copy.

## Pin

Stay on smoked **`native-fdc87ae-8a627f102c73`** (or newer `native-fdc87ae-*` after a green `tfg-dev` build) until **#3** clears for AE2 (or we consciously drop AE2). Tip `dd67b76` is watch-only.

## Builds

Native-build is expensive → **batch** deepen waves into **one** `tfg-dev` rebuild when a code wave is ready.  
Asset/data-only waves: pack → wipe `mod-content` → Play smoke (**no** native-build).

## Related docs

- Gap inventory + waves: [`deepen-to-horizon-cap.md`](deepen-to-horizon-cap.md)
- Pin/registry context: [`horizon-pin-roadmap-2026-11-19.md`](horizon-pin-roadmap-2026-11-19.md)
- Licenses: [`asset-license-table.md`](asset-license-table.md)
