//! Per-player runtime state (session-local until persistent Host storage exists).

use crate::nutrition::Nutrition;
use crate::thirst::Thirst;
use std::collections::HashMap;
use std::sync::Mutex;

pub struct PlayerState {
    pub thirst: Thirst,
    pub nutrition: Nutrition,
    pub ticks: u64,
    pub last_hud_tick: u64,
}

impl PlayerState {
    pub fn new() -> Self {
        Self {
            thirst: Thirst::new(),
            nutrition: Nutrition::new(),
            ticks: 0,
            last_hud_tick: 0,
        }
    }
}

impl Default for PlayerState {
    fn default() -> Self {
        Self::new()
    }
}

static STATES: Mutex<Option<HashMap<u128, PlayerState>>> = Mutex::new(None);

pub fn with_player<R>(uuid: u128, f: impl FnOnce(&mut PlayerState) -> R) -> R {
    let mut guard = STATES.lock().unwrap_or_else(|e| e.into_inner());
    let map = guard.get_or_insert_with(HashMap::new);
    let state = map.entry(uuid).or_insert_with(PlayerState::new);
    f(state)
}
