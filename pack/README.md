# Pack draft

**Public modpack = separate git repo later.**  
**One launcher instance only** for the draft pack (duplicates confuse everyone).

## Version policy (short)

- Develop against **published Nightly** when possible.
- If a mod (e.g. Create 0.9) needs a **newer main commit** than Nightly: note it and **wait** (or use an older mod / backport) — do not maintain a second full instance.
- **Native rebuilds are costly** — only on real stack changes.

**Locked mod transfer list:** `docs/mod-transfer-list.md`  
**Instance / batch statuses:** `draft-mods.toml`  
**Pack glue (tags/balance datapack):** [`glue/`](glue/) — no native-build  
**Build rule:** one batch native-build; do not rebuild per mod.

Next rebuild → Nightly + Batch A (JEI, Jade, AE2, ± AppleSkin/Continuity). Create = Batch B when Nightly catches up.
