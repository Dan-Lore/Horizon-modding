//! Boilers, steam turbines, and fuel EU generators.

use crate::energy::{
    burn, eu, set_burn, set_eu, set_packet_voltage, sync_data, STEAM_CAP,
};
use crate::eu_rules;
use crate::fluids::{self, BIOGAS, DIESEL, LAVA, STEAM, WATER};
use crate::net::transfer_eu_out;
use crate::registry::{Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

const BOILER_STEAM_PER_TICK: i32 = 160;
const HP_BOILER_STEAM_PER_TICK: i32 = 480;
const FUEL_COAL: i32 = 1_600;
const FUEL_COAL_BLOCK: i32 = 16_000;
const TURBINE_STEAM_PER_TICK: i32 = 8;
const TURBINE_EU_PER_TICK: i32 = 32;
const FUEL_EU_PER_TICK: i32 = 32;

fn solid_fuel(item: &str) -> i32 {
    match item {
        "minecraft:coal" | "minecraft:charcoal" => FUEL_COAL,
        "minecraft:coal_block" => FUEL_COAL_BLOCK,
        "minecraft:blaze_powder" => FUEL_COAL / 2,
        "minecraft:dried_kelp_block" => FUEL_COAL * 2,
        _ => 0,
    }
}

pub fn tick(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    match spec.kind {
        Kind::Boiler => tick_boiler(host, pos, entity, spec),
        Kind::SteamTurbine => tick_turbine(host, pos, entity, spec),
        Kind::FuelGen => tick_fuel_gen(host, pos, entity, spec),
        Kind::Cable | Kind::BatteryBuffer | Kind::Hull | Kind::EnergyHatch => {
            tick_eu_node(host, pos, entity, spec)
        }
        Kind::Diode | Kind::Transformer | Kind::ItemHatch | Kind::Multiblock
        | Kind::SteamProcessor | Kind::EuProcessor => {}
    }
}

fn tick_boiler(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, _spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    let (mut burn_left, mut burn_max) = burn(entity);
    if burn_left <= 0 {
        if let Some(stack) = entity.items[0].as_mut() {
            let value = solid_fuel(&stack.item);
            if value > 0 {
                burn_left = value;
                burn_max = value;
                stack.count = stack.count.saturating_sub(1);
                if stack.count == 0 {
                    entity.items[0] = None;
                }
            }
        }
    }
    fluids::take_bucket(entity, 0, "minecraft:water_bucket", 0, 2, WATER, STEAM_CAP);
    fluids::absorb_water_block(host, pos, entity, 0, 2, STEAM_CAP, 50);
    fluids::pull_from_neighbours(host, pos, entity, 0, 2, WATER, STEAM_CAP, 250);
    let mut working = false;
    if burn_left > 0 && fluids::amount(entity, 0, WATER) > 0 {
        burn_left -= 1;
        let _ = fluids::drain(entity, 0, 2, WATER, 1);
        let rate = if entity.id.contains("boiler_hp") {
            HP_BOILER_STEAM_PER_TICK
        } else {
            BOILER_STEAM_PER_TICK
        };
        let _ = fluids::fill(entity, 1, 2, STEAM, rate, STEAM_CAP);
        working = true;
    }
    set_burn(entity, burn_left, burn_max);
    let (b, bm) = burn(entity);
    sync_data(entity, b, bm.max(1), fluids::amount(entity, 1, STEAM), STEAM_CAP);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_turbine(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    fluids::pull_from_neighbours(host, pos, entity, 0, 1, STEAM, STEAM_CAP, 500);
    let mut working = false;
    let have = fluids::amount(entity, 0, STEAM);
    let cap = spec.gauge_cap();
    let eu_out = spec.voltage.max(TURBINE_EU_PER_TICK);
    let steam_need = TURBINE_STEAM_PER_TICK.max(eu_out / 8);
    if have >= steam_need && eu(entity) + eu_out <= cap {
        let _ = fluids::drain(entity, 0, 1, STEAM, steam_need);
        set_eu(entity, eu(entity) + eu_out, cap);
        set_packet_voltage(entity, spec.voltage);
        working = true;
    }
    transfer_eu_out(host, pos, entity, spec);
    sync_data(
        entity,
        if working { 1 } else { 0 },
        1,
        eu(entity),
        cap,
    );
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_fuel_gen(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    let gas = entity.id.contains("gas_turbine");
    if gas {
        take_cell(entity, BIOGAS);
        fluids::pull_from_neighbours(host, pos, entity, 0, 1, BIOGAS, STEAM_CAP, 250);
    } else {
        fluids::take_bucket(entity, 0, "minecraft:lava_bucket", 0, 1, LAVA, STEAM_CAP);
        fluids::pull_from_neighbours(host, pos, entity, 0, 1, LAVA, STEAM_CAP, 250);
        fluids::pull_from_neighbours(host, pos, entity, 0, 1, DIESEL, STEAM_CAP, 250);
    }
    let fuel = if gas { BIOGAS } else if fluids::amount(entity, 0, LAVA) > 0 {
        LAVA
    } else {
        DIESEL
    };
    let mut working = false;
    let cap = spec.gauge_cap();
    let eu_out = spec.voltage.max(FUEL_EU_PER_TICK);
    if fluids::amount(entity, 0, fuel) > 0 && eu(entity) + eu_out <= cap {
        let _ = fluids::drain(entity, 0, 1, fuel, 1);
        set_eu(entity, eu(entity) + eu_out, cap);
        set_packet_voltage(entity, spec.voltage);
        working = true;
    }
    transfer_eu_out(host, pos, entity, spec);
    let stored = fluids::amount(entity, 0, fuel);
    sync_data(entity, stored, STEAM_CAP, eu(entity), cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn take_cell(entity: &mut ModBlockEntity, fluid: &str) {
    let Some(stack) = entity.items.first().and_then(|s| s.as_ref()) else {
        return;
    };
    if stack.item.as_ref() != "greglite:biogas_cell" || stack.count == 0 {
        return;
    }
    if STEAM_CAP - fluids::amount(entity, 0, fluid) < 1000 {
        return;
    }
    let _ = fluids::fill(entity, 0, 1, fluid, 1000, STEAM_CAP);
    if let Some(stack) = entity.items[0].as_mut() {
        stack.count = stack.count.saturating_sub(1);
        if stack.count == 0 {
            entity.items[0] = None;
        }
    }
}

fn battery_item(voltage: i32) -> String {
    let tier = match voltage {
        8 => "ulv",
        32 => "lv",
        128 => "mv",
        512 => "hv",
        2_048 => "ev",
        8_192 => "iv",
        32_768 => "luv",
        131_072 => "zpm",
        524_288 => "uv",
        _ => "lv",
    };
    format!("greglite:{tier}_battery")
}

fn battery_charge(entity: &ModBlockEntity, slot: usize) -> i32 {
    match entity.nbt.get(&format!("Bat{slot}").into()) {
        Some(horizon_client::mod_api::Tag::Int(v)) => (*v).max(0),
        _ => 0,
    }
}

fn set_battery_charge(entity: &mut ModBlockEntity, slot: usize, value: i32) {
    entity.nbt.insert(
        format!("Bat{slot}").into(),
        horizon_client::mod_api::Tag::Int(value.max(0)),
    );
}

fn balance_batteries(entity: &mut ModBlockEntity, spec: &Spec) {
    let want = battery_item(spec.voltage);
    let each = eu_rules::battery_capacity(spec.voltage).max(1);
    let cap = spec.gauge_cap();
    for slot in 0..4 {
        let present = entity
            .items
            .get(slot)
            .and_then(|s| s.as_ref())
            .is_some_and(|stack| stack.item.as_ref() == want);
        if !present {
            set_battery_charge(entity, slot, 0);
            continue;
        }
        let mut charge = battery_charge(entity, slot).min(each);
        if eu(entity) < spec.voltage && charge > 0 {
            let room = cap - eu(entity);
            let move_amt = charge.min(room).min(spec.voltage).max(0);
            if move_amt > 0 {
                charge -= move_amt;
                set_eu(entity, eu(entity) + move_amt, cap);
                set_packet_voltage(entity, spec.voltage);
            }
        }
        set_battery_charge(entity, slot, charge);
    }
}

fn charge_batteries(entity: &mut ModBlockEntity, spec: &Spec) {
    let want = battery_item(spec.voltage);
    let each = eu_rules::battery_capacity(spec.voltage).max(1);
    let cap = spec.gauge_cap();
    for slot in 0..4 {
        let present = entity
            .items
            .get(slot)
            .and_then(|s| s.as_ref())
            .is_some_and(|stack| stack.item.as_ref() == want);
        if !present {
            continue;
        }
        let mut charge = battery_charge(entity, slot).min(each);
        let room = each - charge;
        let spare = eu(entity).saturating_sub(spec.voltage);
        let move_amt = room.min(spare).max(0);
        if move_amt > 0 {
            charge += move_amt;
            set_eu(entity, eu(entity) - move_amt, cap);
        }
        set_battery_charge(entity, slot, charge);
    }
}

fn tick_eu_node(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if spec.kind == Kind::BatteryBuffer && entity.items.len() < 4 {
        entity.items.resize(4, None);
    }
    if spec.kind == Kind::BatteryBuffer {
        balance_batteries(entity, spec);
    }
    if spec.kind != Kind::EnergyHatch {
        transfer_eu_out(host, pos, entity, spec);
    }
    if spec.kind == Kind::BatteryBuffer {
        charge_batteries(entity, spec);
    }
    let cap = spec.gauge_cap();
    sync_data(entity, eu(entity), cap, eu(entity), cap);
}
