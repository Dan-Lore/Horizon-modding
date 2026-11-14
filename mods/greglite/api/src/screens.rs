//! Machine screens: Horizon draws the vanilla-style panel + slot frames;
//! we only overlay EU/steam gauge and progress.

use crate::registry::{self, Kind};
use horizon_client::mod_api::{Host, NativeScreen, ScreenDrawEvent, ScreenEvent};

fn base_screen(slots: Vec<Option<[f32; 2]>>) -> NativeScreen {
    NativeScreen {
        width: 176.0,
        height: 166.0,
        slots,
        inventory_y: 84.0,
        inventory_x: 8.0,
        // Let Horizon draw title/"Inventory" and the proper slot chrome.
        own_labels: false,
        own_background: false,
    }
}

pub fn layout(event: &ScreenEvent<'_>) -> Option<NativeScreen> {
    let spec = registry::find(event.block)?;
    match spec.kind {
        Kind::Cable | Kind::Hull => None,
        Kind::Multiblock => Some(base_screen(vec![Some([53.0, 35.0]), Some([116.0, 35.0])])),
        Kind::Boiler | Kind::FuelGen | Kind::SteamTurbine => {
            Some(base_screen(vec![Some([80.0, 53.0])]))
        }
        Kind::BatteryBuffer => Some(base_screen(vec![
            Some([53.0, 35.0]),
            Some([71.0, 35.0]),
            Some([89.0, 35.0]),
            Some([107.0, 35.0]),
        ])),
        Kind::SteamProcessor | Kind::EuProcessor => {
            if spec.inputs >= 2 {
                Some(base_screen(vec![
                    Some([53.0, 25.0]),
                    Some([71.0, 25.0]),
                    Some([116.0, 35.0]),
                ]))
            } else {
                Some(base_screen(vec![Some([53.0, 35.0]), Some([116.0, 35.0])]))
            }
        }
    }
}

pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    let Some(spec) = registry::find(event.block) else {
        return;
    };
    if matches!(spec.kind, Kind::Cable | Kind::Hull) {
        return;
    }
    let ox = event.origin[0];
    let oy = event.origin[1];

    let data = event.data;
    let (primary, primary_max, energy, cap) = if data.len() >= 4 {
        (
            data[0].max(0),
            data[1].max(1),
            data[2].max(0),
            data[3].max(1),
        )
    } else if data.len() >= 3 {
        (data[0].max(0), data[1].max(1), data[2].max(0), 1)
    } else {
        (0, 1, 0, 1)
    };

    // EU / steam gauge (left)
    let gauge_x = ox + 10.0;
    let gauge_y = oy + 16.0;
    let gauge_w = 8.0;
    let gauge_h = 54.0;
    host.fill(event.batch, [gauge_x, gauge_y, gauge_w, gauge_h], 0xFF202020);
    let filled = (energy as f32 / cap as f32).clamp(0.0, 1.0) * gauge_h;
    let color = if spec.eu_ok && !matches!(spec.kind, Kind::Boiler | Kind::SteamProcessor) {
        0xFFE8C040
    } else {
        0xFFD0E8FF
    };
    if filled > 0.0 {
        host.fill(
            event.batch,
            [gauge_x, gauge_y + (gauge_h - filled), gauge_w, filled],
            color,
        );
    }

    match spec.kind {
        Kind::Boiler | Kind::FuelGen => {
            let _ = host.sprite(
                event.batch,
                "greglite:gui/progress_bar_boiler_fuel_bronze",
                [0.0, 0.0, 18.0, 18.0],
                [ox + 80.0, oy + 35.0, 18.0, 18.0],
            );
            let frac = (primary as f32 / primary_max as f32).clamp(0.0, 1.0);
            let h = 18.0 * frac;
            if h > 0.0 {
                let _ = host.sprite(
                    event.batch,
                    "greglite:gui/progress_bar_boiler_fuel_bronze",
                    [0.0, 18.0 - h, 18.0, h],
                    [ox + 80.0, oy + 35.0 + (18.0 - h), 18.0, h],
                );
            }
        }
        Kind::SteamProcessor | Kind::EuProcessor | Kind::SteamTurbine | Kind::Multiblock => {
            let _ = host.sprite(
                event.batch,
                "greglite:gui/progress_bar_arrow_bronze",
                [0.0, 0.0, 20.0, 16.0],
                [ox + 79.0, oy + 34.0, 20.0, 16.0],
            );
            let frac = (primary as f32 / primary_max as f32).clamp(0.0, 1.0);
            let w = 20.0 * frac;
            if w > 0.0 {
                let _ = host.sprite(
                    event.batch,
                    "greglite:gui/progress_bar_arrow_bronze",
                    [0.0, 0.0, w, 16.0],
                    [ox + 79.0, oy + 34.0, w, 16.0],
                );
            }
        }
        _ => {}
    }
}
