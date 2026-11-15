# TFC Horizon tracker

Generated from `mods/tfc/tracker/catalog.json` (mod 0.1.0, Horizon `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca`, hooks 411).
Regenerate with `python3 mods/tfc/tools/check.py`.

| Wave | System | Status | Smoke |
| --- | --- | --- | --- |
| W0 | Scaffold, attribution, pack script | done | python3 tools/pack-tfc.py writes mods/tfc/dist/tfc.hmod with POSIX paths, horizon-mod.toml, and horizon-native.json. Join a world and expect the TFC Horizon 0.1.0 login line. |
| W1 | Calendar, thin climate, thirst | done | Action bar updates every 40 ticks with season, month, °C, thirst, and G/F/V/P/D. Thirst reaches 0 after 24000 ticks and chat says to drink. Hold-use tfc:jug or tfc:wooden_bucket (32 ticks) and thirst rises; the vessel stays. |
| W2 | Rock and ore slice, prospector | done | /give @s tfc:andesite_raw and /give @s tfc:ore_native_copper. Place the ore, hold tfc:prospector_pick, and right-click it: chat names native copper and a local rock preview. |
| W3 | Knapping stand-in, stone tools, firepit | done | Craft tfc:stone_axe from andesite cobble + stick (knapping UI is this crafting recipe). Craft and place tfc:firepit, fuel it with coal or a log in slot 0, put minecraft:beef in the input, and take tfc:cooked_meat. |
| W4 | Clay, pottery, pit kiln, charcoal pit | done | Craft tfc:unfired_vessel from clay balls. Place tfc:pit_kiln, insert the unfired vessel, and take tfc:vessel. Place tfc:charcoal_pit, insert minecraft:oak_log, and take minecraft:charcoal. |
| W5 | Charcoal forge and copper cast | done | Place tfc:charcoal_forge with fuel in slot 0. Smelt tfc:nugget_native_copper into tfc:copper_ingot, then cast tfc:copper_axe_head and craft it with a stick into tfc:copper_axe. |
| W6 | Bloomery, anvil, welding stand-in | done | Bloomery turns tfc:nugget_hematite into tfc:raw_iron_bloom. Anvil turns that bloom into tfc:wrought_iron_ingot and an ingot into a sheet. Two copper ingots craft into tfc:copper_double_ingot (weld stand-in). |
| W7 | Food size, weight, five nutrients | done | Hold-use tfc:bread or tfc:cooked_meat for 32 ticks. The stack shrinks, the nutrient letters on the action bar move, and the tooltip shows size, weight, and decay days. |
| W7 | Per-stack rot timer | blocked | Decay days are shown on the tooltip. A creation-tick on the stack needs an item-component write this pin does not use, so food does not turn into rot. |
| W8 | Crops with season and temperature gate | done | Place tfc:crop_wheat. In summer (absolute day 48 at this calendar, about 26C) growth advances every 200 ticks and the output slot fills with tfc:wheat at 7. In January (day 0, about 6C, winter) growth stays put. Barley accepts spring and autumn, not summer. |
| W9 | Quern and barrel | done | Quern grinds tfc:wheat into tfc:flour and tfc:limestone_gravel into tfc:flux. Barrel turns minecraft:oak_log into tfc:tannin. |
| W10 | Lumber, log pile, support warning | done | Craft tfc:lumber from an oak log and tfc:support_beam from lumber. Log pile opens 9 slots. Break a tfc rock that has another tfc rock above it and no adjacent support beam: chat warns that the upper rock is unsupported. |
| W10 | Replace unsupported rock with cobble | blocked | set_block needs a BlockStateId. default_state is API 446, after hooks 411, so the warning does not change the block. |
| W11 | Pan and sluice | done | Right-click with tfc:pan and chat points at the sluice. Craft tfc:ore_deposit from gravel + pan. Sluice turns that deposit into tfc:nugget_native_copper. |
| W12 | Blast furnace and brass | done | Blast furnace with fuel, tfc:wrought_iron_ingot, and tfc:flux yields tfc:steel_ingot. Craft copper + zinc ingots into tfc:brass_ingot. Forge also melts tin, bismuth, silver, and gold nuggets. |
| W13 | Animals | deferred | tables/animals.json lists cow, sheep, pig, chicken, horse, wolf, deer, and fish. No entity is spawned. Login line says animals are deferred. |
| W14 | Full rock layers, climate maps, biomes, veins | blocked | No chunk hook places rocks. Prospect chat names a stable preview rock from tables/worldgen.json. The planned layer list is in that file. Place the eight content rocks and eight ores by hand or /give. |
| W15 | Glass, chisel, powderkeg, JEI recipe types | done | Craft tfc:glass_batch from sand + flux and fire it in the pit kiln to minecraft:glass. Right-click a tfc rock with a chisel for the mark line. Right-click tfc:powderkeg for the content-only line. Custom recipe types tfc:firepit, tfc:charcoal_forge, tfc:pit_kiln, tfc:quern, tfc:barrel, tfc:bloomery, tfc:anvil, tfc:sluice, tfc:charcoal_pit, and tfc:blast_furnace are in data/tfc/recipe for JEI once the content snapshot loads. Do not native-build this onto tfg-horizon beside AE2 until that smoke is intentional. |
