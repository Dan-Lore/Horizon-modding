# Ad Astra Horizon tracker

Generated from `mods/adastra/tracker/catalog.json` (mod 0.1.0, Horizon `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca`, hooks 411).
Regenerate with `python3 mods/adastra/tools/check.py`.

| Wave | System | Status | Smoke |
| --- | --- | --- | --- |
| W0 | Scaffold, attribution, pack script | done | python3 tools/pack-adastra.py writes mods/adastra/dist/adastra.hmod with POSIX paths, horizon-mod.toml, and horizon-native.json. Join a world and expect the Ad Astra Horizon 0.1.0 login line. |
| W1 | Materials and moon/mars blocksets | done | /give @s adastra:desh_ingot, adastra:moon_stone, adastra:mars_stone, adastra:cheese, adastra:flag. Place the stones; craft cobble from stone. |
| W2 | FE buffer, coal generator, solar | done | Place adastra:coal_generator with coal in slot 0 beside a machine. Energy gauge fills. Place adastra:solar_panel; daytime FE accumulates in its buffer. |
| W3 | Compressor plates | done | Place adastra:compressor next to a charged generator. Put adastra:desh_ingot or steel_ingot in the input; take the plate. FE drains while progressing. |
| W4 | Oxygen, suit, vacuum marker | done | Use suit pieces to don. Fill adastra:oxygen_tank at adastra:oxygen_loader. Action bar shows O2. Stand near adastra:vacuum_marker without a sealed suit: chat reports vacuum damage. |
| W5 | Fuel refinery | done | Put adastra:oil in adastra:fuel_refinery with FE; take adastra:rocket_fuel. |
| W6 | NASA workbench and rocket stub | done | Craft adastra:rocket_t1 at the workbench recipes. Use the rocket: countdown chat, then launch stub (dimensions blocked). |
| W7 | Oxygen distributor | done | Place adastra:oxygen_distributor with FE and an oxygen tank inside a vacuum marker zone; sealed breathing resumes without suit drain while in range. |
| W8 | Cryo freezer | done | adastra:cryo_freezer turns ice / blue ice into adastra:ice_shard (≥2 recipes) when powered. |
| W9 | Gravity stub and pack notes | done | Stand on moon_stone or mars_stone: action bar shows low-g. Pack agent follows docs/adastra-plan.md smoke contract; keep on=[] until /give works. |
| W10 | Custom dimensions / planet travel | blocked | Horizon dimensions API not available on hooks 411. Rockets stay launch stubs. |
