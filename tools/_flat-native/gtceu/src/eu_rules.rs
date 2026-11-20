//! Voltage, amps, loss, overclock, and multiblock shell checks.
//!
//! No Horizon types: `rustc --test` can run this file on its own.

/// GregTech tier voltages, ULV through UHV.
pub fn tier_voltage(tier: &str) -> i32 {
    match tier {
        "ulv" => 8,
        "lv" => 32,
        "mv" => 128,
        "hv" => 512,
        "ev" => 2_048,
        "iv" => 8_192,
        "luv" => 32_768,
        "zpm" => 131_072,
        "uv" => 524_288,
        "uhv" => 2_097_152,
        _ => 32,
    }
}

/// Next tier up: LV→MV is ×4.
pub fn tier_up(voltage: i32) -> i32 {
    voltage.saturating_mul(4)
}

/// `(voltage, loss per block)` for a cable material. Unknown materials are LV with loss 1.
pub fn cable_material(material: &str) -> (i32, i32) {
    let (voltage, loss) = match material {
        "cobalt" => (32, 2),
        "manganese_phosphide" => (32, 0),
        "nickel" => (32, 3),
        "tin" => (32, 1),
        "annealed_copper" => (128, 1),
        "copper" => (128, 2),
        "cupronickel" => (128, 1),
        "iron" => (128, 3),
        "magnesium_diboride" => (128, 0),
        "electrum" => (512, 2),
        "gold" => (512, 2),
        "kanthal" => (512, 3),
        "mercury_barium_calcium_cuprate" => (512, 0),
        "silver" => (512, 1),
        "aluminium" => (2_048, 1),
        "black_steel" => (2_048, 2),
        "nichrome" => (2_048, 4),
        "rtm_alloy" => (2_048, 2),
        "steel" => (2_048, 2),
        "uranium_triplatinum" => (2_048, 0),
        "graphene" => (8_192, 1),
        "platinum" => (8_192, 1),
        "tungsten" => (8_192, 2),
        "tungsten_steel" => (8_192, 2),
        "indium_tin_barium_titanium_cuprate" => (32_768, 0),
        "niobium_nitride" => (32_768, 1),
        "niobium_titanium" => (32_768, 2),
        "osmium" => (32_768, 2),
        "naquadah" => (131_072, 2),
        "trinium" => (131_072, 4),
        "uranium_rhodium_dinaquadide" => (131_072, 0),
        "vanadium_gallium" => (131_072, 2),
        "naquadah_alloy" => (524_288, 4),
        "tritanium" => (524_288, 8),
        "yttrium_barium_cuprate" => (524_288, 4),
        "europium" => (2_097_152, 32),
        "ruthenium_trinium_americium_neutronate" => (2_097_152, 0),
        "lead" => (8, 2),
        _ => (32, 1),
    };
    (voltage, loss)
}

/// `1x` carries 1 A, `4x` carries 4 A. Voltage and loss come from the material.
pub fn cable_electrical(material: &str, quad: bool) -> (i32, i32, i32) {
    let (voltage, loss) = cable_material(material);
    let amps = if quad { 4 } else { 1 };
    (voltage, loss, amps)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EuSink {
    /// Forwards a packet at or below its rated voltage.
    Cable,
    /// Runs only on a packet of its own voltage. A higher packet is refused.
    Machine,
    /// Passes a packet at or below its voltage, one way.
    Diode,
    /// Stores a packet of its own voltage (a battery buffer).
    Buffer,
    /// Stores a packet at or below its voltage (an energy hatch).
    Hatch,
}

pub fn accepts(sink: EuSink, sink_voltage: i32, packet_voltage: i32) -> bool {
    if packet_voltage <= 0 || sink_voltage <= 0 {
        return false;
    }
    match sink {
        EuSink::Machine | EuSink::Buffer => packet_voltage == sink_voltage,
        EuSink::Cable | EuSink::Diode | EuSink::Hatch => packet_voltage <= sink_voltage,
    }
}

/// One overclock step is the next tier (×4 voltage): ×2 speed and ×4 EU/t.
/// `None` when the machine is below `min_voltage`.
pub fn overclock(
    min_voltage: i32,
    machine_voltage: i32,
    duration: i32,
    eu_per_t: i32,
) -> Option<(i32, i32)> {
    let min_voltage = min_voltage.max(1);
    if machine_voltage < min_voltage {
        return None;
    }
    let mut steps = 0i32;
    let mut threshold = min_voltage;
    while steps < 8 && machine_voltage >= threshold.saturating_mul(4) {
        threshold = threshold.saturating_mul(4);
        steps += 1;
    }
    let speed = 1i32 << steps;
    let power = 1i32 << (steps.saturating_mul(2));
    Some((
        (duration.max(1) / speed).max(1),
        eu_per_t.max(1).saturating_mul(power),
    ))
}

pub fn chance_passes(roll_key: i32, chance_percent: i32) -> bool {
    let chance = chance_percent.clamp(0, 100);
    roll_key.rem_euclid(100) < chance
}

pub fn facing_offset(name: &str) -> [i32; 3] {
    match name {
        "south" => [0, 0, 1],
        "east" => [1, 0, 0],
        "west" => [-1, 0, 0],
        "up" => [0, 1, 0],
        "down" => [0, -1, 0],
        _ => [0, 0, -1],
    }
}

pub fn opposite_offset(offset: [i32; 3]) -> [i32; 3] {
    [-offset[0], -offset[1], -offset[2]]
}

pub fn battery_capacity(voltage: i32) -> i32 {
    voltage.saturating_mul(1_000)
}

/// EU moved for one amp. Loss is not taken out of a full forwarded amp; callers
/// decay leftover EU in the cable by `loss` after the push.
pub fn amp_eu(voltage: i32) -> i32 {
    voltage.max(0)
}

fn is_air(block: &str) -> bool {
    matches!(
        block,
        "minecraft:air" | "minecraft:cave_air" | "minecraft:void_air" | ""
    )
}

fn add(pos: [i32; 3], offset: [i32; 3]) -> [i32; 3] {
    [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]]
}

const INWARD: [[i32; 3]; 6] = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ShellKind {
    Coke,
    Ebf,
    /// Same hatch layout as EBF; casings only (no coils). Reuses `ebf_casing`.
    Freezer,
    /// N8 oil slice — casings + hatches, same 3×3×3 shell as freezer.
    Distillation,
    Cracker,
    Lcr,
    Cleanroom,
}

impl ShellKind {
    fn controller_suffix(self) -> Option<&'static str> {
        match self {
            ShellKind::Coke => Some("multi_coke_oven"),
            ShellKind::Ebf => Some("multi_electric_blast_furnace"),
            ShellKind::Freezer => Some("multi_vacuum_freezer"),
            ShellKind::Distillation => Some("multi_distillation_tower"),
            ShellKind::Cracker => Some("multi_cracker"),
            ShellKind::Lcr => Some("multi_large_chemical_reactor"),
            ShellKind::Cleanroom => Some("multi_cleanroom"),
        }
    }

    fn hatch_casing(self) -> bool {
        matches!(
            self,
            ShellKind::Freezer
                | ShellKind::Distillation
                | ShellKind::Cracker
                | ShellKind::Lcr
                | ShellKind::Cleanroom
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ShellScan {
    pub heat: i32,
    pub input_hatch: Option<[i32; 3]>,
    pub output_hatch: Option<[i32; 3]>,
    pub energy_hatch: Option<[i32; 3]>,
}

/// Face-centred controller, one-block air interior, 3×3×3 shell.
/// Coke: bricks only. EBF: casings, coils, hatches. Freezer: casings + hatches.
pub fn scan_shell(
    origin: [i32; 3],
    block_at: &dyn Fn([i32; 3]) -> String,
    kind: ShellKind,
) -> Option<ShellScan> {
    for inward in INWARD {
        let center = add(origin, inward);
        if !is_air(&block_at(center)) {
            continue;
        }
        let mut heat = 0;
        let mut input_hatch = None;
        let mut output_hatch = None;
        let mut energy_hatch = None;
        let mut ok = true;
        for dz in -1..=1 {
            for dy in -1..=1 {
                for dx in -1..=1 {
                    if dx == 0 && dy == 0 && dz == 0 {
                        continue;
                    }
                    let pos = add(center, [dx, dy, dz]);
                    let block = block_at(pos);
                    if pos == origin {
                        let suffix = kind.controller_suffix().unwrap_or("");
                        if !block.ends_with(suffix) {
                            ok = false;
                        }
                        continue;
                    }
                    match kind {
                        ShellKind::Coke => {
                            if !block.ends_with("coke_oven_bricks") {
                                ok = false;
                            }
                        }
                        ShellKind::Ebf => {
                            if block.ends_with("input_hatch") {
                                input_hatch = Some(pos);
                            } else if block.ends_with("output_hatch") {
                                output_hatch = Some(pos);
                            } else if block.ends_with("energy_hatch") {
                                energy_hatch = Some(pos);
                            } else if block.ends_with("cupronickel_coil_block") {
                                heat = heat.max(1_800);
                            } else if block.ends_with("kanthal_coil_block") {
                                heat = heat.max(2_700);
                            } else if block.ends_with("ebf_casing") {
                            } else {
                                ok = false;
                            }
                        }
                        ShellKind::Freezer
                        | ShellKind::Distillation
                        | ShellKind::Cracker
                        | ShellKind::Lcr
                        | ShellKind::Cleanroom => {
                            if block.ends_with("input_hatch") {
                                input_hatch = Some(pos);
                            } else if block.ends_with("output_hatch") {
                                output_hatch = Some(pos);
                            } else if block.ends_with("energy_hatch") {
                                energy_hatch = Some(pos);
                            } else if block.ends_with("ebf_casing") {
                            } else {
                                ok = false;
                            }
                        }
                    }
                }
            }
        }
        if !ok {
            continue;
        }
        let needs_hatches = matches!(kind, ShellKind::Ebf) || kind.hatch_casing();
        if needs_hatches && (input_hatch.is_none() || output_hatch.is_none() || energy_hatch.is_none())
        {
            continue;
        }
        return Some(ShellScan {
            heat,
            input_hatch,
            output_hatch,
            energy_hatch,
        });
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn tin_cable_is_lv_one_amp() {
        assert_eq!(cable_electrical("tin", false), (32, 1, 1));
        assert_eq!(cable_electrical("tin", true), (32, 1, 4));
        assert_eq!(cable_electrical("copper", false).0, 128);
    }

    #[test]
    fn machines_take_only_their_voltage() {
        assert!(accepts(EuSink::Machine, 32, 32));
        assert!(!accepts(EuSink::Machine, 128, 32));
        assert!(!accepts(EuSink::Machine, 32, 128));
        assert!(accepts(EuSink::Cable, 32, 32));
        assert!(!accepts(EuSink::Cable, 32, 128));
        assert!(accepts(EuSink::Hatch, 524_288, 32));
        assert!(!accepts(EuSink::Buffer, 128, 32));
        assert!(accepts(EuSink::Buffer, 32, 32));
        assert!(!accepts(EuSink::Diode, 32, 128));
    }

    #[test]
    fn overclock_scales_one_tier() {
        assert_eq!(overclock(32, 32, 80, 2), Some((80, 2)));
        assert_eq!(overclock(32, 128, 80, 2), Some((40, 8)));
        assert_eq!(overclock(128, 32, 80, 2), None);
    }

    #[test]
    fn chance_is_stable() {
        assert!(chance_passes(0, 100));
        assert!(!chance_passes(50, 50));
        assert!(chance_passes(49, 50));
    }

    #[test]
    fn transformer_ratio_is_four_to_one() {
        assert_eq!(tier_up(32), 128);
        assert_eq!(amp_eu(32) * 4, amp_eu(128));
    }

    fn world(cells: &[([i32; 3], &str)]) -> HashMap<[i32; 3], String> {
        cells
            .iter()
            .map(|(p, b)| (*p, (*b).to_owned()))
            .collect()
    }

    fn at(map: &HashMap<[i32; 3], String>, pos: [i32; 3]) -> String {
        map.get(&pos).cloned().unwrap_or_else(|| "minecraft:air".into())
    }

    fn fill_coke(controller: [i32; 3], inward: [i32; 3]) -> HashMap<[i32; 3], String> {
        let center = [
            controller[0] + inward[0],
            controller[1] + inward[1],
            controller[2] + inward[2],
        ];
        let mut cells = Vec::new();
        for dz in -1..=1 {
            for dy in -1..=1 {
                for dx in -1..=1 {
                    if dx == 0 && dy == 0 && dz == 0 {
                        continue;
                    }
                    let pos = [center[0] + dx, center[1] + dy, center[2] + dz];
                    let block = if pos == controller {
                        "gtceu:multi_coke_oven"
                    } else {
                        "gtceu:coke_oven_bricks"
                    };
                    cells.push((pos, block));
                }
            }
        }
        world(&cells)
    }

    #[test]
    fn coke_shell_needs_every_brick() {
        let map = fill_coke([0, 1, 0], [0, -1, 0]);
        assert!(scan_shell([0, 1, 0], &|p| at(&map, p), ShellKind::Coke).is_some());
        let mut broken = map.clone();
        broken.insert([1, 1, 1], "minecraft:stone".into());
        assert!(scan_shell([0, 1, 0], &|p| at(&broken, p), ShellKind::Coke).is_none());
        assert!(scan_shell([0, 1, 0], &|_| "minecraft:air".into(), ShellKind::Coke).is_none());
    }

    fn fill_hatch_shell(
        controller: [i32; 3],
        controller_id: &str,
        coil: Option<&str>,
    ) -> HashMap<[i32; 3], String> {
        let center = [0, 0, 0];
        let mut cells = Vec::new();
        for dz in -1..=1 {
            for dy in -1..=1 {
                for dx in -1..=1 {
                    if dx == 0 && dy == 0 && dz == 0 {
                        continue;
                    }
                    let pos = [center[0] + dx, center[1] + dy, center[2] + dz];
                    let block = if pos == controller {
                        controller_id
                    } else if pos == [1, 0, 0] {
                        "gtceu:input_hatch"
                    } else if pos == [-1, 0, 0] {
                        "gtceu:output_hatch"
                    } else if pos == [0, 0, 1] {
                        "gtceu:energy_hatch"
                    } else if pos == [0, 0, -1] {
                        coil.unwrap_or("gtceu:ebf_casing")
                    } else {
                        "gtceu:ebf_casing"
                    };
                    cells.push((pos, block));
                }
            }
        }
        world(&cells)
    }

    #[test]
    fn ebf_shell_needs_hatches_and_reports_heat() {
        let controller = [0, 1, 0];
        let map = fill_hatch_shell(
            controller,
            "gtceu:multi_electric_blast_furnace",
            Some("gtceu:cupronickel_coil_block"),
        );
        let hit = scan_shell(controller, &|p| at(&map, p), ShellKind::Ebf).expect("shell");
        assert_eq!(hit.heat, 1_800);
        assert_eq!(hit.input_hatch, Some([1, 0, 0]));
        assert_eq!(hit.energy_hatch, Some([0, 0, 1]));
    }

    #[test]
    fn freezer_shell_needs_hatches_no_coils() {
        let controller = [0, 1, 0];
        let map = fill_hatch_shell(controller, "gtceu:multi_vacuum_freezer", None);
        let hit = scan_shell(controller, &|p| at(&map, p), ShellKind::Freezer).expect("shell");
        assert_eq!(hit.heat, 0);
        assert_eq!(hit.input_hatch, Some([1, 0, 0]));
        assert_eq!(hit.output_hatch, Some([-1, 0, 0]));
        assert_eq!(hit.energy_hatch, Some([0, 0, 1]));
        let mut broken = map.clone();
        broken.insert([0, 0, -1], "gtceu:cupronickel_coil_block".into());
        assert!(scan_shell(controller, &|p| at(&broken, p), ShellKind::Freezer).is_none());
    }

    #[test]
    fn n8_hatch_shells_form_with_casings() {
        let controller = [0, 1, 0];
        for (id, kind) in [
            ("gtceu:multi_distillation_tower", ShellKind::Distillation),
            ("gtceu:multi_cracker", ShellKind::Cracker),
            ("gtceu:multi_large_chemical_reactor", ShellKind::Lcr),
            ("gtceu:multi_cleanroom", ShellKind::Cleanroom),
        ] {
            let map = fill_hatch_shell(controller, id, None);
            let hit = scan_shell(controller, &|p| at(&map, p), kind).expect(id);
            assert_eq!(hit.input_hatch, Some([1, 0, 0]));
            assert_eq!(hit.output_hatch, Some([-1, 0, 0]));
            assert_eq!(hit.energy_hatch, Some([0, 0, 1]));
        }
    }
}
