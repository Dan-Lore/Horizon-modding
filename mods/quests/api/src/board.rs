//! Quest board block entity — furnace-style submit menu chrome for item tasks.

use horizon_client::mod_api::{ModContainer, NativeScreen, ScreenEvent};

pub const BLOCK: &str = "quests:quest_board";

pub fn is_board(block: &str) -> bool {
    block == BLOCK
}

pub fn container() -> ModContainer {
    ModContainer {
        slots: 3,
        faces: [
            vec![0, 1, 2],
            vec![0, 1, 2],
            vec![0, 1, 2],
            vec![0, 1, 2],
            vec![0, 1, 2],
            vec![0, 1, 2],
        ],
        inputs: vec![0, 1, 2],
        outputs: vec![],
        menu: Some(BLOCK.to_owned()),
    }
}

pub fn layout(event: &ScreenEvent<'_>) -> Option<NativeScreen> {
    if event.block != BLOCK {
        return None;
    }
    Some(NativeScreen {
        width: 176.0,
        height: 166.0,
        slots: vec![
            Some([62.0, 35.0]),
            Some([80.0, 35.0]),
            Some([98.0, 35.0]),
        ],
        inventory_y: 84.0,
        inventory_x: 8.0,
        own_labels: false,
        own_background: false,
    })
}
