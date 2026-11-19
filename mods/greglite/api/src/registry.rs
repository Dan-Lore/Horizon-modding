//! Dynamic GTM-oriented machine specs (pattern parse + steam specials).

use horizon_client::mod_api::ModContainer;
use std::sync::Mutex;

use crate::energy::{BUFFER_EU_CAP, CABLE_EU_CAP, LV_EU_CAP, STEAM_CAP};
use crate::eu_rules;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Kind {
    Boiler,
    SteamProcessor,
    EuProcessor,
    SteamTurbine,
    FuelGen,
    Cable,
    BatteryBuffer,
    Hull,
    Multiblock,
    Diode,
    Transformer,
    ItemHatch,
    EnergyHatch,
}

#[derive(Clone, Debug)]
pub struct Spec {
    pub id: String,
    pub menu: String,
    pub kind: Kind,
    pub recipe_type: Option<String>,
    pub inputs: usize,
    /// First output slot. Further outputs occupy the following slots.
    pub output: Option<usize>,
    pub outputs: usize,
    /// Programmed-circuit slot, when this machine has one.
    pub circuit: Option<usize>,
    pub eu_cap: i32,
    pub steam_ok: bool,
    pub eu_ok: bool,
    pub voltage: i32,
    pub amps: i32,
    pub loss: i32,
}

impl Spec {
    pub fn slots(&self) -> usize {
        match self.kind {
            Kind::Boiler | Kind::FuelGen | Kind::SteamTurbine => 1,
            Kind::ItemHatch => {
                if self.id.ends_with("input_hatch") {
                    2
                } else {
                    1
                }
            }
            Kind::BatteryBuffer => 4,
            Kind::Cable | Kind::Hull | Kind::Diode | Kind::Transformer | Kind::EnergyHatch => 0,
            Kind::Multiblock => 2,
            Kind::SteamProcessor | Kind::EuProcessor => self.inputs + self.outputs.max(1),
        }
    }

    pub fn container(&self) -> Option<ModContainer> {
        match self.kind {
            Kind::Cable | Kind::Hull | Kind::Diode | Kind::Transformer | Kind::EnergyHatch => None,
            Kind::Boiler | Kind::FuelGen | Kind::SteamTurbine => Some(ModContainer {
                slots: 1,
                faces: [vec![0], vec![0], vec![0], vec![0], vec![0], vec![0]],
                inputs: vec![0],
                outputs: vec![],
                menu: Some(self.menu.clone()),
            }),
            Kind::BatteryBuffer => Some(ModContainer {
                slots: 4,
                faces: [
                    vec![0, 1, 2, 3],
                    vec![0, 1, 2, 3],
                    vec![0, 1, 2, 3],
                    vec![0, 1, 2, 3],
                    vec![0, 1, 2, 3],
                    vec![0, 1, 2, 3],
                ],
                inputs: vec![0, 1, 2, 3],
                outputs: vec![],
                menu: Some(self.menu.clone()),
            }),
            Kind::ItemHatch => {
                let input = self.id.ends_with("input_hatch");
                let slots = if input { 2 } else { 1 };
                let indexes: Vec<usize> = (0..slots).collect();
                Some(ModContainer {
                    slots,
                    faces: [
                        indexes.clone(),
                        indexes.clone(),
                        indexes.clone(),
                        indexes.clone(),
                        indexes.clone(),
                        indexes,
                    ],
                    inputs: if input { vec![0, 1] } else { vec![] },
                    outputs: if input { vec![] } else { vec![0] },
                    menu: Some(self.menu.clone()),
                })
            }
            Kind::Multiblock => Some(ModContainer {
                slots: 2,
                faces: [vec![1], vec![0], vec![0], vec![0], vec![0], vec![0]],
                inputs: vec![0],
                outputs: vec![1],
                menu: Some(self.menu.clone()),
            }),
            Kind::SteamProcessor | Kind::EuProcessor => {
                let slots = self.slots();
                let mut faces = [Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new()];
                for i in 0..self.inputs {
                    faces[1].push(i);
                    faces[2].push(i);
                    faces[4].push(i);
                    faces[5].push(i);
                }
                let outputs: Vec<usize> = (0..self.outputs)
                    .filter_map(|i| self.output.map(|first| first + i))
                    .collect();
                for out in &outputs {
                    faces[0].push(*out);
                }
                let inputs: Vec<usize> = (0..self.inputs).collect();
                Some(ModContainer {
                    slots,
                    faces,
                    inputs,
                    outputs,
                    menu: Some(self.menu.clone()),
                })
            }
        }
    }

    pub fn gauge_cap(&self) -> i32 {
        match self.kind {
            Kind::Boiler | Kind::SteamProcessor => STEAM_CAP,
            Kind::Cable | Kind::Diode => (self.voltage.max(8) * self.amps.max(1)).max(CABLE_EU_CAP),
            Kind::Transformer | Kind::EnergyHatch => self.voltage.saturating_mul(4).max(self.voltage),
            Kind::BatteryBuffer => BUFFER_EU_CAP.max(self.voltage * 256),
            _ if self.eu_ok => self.eu_cap.max(self.voltage * 64).max(LV_EU_CAP),
            _ => STEAM_CAP,
        }
    }
}

fn voltage_of(tier: &str) -> i32 {
    match tier {
        "ulv" => 8,
        "lv" => 32,
        "mv" => 128,
        "hv" => 512,
        "ev" => 2048,
        "iv" => 8192,
        "luv" => 32768,
        "zpm" => 131072,
        "uv" => 524288,
        _ => 32,
    }
}

fn dual_input(mtype: &str) -> bool {
    // Only machines whose recipes use `ingredients: [a, b]` (not single `ingredient`).
    matches!(
        mtype,
        "alloy_smelter"
            | "mixer"
            | "assembler"
            | "chemical_reactor"
            | "circuit_assembler"
            | "canner"
            | "packer"
            | "welder"
            | "chemical_bath"
            | "autoclave"
    )
}

fn steam_spec(id: &str) -> Option<Spec> {
    let (kind, recipe, inputs, output, menu) = match id {
        "greglite:steam_solid_boiler_lp" => (
            Kind::Boiler,
            None,
            1,
            None,
            "greglite:steam_boiler",
        ),
        "greglite:steam_solid_boiler_hp" => (
            Kind::Boiler,
            None,
            1,
            None,
            "greglite:steam_solid_boiler_hp",
        ),
        "greglite:steam_alloy_smelter" => (
            Kind::SteamProcessor,
            Some("greglite:alloy_smelter"),
            2,
            Some(2),
            "greglite:steam_alloy_smelter",
        ),
        "greglite:steam_macerator" => (
            Kind::SteamProcessor,
            Some("greglite:macerator"),
            1,
            Some(1),
            "greglite:steam_macerator",
        ),
        "greglite:steam_compressor" => (
            Kind::SteamProcessor,
            Some("greglite:compressor"),
            1,
            Some(1),
            "greglite:steam_compressor",
        ),
        _ => return None,
    };
    Some(Spec {
        id: id.to_owned(),
        menu: menu.to_owned(),
        kind,
        recipe_type: recipe.map(str::to_owned),
        inputs,
        output,
        outputs: if output.is_some() { 1 } else { 0 },
        circuit: None,
        eu_cap: 0,
        steam_ok: true,
        eu_ok: false,
        voltage: 0,
        amps: 1,
        loss: 0,
    })
}

fn parse_spec(id: &str) -> Option<Spec> {
    if let Some(s) = steam_spec(id) {
        return Some(s);
    }
    let Some(rest) = id.strip_prefix("greglite:") else {
        return None;
    };

    if rest.ends_with("_cable_1x") || rest.ends_with("_cable_4x") {
        let quad = rest.ends_with("_cable_4x");
        let material = rest
            .trim_end_matches("_cable_4x")
            .trim_end_matches("_cable_1x");
        let (voltage, loss, amps) = eu_rules::cable_electrical(material, quad);
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::Cable,
            recipe_type: None,
            inputs: 0,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: CABLE_EU_CAP * amps,
            steam_ok: false,
            eu_ok: true,
            voltage,
            amps,
            loss,
        });
    }

    if rest == "input_hatch" || rest == "output_hatch" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::ItemHatch,
            recipe_type: None,
            inputs: 1,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: 0,
            steam_ok: false,
            eu_ok: false,
            voltage: 0,
            amps: 1,
            loss: 0,
        });
    }
    if rest == "energy_hatch" {
        let voltage = eu_rules::tier_voltage("uv");
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::EnergyHatch,
            recipe_type: None,
            inputs: 0,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: voltage * 64,
            steam_ok: false,
            eu_ok: true,
            voltage,
            amps: 2,
            loss: 0,
        });
    }

    if rest.starts_with("multi_") {
        let (recipe, voltage, eu_ok) = if rest == "multi_coke_oven" {
            (Some("greglite:coke_oven".to_owned()), 0, false)
        } else if rest == "multi_electric_blast_furnace" {
            (Some("greglite:electric_blast_furnace".to_owned()), 32, true)
        } else if rest == "multi_vacuum_freezer" {
            (Some("greglite:vacuum_freezer".to_owned()), 32, true)
        } else if rest == "multi_distillation_tower" {
            (Some("greglite:distillation_tower".to_owned()), 32, true)
        } else if rest == "multi_cracker" {
            (Some("greglite:cracker".to_owned()), 32, true)
        } else if rest == "multi_large_chemical_reactor" {
            (Some("greglite:large_chemical_reactor".to_owned()), 128, true)
        } else if rest == "multi_cleanroom" {
            (Some("greglite:cleanroom".to_owned()), 32, true)
        } else {
            (Some("greglite:multiblock".to_owned()), 128, true)
        };
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::Multiblock,
            recipe_type: recipe,
            inputs: 1,
            output: Some(1),
            outputs: 1,
            circuit: None,
            eu_cap: LV_EU_CAP * 16,
            steam_ok: false,
            eu_ok,
            voltage,
            amps: 1,
            loss: 0,
        });
    }

    let (tier, mtype) = rest.split_once('_')?;
    if !matches!(
        tier,
        "ulv" | "lv" | "mv" | "hv" | "ev" | "iv" | "luv" | "zpm" | "uv"
    ) {
        return None;
    }
    // types can contain underscores: battery_buffer_4x, steam_turbine, machine_hull, electric_furnace
    let mtype = &rest[tier.len() + 1..];
    let v = voltage_of(tier);

    if mtype == "steam_turbine" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::SteamTurbine,
            recipe_type: None,
            inputs: 1,
            output: None,
            eu_cap: v * 64,
            steam_ok: true,
            eu_ok: true,
            voltage: v,
            amps: 1,
            loss: 0,
            outputs: 0,
            circuit: None,
        });
    }
    if mtype == "combustion" || mtype == "gas_turbine" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::FuelGen,
            recipe_type: None,
            inputs: 1,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: v * 64,
            steam_ok: false,
            eu_ok: true,
            voltage: v,
            amps: 1,
            loss: 0,
        });
    }
    if mtype == "battery_buffer_4x" || mtype == "charger_4" || mtype == "buffer" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::BatteryBuffer,
            recipe_type: None,
            inputs: 4,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: v * 256,
            steam_ok: false,
            eu_ok: true,
            voltage: v,
            amps: 1,
            loss: 0,
        });
    }
    if mtype == "machine_hull" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::Hull,
            recipe_type: None,
            inputs: 0,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: v * 64,
            steam_ok: false,
            eu_ok: true,
            voltage: v,
            amps: 1,
            loss: 0,
        });
    }
    if mtype == "transformer" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::Transformer,
            recipe_type: None,
            inputs: 0,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: v.saturating_mul(4),
            steam_ok: false,
            eu_ok: true,
            voltage: v,
            amps: 4,
            loss: 0,
        });
    }
    if mtype == "diode" {
        return Some(Spec {
            id: id.to_owned(),
            menu: id.to_owned(),
            kind: Kind::Diode,
            recipe_type: None,
            inputs: 0,
            output: None,
            outputs: 0,
            circuit: None,
            eu_cap: v * 4,
            steam_ok: false,
            eu_ok: true,
            voltage: v,
            amps: 1,
            loss: 0,
        });
    }

    let circuit = matches!(
        mtype,
        "bender" | "extruder" | "forming_press" | "lathe"
    );
    let outputs = if matches!(mtype, "centrifuge" | "electrolyzer") {
        4
    } else {
        1
    };
    let inputs = if dual_input(mtype) {
        2
    } else if circuit {
        2
    } else {
        1
    };
    Some(Spec {
        id: id.to_owned(),
        menu: id.to_owned(),
        kind: Kind::EuProcessor,
        recipe_type: Some(format!("greglite:{mtype}")),
        inputs,
        output: Some(inputs),
        outputs,
        circuit: if circuit { Some(inputs - 1) } else { None },
        eu_cap: v * 64,
        steam_ok: false,
        eu_ok: true,
        voltage: v,
        amps: 1,
        loss: 0,
    })
}

static CACHE: Mutex<Option<std::collections::HashMap<String, Spec>>> = Mutex::new(None);

pub fn find(id: &str) -> Option<Spec> {
    let mut guard = CACHE.lock().ok()?;
    let map = guard.get_or_insert_with(std::collections::HashMap::new);
    if let Some(s) = map.get(id) {
        return Some(s.clone());
    }
    let parsed = parse_spec(id)?;
    map.insert(id.to_owned(), parsed.clone());
    Some(parsed)
}

pub fn is_ours(id: &str) -> bool {
    find(id).is_some()
}
