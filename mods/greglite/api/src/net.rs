//! EU packets: one amp is `voltage` EU. Machines accept only their own voltage.
//! Cables, diodes, and buffers accept a packet at or below their rating.
//! Leftover EU in a cable decays by the material loss after the push.

use crate::energy::{eu, packet_voltage, set_eu, set_packet_voltage};
use crate::eu_rules::{self, EuSink};
use crate::registry::{self, Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

const OFFSETS: [[i32; 3]; 6] = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
];

fn sink_of(spec: &Spec) -> EuSink {
    match spec.kind {
        Kind::Cable => EuSink::Cable,
        Kind::Diode => EuSink::Diode,
        Kind::EuProcessor | Kind::Multiblock | Kind::SteamTurbine | Kind::FuelGen => EuSink::Machine,
        Kind::BatteryBuffer | Kind::Transformer | Kind::Hull | Kind::Boiler | Kind::SteamProcessor
        | Kind::ItemHatch => EuSink::Buffer,
        Kind::EnergyHatch => EuSink::Hatch,
    }
}

fn held_packet(other: &ModBlockEntity, spec: &Spec) -> i32 {
    let stored = packet_voltage(other);
    if stored > 0 { stored } else { spec.voltage }
}

fn give_amp(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    spec: &Spec,
    packet: i32,
    only: Option<[i32; 3]>,
) -> bool {
    if packet <= 0 || eu(entity) < packet {
        return false;
    }
    for offset in OFFSETS {
        if only.is_some_and(|want| want != offset) {
            continue;
        }
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        let mut gave = false;
        let _ = host.change_mod_block_entity(npos, &mut |other| {
            let Some(dest) = registry::find(&other.id) else {
                return;
            };
            if !dest.eu_ok {
                return;
            }
            if !eu_rules::accepts(sink_of(&dest), dest.voltage, packet) {
                return;
            }
            let cap = dest.gauge_cap();
            let theirs = eu(other);
            if theirs.saturating_add(packet) > cap {
                return;
            }
            set_eu(other, theirs + packet, cap);
            set_packet_voltage(other, packet);
            gave = true;
        });
        if gave {
            set_eu(entity, eu(entity) - packet, spec.gauge_cap());
            return true;
        }
    }
    false
}

fn push_amps(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    spec: &Spec,
    packet: i32,
    amps: i32,
    only: Option<[i32; 3]>,
) {
    let mut left = amps.max(0);
    while left > 0 && give_amp(host, pos, entity, spec, packet, only) {
        left -= 1;
    }
}

pub fn transfer_eu_out(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let stored = packet_voltage(entity);
    let packet = if stored > 0 { stored } else { spec.voltage.max(0) };
    if packet <= 0 {
        return;
    }
    push_amps(host, pos, entity, spec, packet, spec.amps.max(1), None);
    if spec.kind == Kind::Cable && spec.loss > 0 {
        let have = eu(entity);
        if have > 0 {
            set_eu(entity, have - spec.loss.min(have), spec.gauge_cap());
        }
    }
}

/// Machines receive EU when a neighbour pushes. Pulling as well would double an amp.
pub fn transfer_eu_in(
    _host: &mut dyn Host,
    _pos: [i32; 3],
    _entity: &mut ModBlockEntity,
    _spec: &Spec,
) {
}

fn facing_name(host: &mut dyn Host, pos: [i32; 3]) -> String {
    let dim = host.dimension();
    let Some(level) = host.level(dim) else {
        return "north".to_owned();
    };
    level
        .block_property(host, pos, "facing")
        .unwrap_or_else(|| "north".to_owned())
}

fn take_amp_from(host: &mut dyn Host, npos: [i32; 3], packet: i32) -> bool {
    if packet <= 0 {
        return false;
    }
    let mut took = false;
    let _ = host.change_mod_block_entity(npos, &mut |other| {
        let Some(spec) = registry::find(&other.id) else {
            return;
        };
        if !spec.eu_ok || held_packet(other, &spec) != packet {
            return;
        }
        if matches!(
            spec.kind,
            Kind::EuProcessor
                | Kind::SteamProcessor
                | Kind::Multiblock
                | Kind::ItemHatch
                | Kind::Transformer
        ) {
            return;
        }
        let have = eu(other);
        if have < packet {
            return;
        }
        set_eu(other, have - packet, spec.gauge_cap());
        took = true;
    });
    took
}

pub fn tick_diode(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let facing = facing_name(host, pos);
    let out_off = eu_rules::facing_offset(&facing);
    let in_off = eu_rules::opposite_offset(out_off);
    let packet = spec.voltage;
    if eu(entity) < packet {
        let npos = [pos[0] + in_off[0], pos[1] + in_off[1], pos[2] + in_off[2]];
        if take_amp_from(host, npos, packet) {
            set_eu(entity, eu(entity) + packet, spec.gauge_cap());
            set_packet_voltage(entity, packet);
        }
    }
    push_amps(host, pos, entity, spec, packet, 1, Some(out_off));
}

pub fn tick_transformer(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let low = spec.voltage.max(1);
    let high = eu_rules::tier_up(low);
    let cap = spec.gauge_cap().max(high);
    // Hold at most one high packet of low-side energy, then emit 1 A high.
    let mut pulled_low = 0;
    for offset in OFFSETS {
        if pulled_low >= 4 || eu(entity) + low > high {
            break;
        }
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        if take_amp_from(host, npos, low) {
            set_eu(entity, eu(entity) + low, cap);
            set_packet_voltage(entity, low);
            pulled_low += 1;
        }
    }
    if eu(entity) >= high {
        let before = eu(entity);
        push_amps(host, pos, entity, spec, high, 1, None);
        if eu(entity) < before {
            set_packet_voltage(entity, low);
        }
    }
    if pulled_low > 0 {
        return;
    }
    // Step down only on a tick that did not take low-side energy: 1 A high → 4 A low.
    for offset in OFFSETS {
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        if !take_amp_from(host, npos, high) {
            continue;
        }
        set_eu(entity, eu(entity) + high, cap);
        set_packet_voltage(entity, low);
        push_amps(host, pos, entity, spec, low, 4, None);
        break;
    }
}
