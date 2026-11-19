# Firmalife (Horizon rewrite)

Firmalife-inspired food vertical slice for Horizon. Version **0.1.2**.

## Scope

- `cheese_wheel`, `drying_mat`, `oven`, `greenhouse_panel`, `vat`, `beehive`, `sprinkler` blocks
- `jar`, `honey_jar`, `cheese`, `dried_fruit`, `raw_honey`, `olive_oil_bottle` + recipes
- Oven: potato → dried fruit; vat: milk → cheese; beehive: raw honey; drying mat: crops → dried fruit
- Sprinkler moistens nearby farmland (`moisture=7`)
- No worldgen, no custom entities, no ARR textures

## Pin

Same as Greglite / TFC: Horizon `fdc87ae`, hooks 411. Pack into `tfg-dev` only when asked.

**Textures:** MIT Firmalife jar via `python mods/firmalife/tools/fetch_firmalife_textures.py` (TFG instance path).
