//! Per-player survival state (thirst, nutrients, calendar cache).

use std::collections::HashMap;
use std::sync::Mutex;

pub const THIRST_MAX: i32 = 100;
pub const THIRST_DRAIN_EVERY: u32 = 80; // ticks ≈ 4s

#[derive(Clone, Debug)]
pub struct PlayerState {
    pub thirst: i32,
    pub ticks: u32,
    pub grain: i32,
    pub fruit: i32,
    pub veg: i32,
    pub protein: i32,
    pub dairy: i32,
    pub last_season: u8,
    pub last_temp: f32,
    pub last_rain: f32,
    pub pos: [i32; 3],
}

impl Default for PlayerState {
    fn default() -> Self {
        Self {
            thirst: THIRST_MAX,
            ticks: 0,
            grain: 50,
            fruit: 50,
            veg: 50,
            protein: 50,
            dairy: 50,
            last_season: 0,
            last_temp: 15.0,
            last_rain: 300.0,
            pos: [0, 64, 0],
        }
    }
}

static PLAYERS: Mutex<Option<HashMap<u128, PlayerState>>> = Mutex::new(None);

fn map() -> std::sync::MutexGuard<'static, Option<HashMap<u128, PlayerState>>> {
    PLAYERS.lock().unwrap_or_else(|e| e.into_inner())
}

pub fn with_player<R>(uuid: u128, f: impl FnOnce(&mut PlayerState) -> R) -> R {
    let mut guard = map();
    let store = guard.get_or_insert_with(HashMap::new);
    let state = store.entry(uuid).or_default();
    f(state)
}

pub fn get(uuid: u128) -> PlayerState {
    with_player(uuid, |s| s.clone())
}
