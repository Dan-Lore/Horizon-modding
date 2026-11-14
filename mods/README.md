# Mods (one folder per mod)

Each Horizon-native mod lives in its **own** subdirectory here. Do not dump a whole pack into one mod folder.

## Convention

```
mods/
  create-horizon/     # upstream Clone/PR work for Delete228/create-horizon (not a parallel Create)
  <mod-id>/           # e.g. tfc-climate, gt-basic-machine, hello-hud
    README.md         # what it does, status, upstream inspiration + links
    NOTICE            # licenses / attribution
    …                 # .hmod and/or .hnmod project files
  _template/          # optional starter copy (keep empty or mirror upstream template)
```

## Rules

1. **One logical mod = one folder** (matches how Horizon loads `.hmod` / `.hnmod`).
2. Port / reimplement **incrementally**; keep the mod playable or clearly WIP in its README.
3. Pack assembly happens under `../pack/`, not by merging sources into one mod.
4. Name folders with stable ids (`kebab-case`), not display titles.

## Git vs download

- **Developers:** this monorepo (for now). Optional later: one git repo per mature mod.
- **Players:** download the built `.hmod` / `.hnmod` from Releases / Horizon registry — not `git clone` of the whole tree.
