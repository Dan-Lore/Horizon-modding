# Ad Astra Horizon

Clean-room Horizon rewrite of an **Ad Astra overworld** slice (materials, FE
machines, oxygen, rocket stub). Not a jar port. Dimensions stay blocked.

Plan: [`docs/adastra-plan.md`](../../docs/adastra-plan.md).  
Tracker: [`tracker/catalog.json`](tracker/catalog.json).

## Build

```bash
python3 mods/adastra/tools/gen_content.py   # needs Pillow (PIL)
python3 mods/adastra/tools/check.py
python3 tools/pack-adastra.py
```

Writes `mods/adastra/dist/adastra.hmod`. Does **not** install onto `tfg-horizon`.
`horizon-native.json`: game pin `fdc87ae`, **mixins** `5a64af9…`, **hooks** `411`.
Pack entry exists with `on = []` until `/give` + visible textures.

## Play slice

1. Login line names Ad Astra Horizon 0.1.0.
2. `/give` desh/steel/moon stone; place coal generator beside compressor.
3. Don suit pieces (use item), fill oxygen tanks at the loader, stand near a vacuum marker.
4. Refine oil → rocket fuel; craft Tier-1 rocket; use it for the launch stub.
5. Distributor makes a vacuum-safe bubble; cryo freezer makes ice shards; moon/mars foot blocks show low-g on the action bar.

Smoke paths are in the catalog. `done` requires a written path.
