//! Boilers, steam turbines, and fuel EU generators.

use crate::energy::{
    burn, eu, set_burn, set_eu, set_steam, steam, sync_data, STEAM_CAP,
};
use crate::net::{transfer_eu_out, transfer_steam_in, transfer_steam_out};
use crate::registry::{Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

const BOILER_STEAM_PER_TICK: i32 = 12;
const HP_BOILER_STEAM_PER_TICK: i32 = 36;
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
        Kind::Cable | Kind::BatteryBuffer | Kind::Hull => tick_eu_node(host, pos, entity, spec),
        Kind::Multiblock | Kind::SteamProcessor | Kind::EuProcessor => {}
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
    let mut working = false;
    if burn_left > 0 {
        burn_left -= 1;
        let rate = if entity.id.contains("boiler_hp") {
            HP_BOILER_STEAM_PER_TICK
        } else {
            BOILER_STEAM_PER_TICK
        };
        set_steam(entity, steam(entity) + rate);
        working = true;
    }
    set_burn(entity, burn_left, burn_max);
    transfer_steam_out(host, pos, entity);
    let (b, bm) = burn(entity);
    sync_data(entity, b, bm.max(1), steam(entity), STEAM_CAP);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_turbine(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    transfer_steam_in(host, pos, entity);
    let mut working = false;
    let have = steam(entity);
    let cap = spec.gauge_cap();
    let eu_out = spec.voltage.max(TURBINE_EU_PER_TICK);
    let steam_need = TURBINE_STEAM_PER_TICK.max(eu_out / 8);
    if have >= steam_need && eu(entity) + eu_out <= cap {
        set_steam(entity, have - steam_need);
        set_eu(entity, eu(entity) + eu_out, cap);
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
    let mut working = false;
    let cap = spec.gauge_cap();
    let eu_out = spec.voltage.max(FUEL_EU_PER_TICK);
    if burn_left > 0 && eu(entity) + eu_out <= cap {
        burn_left -= 1;
        set_eu(entity, eu(entity) + eu_out, cap);
        working = true;
    } else if burn_left > 0 {
        burn_left -= 1;
    }
    set_burn(entity, burn_left, burn_max);
    transfer_eu_out(host, pos, entity, spec);
    let (b, bm) = burn(entity);
    sync_data(entity, b, bm.max(1), eu(entity), cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_eu_node(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if spec.kind == Kind::BatteryBuffer && entity.items.len() < 4 {
        entity.items.resize(4, None);
    }
    // Batteries in buffer slots add virtual capacity boost when present.
    if spec.kind == Kind::BatteryBuffer {
        let batteries = entity
            .items
            .iter()
            .filter(|s| {
                s.as_ref()
                    .map(|st| st.item.as_ref() == "greglite:lv_battery")
                    .unwrap_or(false)
            })
            .count() as i32;
        if batteries > 0 {
            let boost = batteries * 8_000;
            let want = eu(entity).min(spec.gauge_cap() + boost);
            set_eu(entity, want, spec.gauge_cap() + boost);
        }
    }
    transfer_eu_out(host, pos, entity, spec);
    let cap = spec.gauge_cap();
    sync_data(entity, eu(entity), cap, eu(entity), cap);
}
