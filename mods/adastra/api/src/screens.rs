//! Slot layouts and FE / progress gauges.

use crate::registry::{self, Kind, Spec};
use horizon_client::mod_api::{Host, NativeScreen, ScreenDrawEvent, ScreenEvent};

fn positions(spec: Spec) -> Vec<Option<[f32; 2]>> {
    let count = spec.slots();
    if spec.kind == Kind::Storage {
        return (0..count)
            .map(|index| {
                let col = (index % 3) as f32;
                let row = (index / 3) as f32;
                Some([62.0 + col * 18.0, 17.0 + row * 18.0])
            })
            .collect();
    }
    if count == 0 {
        return Vec::new();
    }
    if count == 1 {
        return vec![Some([80.0, 35.0])];
    }
    (0..count)
        .map(|index| {
            let last = spec.output.is_some() && index + 1 == count;
            let x = if last {
                116.0
            } else {
                44.0 + index as f32 * 18.0
            };
            Some([x, 35.0])
        })
        .collect()
}

pub fn layout(event: &ScreenEvent<'_>) -> Option<NativeScreen> {
    let spec = registry::find(event.block)?;
    if spec.slots() == 0 {
        return None;
    }
    Some(NativeScreen {
        width: 176.0,
        height: 166.0,
        slots: positions(spec),
        inventory_y: 84.0,
        inventory_x: 8.0,
        own_labels: false,
        own_background: false,
    })
}

pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    let Some(spec) = registry::find(event.block) else {
        return;
    };
    if spec.kind == Kind::Storage || spec.slots() == 0 {
        return;
    }
    let data = event.data;
    let (primary, primary_max, gauge, cap) = if data.len() >= 4 {
        (data[0].max(0), data[1].max(1), data[2].max(0), data[3].max(1))
    } else {
        (0, 1, 0, 1)
    };
    let ox = event.origin[0];
    let oy = event.origin[1];
    host.fill(event.batch, [ox + 79.0, oy + 34.0, 24.0, 16.0], 0xFF_202020);
    let width = (primary as f32 / primary_max as f32).clamp(0.0, 1.0) * 22.0;
    host.fill(event.batch, [ox + 80.0, oy + 35.0, width, 14.0], 0xFF_40A0E0);
    host.fill(event.batch, [ox + 8.0, oy + 20.0, 10.0, 48.0], 0xFF_202020);
    let filled = (gauge as f32 / cap as f32).clamp(0.0, 1.0) * 46.0;
    host.fill(
        event.batch,
        [ox + 9.0, oy + 67.0 - filled, 8.0, filled],
        0xFF_50C8FF,
    );
}
