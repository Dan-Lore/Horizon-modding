# TFG-Modern → Horizon: code vs assets

**Reference instance:** `C:\Users\smoln\curseforge\minecraft\Instances\TerraFirmaGreg-Modern`  
**Rule:** `.cursor/rules/tfg-horizon-porting.mdc`

## What “like TFG” actually means

| What TFG does | What our Horizon rewrite is |
| --- | --- |
| Ships the **author’s published jar** (whole package under that jar’s license) | Builds a **new** `.hmod` / `.hnmod` that reimplements mechanics on Rust |
| Forge/Java runs that jar | Horizon **cannot** execute Forge jars |
| Assets stay inside the original jar as the author released them | Copying PNG/ogg into `mods/<id>/` is a **new distribution** of those files |

So: wanting “the same mod, but on Rust” gives you **MIT/LGPL/EUPL rights to study and rewrite code** where the license allows — it does **not** automatically mean “extract ARR textures into our repo.”  
Closest legal analogue to TFG would be shipping an **official Horizon package from the upstream author**. That does not exist for Ad Astra today.

**Practical paths for ARR assets:** ask upstream for a Horizon-port grant; keep placeholders; or only vendor assets from licenses that allow it.

## Quick table (from TFG jars + upstream LICENSE)

| Mod (TFG role) | Jar / source note | Code | Textures / sounds / models | Horizon workshop |
| --- | --- | --- | --- | --- |
| **Ad Astra** | `ad_astra-forge-1.20.1-1.15.21.jar` — Terrarium License | **MIT** (defined “Code”) | **ARR** (everything else) | Read/reimplement code; **do not** vendor PNG/ogg without permission |
| **TFC** (in TFG) | Bundled in `TerraFirmaGreg-Core-Modern-*.jar` as fork; upstream TFC is **EUPL-1.2** | Open (EUPL / TFG-Core **LGPLv3**) | Generally with the Work — use via attributed fetch (see `mods/tfc/tools/fetch_tfc_textures.py`) | Allowed with attribution + license copy |
| **Firmalife** | `Firmalife-*.jar` says **MIT** | MIT | Treat as MIT unless NOTICE says otherwise | OK to vendor with attribution |
| **GTCEu Modern** | `gtceu-*.jar` — **LGPL-3.0** | LGPL-3.0 | Mostly usable (many from GregTech Refreshed **MIT**); keep credits | GregTech path: OK with NOTICE |
| **Create** | `create-1.20.1-6.0.8.jar` — **MIT** | MIT | MIT (usual Create practice) | OK with attribution |
| **Greate** | `greate-0.0.81.jar` — **MIT** | MIT | Treat as MIT unless NOTICE says otherwise; workshop uses placeholders | `mods/greate-horizon/` rewrite; co-build parked (Create pin ≠ AE2) |
| **AE2** | `appliedenergistics2-*-uelm.jar` — “See GitHub” | Check AE2 repo (typically LGPLv3) | Follow AE2 repo asset terms | Prefer registry AE2 on Horizon; don’t re-vendor unless checked |
| **FTB Quests** | `ftb-quests-*.jar` — **All Rights Reserved** | ARR | ARR | Own quest JSON + placeholders; no FTB art |
| **FTB Teams** | `ftb-teams-*.jar` — **ARR** | ARR | ARR | Own teams mod; no FTB assets |
| **Jade** | `Jade-*.jar` — **CC BY-NC-SA 4.0** | Per CC | Per CC (**NC** = no commercial) | Prefer registry Jade; if vendoring, honor NC/SA |
| **Patchouli** | `Patchouli-*.jar` — **CC BY-NC-SA 3.0** | Per CC | Per CC (NC) | Same caution |
| **KubeJS** | `kubejs-*.jar` — **LGPLv3** | LGPL | Scripts/data as packaged | Read scripts freely; asset case-by-case |

When unsure: open that mod’s `LICENSE` / GitHub and write one line in the mod `NOTICE` before copying any binary asset.

## Ad Astra one-liner (for agents)

Terrarium License splits the project: **code MIT, non-code ARR**. TFG shipping the jar ≠ permission to put Ad Astra textures into `mods/adastra/`.
