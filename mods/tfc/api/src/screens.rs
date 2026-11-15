//! Simple machine screens + progress bar overlay.

use crate::registry;
use horizon_client::mod_api::{Host, NativeScreen, ScreenDrawEvent, ScreenEvent};

fn base_screen(slots: Vec<Option<[f32; 2]>>) -> NativeScreen {
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
    if spec.inputs >= 2 {
        Some(base_screen(vec![
            Some([53.0, 35.0]),
            Some([71.0, 35.0]),
            Some([116.0, 35.0]),
        ]))
    } else {
        Some(base_screen(vec![Some([53.0, 35.0]), Some([116.0, 35.0])]))
    }
}

pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    if registry::find(event.block).is_none() {
        return;
    }
    let ox = event.origin[0];
    let oy = event.origin[1];
    let (prog, max) = if event.data.len() >= 2 {
        (event.data[0].max(0), event.data[1].max(1))
    } else {
        (0, 1)
    };
    let bar_x = ox + 76.0;
    let bar_y = oy + 35.0;
    let bar_w = 24.0;
    let bar_h = 16.0;
    host.fill(event.batch, [bar_x, bar_y, bar_w, bar_h], 0xFF303030);
    let frac = (prog as f32 / max as f32).clamp(0.0, 1.0);
    if frac > 0.0 {
        host.fill(
            event.batch,
            [bar_x, bar_y, bar_w * frac, bar_h],
            0xFFE07030,
        );
    }
}
