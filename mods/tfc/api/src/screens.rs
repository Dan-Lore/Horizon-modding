//! Simple workstation screens.

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
        Kind::LogPile | Kind::Support | Kind::Powderkeg => None,
        Kind::Bloomery | Kind::BlastFurnace => Some(base(vec![
            Some([53.0, 25.0]),
            Some([71.0, 25.0]),
            Some([116.0, 35.0]),
        ])),
        _ => Some(base(vec![Some([53.0, 35.0]), Some([116.0, 35.0])])),
    }
}

pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    let Some(spec) = registry::find(event.block) else {
        return;
    };
    if matches!(spec.kind, Kind::LogPile | Kind::Support | Kind::Powderkeg) {
        return;
    }
    let ox = event.origin[0];
    let oy = event.origin[1];
    let (prog, max) = if event.data.len() >= 2 {
        (event.data[0] as f32, event.data[1].max(1) as f32)
    } else {
        (0.0, 1.0)
    };
    let w = 24.0 * (prog / max).clamp(0.0, 1.0);
    host.fill(event.batch, [ox + 79.0, oy + 34.0, 24.0, 17.0], 0xFF303030);
    if w > 0.0 {
        host.fill(event.batch, [ox + 79.0, oy + 34.0, w, 17.0], 0xFFE0A040);
    }
}
