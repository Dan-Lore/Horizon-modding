# Greate Horizon

Greate-inspired **Create × GregTech** bridge for Horizon. Version **0.1.0**.

## Status

**Code / data slice ready. Co-build parked** until Create and AE2/GregTech share a Nightly.

| Piece | State |
| --- | --- |
| Voltage tier table (ULV–UV) | Pure Rust + unit tests |
| Stress capacity per shaft tier | Pure Rust |
| Recipe tier gate helper | Pure Rust |
| `andesteel_shaft` / `steel_shaft` / `aluminium_shaft` / `stainless_shaft` blocks | Content stubs |
| Live Create kinetic network | Needs Create on same native |
| Live GregTech EU attach | Needs GregTech on same native |

## Pin

Designed for `fdc87ae` / hooks 411 beside GregTech+AE2. Create currently needs `4e5296d` — do not native-build this into `tfg-dev` until pins converge.

Catalog: `cr_greate_integration` → `partial` (awaits pin).
