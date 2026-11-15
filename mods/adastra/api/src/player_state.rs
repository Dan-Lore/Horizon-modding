//! Per-player oxygen, donned suit flags, and rocket launch stub. Memory only.

use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Clone, Debug)]
pub struct PlayerState {
    pub oxygen: f32,
    pub ticks: u64,
    pub last_hud: u64,
    pub helmet: bool,
    pub suit: bool,
    pub pants: bool,
    pub boots: bool,
    pub launch_ticks: i32,
    pub last_vacuum_warn: u64,
}

impl Default for PlayerState {
    fn default() -> Self {
        Self {
            oxygen: 0.0,
            ticks: 0,
            last_hud: 0,
            helmet: false,
            suit: false,
            pants: false,
            boots: false,
            launch_ticks: -1,
            last_vacuum_warn: 0,
        }
    }
}

impl PlayerState {
    pub fn sealed(&self) -> bool {
        self.helmet && self.suit && self.pants && self.boots
    }
}

static STATES: Mutex<Option<HashMap<u128, PlayerState>>> = Mutex::new(None);

fn with_mut<R>(uuid: u128, f: impl FnOnce(&mut PlayerState) -> R) -> R {
    let mut guard = STATES.lock().unwrap_or_else(|err| err.into_inner());
    let map = guard.get_or_insert_with(HashMap::new);
    f(map.entry(uuid).or_default())
}

pub fn tick(uuid: u128) -> (PlayerState, bool) {
    with_mut(uuid, |st| {
        st.ticks = st.ticks.saturating_add(1);
        let refresh = st.ticks.saturating_sub(st.last_hud) >= 40;
        if refresh {
            st.last_hud = st.ticks;
        }
        if st.launch_ticks > 0 {
            st.launch_ticks -= 1;
        }
        (st.clone(), refresh)
    })
}

pub fn refill_oxygen(uuid: u128, amount: f32) -> PlayerState {
    with_mut(uuid, |st| {
        st.oxygen = (st.oxygen + amount).clamp(0.0, 100.0);
        st.clone()
    })
}

pub fn drain_oxygen(uuid: u128, amount: f32) -> PlayerState {
    with_mut(uuid, |st| {
        st.oxygen = (st.oxygen - amount).clamp(0.0, 100.0);
        st.clone()
    })
}

pub fn don_piece(uuid: u128, item: &str) -> Option<&'static str> {
    with_mut(uuid, |st| {
        let msg = match item {
            "adastra:space_helmet" => {
                st.helmet = true;
                Some("Ad Astra: donned space helmet.")
            }
            "adastra:space_suit" => {
                st.suit = true;
                Some("Ad Astra: donned space suit.")
            }
            "adastra:space_pants" => {
                st.pants = true;
                Some("Ad Astra: donned space pants.")
            }
            "adastra:space_boots" => {
                st.boots = true;
                Some("Ad Astra: donned space boots.")
            }
            _ => None,
        };
        msg
    })
}

pub fn start_launch(uuid: u128) -> PlayerState {
    with_mut(uuid, |st| {
        st.launch_ticks = 100;
        st.clone()
    })
}

pub fn launch_phase(uuid: u128) -> i32 {
    with_mut(uuid, |st| st.launch_ticks)
}

pub fn clear_launch(uuid: u128) {
    with_mut(uuid, |st| {
        st.launch_ticks = -1;
    });
}

pub fn should_vacuum_warn(uuid: u128) -> bool {
    with_mut(uuid, |st| {
        let due = st.ticks.saturating_sub(st.last_vacuum_warn) >= 40;
        if due {
            st.last_vacuum_warn = st.ticks;
        }
        due
    })
}

pub fn hud_line(state: &PlayerState, gravity: &str, vacuum: bool, safe: bool) -> String {
    let sealed = if state.sealed() { "suit OK" } else { "suit open" };
    let zone = if safe {
        "O2 bubble"
    } else if vacuum {
        "VACUUM"
    } else {
        "ok"
    };
    format!(
        "Ad Astra O2 {:.0}% | {} | {} | {}",
        state.oxygen, sealed, zone, gravity
    )
}
