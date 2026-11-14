//! Adjacent steam / EU equalisation between Greglite block entities.

use crate::energy::{
    eu, set_eu, set_steam, steam, EU_TRANSFER, STEAM_CAP, STEAM_TRANSFER,
};
use crate::registry::{self, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

const OFFSETS: [[i32; 3]; 6] = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
];

fn push_steam(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    let mut available = steam(entity);
    if available <= 0 {
        return;
    }
    for off in OFFSETS {
        if available <= 0 {
            break;
        }
        let npos = [pos[0] + off[0], pos[1] + off[1], pos[2] + off[2]];
        let mut gave = 0i32;
        let ok = host.change_mod_block_entity(npos, &mut |other| {
            let Some(spec) = registry::find(&other.id) else {
                return;
            };
            if !spec.steam_ok {
                return;
            }
            let theirs = steam(other);
            if theirs >= available {
                return;
            }
            let room = STEAM_CAP - theirs;
            let move_amt = STEAM_TRANSFER.min(room).min(available - theirs).max(0);
            if move_amt <= 0 {
                return;
            }
            set_steam(other, theirs + move_amt);
            gave = move_amt;
        });
        if ok && gave > 0 {
            available -= gave;
            set_steam(entity, available);
        }
    }
}

fn pull_steam(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    let mut room = STEAM_CAP - steam(entity);
    if room <= 0 {
        return;
    }
    for off in OFFSETS {
        if room <= 0 {
            break;
        }
        let npos = [pos[0] + off[0], pos[1] + off[1], pos[2] + off[2]];
        let mut took = 0i32;
        let ok = host.change_mod_block_entity(npos, &mut |other| {
            let Some(spec) = registry::find(&other.id) else {
                return;
            };
            if !spec.steam_ok {
                return;
            }
            let theirs = steam(other);
            let move_amt = STEAM_TRANSFER.min(room).min(theirs).max(0);
            if move_amt <= 0 {
                return;
            }
            set_steam(other, theirs - move_amt);
            took = move_amt;
        });
        if ok && took > 0 {
            let next = steam(entity) + took;
            set_steam(entity, next);
            room = STEAM_CAP - next;
        }
    }
}

fn push_eu(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, self_spec: &Spec) {
    let mut available = eu(entity);
    if available <= 0 {
        return;
    }
    let rate = if self_spec.id.contains("cable_4x") {
        self_spec.voltage.max(EU_TRANSFER) * 4
    } else {
        self_spec.voltage.max(EU_TRANSFER)
    };
    for off in OFFSETS {
        if available <= 0 {
            break;
        }
        let npos = [pos[0] + off[0], pos[1] + off[1], pos[2] + off[2]];
        let mut gave = 0i32;
        let ok = host.change_mod_block_entity(npos, &mut |other| {
            let Some(spec) = registry::find(&other.id) else {
                return;
            };
            if !spec.eu_ok {
                return;
            }
            let theirs = eu(other);
            let cap = spec.gauge_cap();
            if theirs >= available || theirs >= cap {
                return;
            }
            let room = cap - theirs;
            let move_amt = rate.min(room).min(available - theirs).max(0);
            if move_amt <= 0 {
                return;
            }
            set_eu(other, theirs + move_amt, cap);
            gave = move_amt;
        });
        if ok && gave > 0 {
            available -= gave;
            set_eu(entity, available, self_spec.gauge_cap());
        }
    }
}

fn pull_eu(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, self_spec: &Spec) {
    let cap = self_spec.gauge_cap();
    let mut room = cap - eu(entity);
    if room <= 0 {
        return;
    }
    for off in OFFSETS {
        if room <= 0 {
            break;
        }
        let npos = [pos[0] + off[0], pos[1] + off[1], pos[2] + off[2]];
        let mut took = 0i32;
        let ok = host.change_mod_block_entity(npos, &mut |other| {
            let Some(spec) = registry::find(&other.id) else {
                return;
            };
            if !spec.eu_ok {
                return;
            }
            let theirs = eu(other);
            let move_amt = EU_TRANSFER.min(room).min(theirs).max(0);
            if move_amt <= 0 {
                return;
            }
            set_eu(other, theirs - move_amt, spec.gauge_cap());
            took = move_amt;
        });
        if ok && took > 0 {
            let next = eu(entity) + took;
            set_eu(entity, next, cap);
            room = cap - next;
        }
    }
}

pub fn transfer_steam_out(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    push_steam(host, pos, entity);
}

pub fn transfer_steam_in(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    pull_steam(host, pos, entity);
}

pub fn transfer_eu_out(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    push_eu(host, pos, entity, spec);
}

pub fn transfer_eu_in(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    pull_eu(host, pos, entity, spec);
}
