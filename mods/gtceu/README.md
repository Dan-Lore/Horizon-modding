# GregTech (Horizon rewrite)

Display name **GregTech**. Technical id **`gtceu`** until a `gtceu` migration. Version **0.5.5**.  
Textures from GregTech-Modern (LGPL-3.0), see [NOTICE](NOTICE).  
**Completeness vs TFG:** [`docs/tfg-content-coverage.md`](../../docs/tfg-content-coverage.md) — not Absolute GTM.

## Play

| Instance | Role |
| --- | --- |
| `tfg-horizon` / `native-fdc87ae-e0aa83869033` | Pinned working save — **do not native-build** |
| `tfg-dev` | Rebuild / N-waves — **only** here |

```powershell
powershell -File tools/pack-gtceu.ps1 -Out <path-for-tfg-dev>
```

Always pass `-Out` (default without `-Out` targets `tfg-horizon`). Next waves: [`docs/gtceu-continuation-plan.md`](../../docs/gtceu-continuation-plan.md). Behaviour list: [`docs/gtceu-behavior.md`](../../docs/gtceu-behavior.md) — login tip / `coverage.json` do not prove a wave.

## What 0.5.0 adds

- Cable voltage and loss come from the material. `1x` is 1 A, `4x` is 4 A. Tin stays 32 V.
- A machine or battery buffer takes a packet only at its own voltage. A higher packet is refused. There is no explosion.
- Diodes pass one amp along `facing`. Transformers trade 4 A of the low tier for 1 A of the next tier, both ways.
- Battery buffers charge and discharge the battery item of their tier. The old extra capacity on `lv_battery` is gone.
- LV craft chain from copper, iron, coal, slime, and a tin ingot through dust, plate, wire, cable, motor, piston, robot arm, hull, and a second `lv_macerator`.
- Recipes can list several outputs, a chance, a programmed circuit, `min_voltage`, and a fluid in or out. One tier above the minimum is twice as fast and four times the EU/t.
- Boilers turn water into `gtceu:steam`. Turbines burn that steam. Combustion burns lava or `gtceu:diesel`. The gas turbine burns `gtceu:biogas`. The distillery and chemical reactor each move one fluid in and one fluid out.
- `multi_coke_oven` does nothing until its 3×3×3 brick shell is complete, then coal becomes `gtceu:coke` and creosote.
- `multi_electric_blast_furnace` needs casings, one coil, and input, output, and energy hatches. Iron plus coke becomes **hot** steel when coil heat reaches the recipe. An incomplete shell does nothing.
- `multi_vacuum_freezer` needs casings (reuses `ebf_casing`) and the three hatches — no coils. It cools `hot_steel_ingot` into `steel_ingot` with EU.

## What 0.5.2 adds (N8)

- Hatch-shell multis reuse the freezer 3×3×3 (`ebf_casing` + input/output/energy hatches): `multi_distillation_tower`, `multi_cracker`, `multi_large_chemical_reactor`, `multi_cleanroom`.
- Oil slice items: `oil_cell` → `naphtha_cell` (tower) → `ethylene_dust` (cracker) → `polyethylene_ingot` (LCR with coal). Cleanroom turns `epoxy_dust` into `epoxy_foil`.

## What 0.5.3 adds

- `conveyor_module` + `item_pipe` / `fluid_pipe`; covers attach via `use_item_on` (sneak empty-hand remove; filter whitelist item); miner/pump touch the world (`Host::destroy_block` / water absorb).

## What 0.5.4 adds

- Circuit craft chain: `phenolic_circuit_board` → `basic_electronic_circuit` → `good_electronic_circuit` (crafts + assembler / circuit assembler).
- Hot aluminium: EBF `aluminium_dust`+coke → `hot_aluminium_ingot` → freezer → `aluminium_ingot` (needs kanthal-tier heat 1700).

## What 0.5.5 adds

- `fluid_pipe` / `item_pipe` blocks + crafts; `lv_drill` (circuit + motor).

## AE2 Interface / bus side contract (hooks 411)

Stock AE2 15.4.18 on this pin talks to GregTech through Horizon `ModContainer` / `ModFluidTanks` — no custom AE2 API in this crate.

| Face | Items | Fluids |
| --- | --- | --- |
| **Up** | insert (inputs) | fill (input tanks) |
| **Down** | extract (outputs) | drain (output tanks) |
| **N/S/W/E** | insert + extract | fill + drain |

Smoke: Export Bus / ME Interface on top or a side of `lv_macerator` / `hv_chemical_bath`; Import Bus under the machine; Pattern Provider against an `input_hatch` or the same side contract on a singleblock. Bath/washer still idle without water in tank 0.

## Build pin

`tools/pack-gtceu.ps1` records Horizon `fdc87ae`, mixins `5a64af93`, and hooks **411** so native-builds on this pin stay beside AE2 15.4.18. The launcher still rewrites the crate revision to the game it compiles.
