//! Per-player thirst and five nutrients. Memory only; a relog resets them.

use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Clone, Debug)]
pub struct PlayerState {
    pub thirst: f32,
    pub ticks: u64,
    pub grain: f32,
    pub fruit: f32,
    pub veg: f32,
    pub protein: f32,
    pub dairy: f32,
    pub last_hud: u64,
}

impl Default for PlayerState {
    fn default() -> Self {
        Self {
            thirst: 1.0,
            ticks: 0,
            grain: 0.5,
            fruit: 0.5,
            veg: 0.5,
            protein: 0.5,
            dairy: 0.5,
            last_hud: 0,
        }
    }
}

static STATES: Mutex<Option<HashMap<u128, PlayerState>>> = Mutex::new(None);

fn with_mut<R>(uuid: u128, f: impl FnOnce(&mut PlayerState) -> R) -> R {
    let mut guard = STATES.lock().unwrap_or_else(|err| err.into_inner());
    let map = guard.get_or_insert_with(HashMap::new);
    f(map.entry(uuid).or_default())
}

/// Drain thirst and nutrients. `refresh` is true every 40 ticks.
pub fn tick(uuid: u128) -> (PlayerState, bool) {
    with_mut(uuid, |st| {
        st.ticks = st.ticks.saturating_add(1);
        st.thirst = (st.thirst - (1.0 / 24_000.0)).clamp(0.0, 1.0);
        for nutrient in [
            &mut st.grain,
            &mut st.fruit,
            &mut st.veg,
            &mut st.protein,
            &mut st.dairy,
        ] {
            *nutrient = (*nutrient - (1.0 / 48_000.0)).clamp(0.0, 1.0);
        }
        let refresh = st.ticks.saturating_sub(st.last_hud) >= 40;
        if refresh {
            st.last_hud = st.ticks;
        }
        (st.clone(), refresh)
    })
}

pub fn drink(uuid: u128, amount: f32) -> PlayerState {
    with_mut(uuid, |st| {
        st.thirst = (st.thirst + amount).clamp(0.0, 1.0);
        st.clone()
    })
}

pub fn eat(uuid: u128, grain: f32, fruit: f32, veg: f32, protein: f32, dairy: f32) -> PlayerState {
    with_mut(uuid, |st| {
        st.grain = (st.grain + grain * 0.25).clamp(0.0, 1.0);
        st.fruit = (st.fruit + fruit * 0.25).clamp(0.0, 1.0);
        st.veg = (st.veg + veg * 0.25).clamp(0.0, 1.0);
        st.protein = (st.protein + protein * 0.25).clamp(0.0, 1.0);
        st.dairy = (st.dairy + dairy * 0.25).clamp(0.0, 1.0);
        st.clone()
    })
}

pub fn nutrition_line(st: &PlayerState) -> String {
    format!(
        "G{:.0} F{:.0} V{:.0} P{:.0} D{:.0}",
        st.grain * 100.0,
        st.fruit * 100.0,
        st.veg * 100.0,
        st.protein * 100.0,
        st.dairy * 100.0,
    )
}
