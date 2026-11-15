//! Adjacent FE equalisation between Ad Astra machines.

use crate::energy::{fe, set_fe, FE_TRANSFER};
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

pub fn transfer_fe_out(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, self_spec: &Spec) {
    let mut available = fe(entity);
    if available <= 0 {
        return;
    }
    let rate = self_spec.fe_rate.max(FE_TRANSFER);
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
            if !registry::fe_ok(&spec) {
                return;
            }
            let theirs = fe(other);
            let room = spec.fe_cap - theirs;
            let move_amt = rate.min(room).min(available).max(0);
            if move_amt <= 0 {
                return;
            }
            set_fe(other, theirs + move_amt, spec.fe_cap);
            gave = move_amt;
        });
        if ok && gave > 0 {
            available -= gave;
            set_fe(entity, available, self_spec.fe_cap);
        }
    }
}

pub fn transfer_fe_in(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, self_spec: &Spec) {
    let mut room = self_spec.fe_cap - fe(entity);
    if room <= 0 {
        return;
    }
    let rate = self_spec.fe_rate.max(FE_TRANSFER);
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
            if !registry::fe_ok(&spec) {
                return;
            }
            let theirs = fe(other);
            let move_amt = rate.min(room).min(theirs).max(0);
            if move_amt <= 0 {
                return;
            }
            set_fe(other, theirs - move_amt, spec.fe_cap);
            took = move_amt;
        });
        if ok && took > 0 {
            let next = fe(entity) + took;
            set_fe(entity, next, self_spec.fe_cap);
            room = self_spec.fe_cap - next;
        }
    }
}
