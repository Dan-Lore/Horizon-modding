//! Machine GUIs.

use crate::registry::{self, Kind};
use horizon_client::mod_api::{Host, NativeScreen, ScreenDrawEvent, ScreenEvent};

fn base(slots: Vec<Option<[f32; 2]>>) -> NativeScreen {
    NativeScreen {
        width: 176.0,
        height: 166.0,
        slots,
        inventory_y: 84.0,
        inventory_x: 8.0,
        own_labels: false,
        own_background: false,
    }
}

pub fn layout(event: &ScreenEvent<'_>) -> Option<NativeScreen> {
    let spec = registry::find(event.block)?;
    match spec.kind {
        Kind::Powderkeg => None,
        Kind::Firepit | Kind::PitKiln | Kind::Quern | Kind::Barrel | Kind::Sluice | Kind::Anvil => {
            Some(base(vec![Some([53.0, 35.0]), Some([116.0, 35.0])]))
        }
        Kind::Forge | Kind::Bloomery | Kind::BlastFurnace | Kind::Crucible => Some(base(vec![
            Some([53.0, 25.0]),
            Some([71.0, 25.0]),
            Some([116.0, 35.0]),
        ])),
    }
}

pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    if registry::find(event.block).is_none() {
        return;
    }
    let ox = event.origin[0];
    let oy = event.origin[1];
    let data = event.data;
    let (primary, primary_max) = if data.len() >= 2 {
        (data[0].max(0), data[1].max(1))
    } else {
        (0, 1)
    };
    let gauge_x = ox + 10.0;
    let gauge_y = oy + 16.0;
    let gauge_w = 8.0;
    let gauge_h = 54.0;
    host.fills(event.batch, [gauge_x, gauge_y, gauge_w, gauge_h], 0xFF202020);
    let filled = (primary as f32 / primary_max as f32).clamp(0.0, 1.0) * gauge_h;
    host.fills(
        event.batch,
        [gauge_x, gauge_y + gauge_h - filled, gauge_w, filled],
        0xFFE07020,
    );
}
