//! Block entity registry for TFC machines.

use horizon_client::mod_api::ModContainer;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Firepit,
    PitKiln,
    Forge,
    Bloomery,
    Anvil,
    Quern,
    Barrel,
    Sluice,
    BlastFurnace,
    Crucible,
    Powderkeg,
}

#[derive(Clone, Copy, Debug)]
pub struct Spec {
    pub id: &'static str,
    pub kind: Kind,
    pub inputs: usize,
}

const SPECS: &[Spec] = &[
    Spec {
        id: "tfc:firepit",
        kind: Kind::Firepit,
        inputs: 1,
    },
    Spec {
        id: "tfc:pit_kiln",
        kind: Kind::PitKiln,
        inputs: 1,
    },
    Spec {
        id: "tfc:charcoal_forge",
        kind: Kind::Forge,
        inputs: 2,
    },
    Spec {
        id: "tfc:bloomery",
        kind: Kind::Bloomery,
        inputs: 2,
    },
    Spec {
        id: "tfc:anvil_stone",
        kind: Kind::Anvil,
        inputs: 1,
    },
    Spec {
        id: "tfc:anvil_copper",
        kind: Kind::Anvil,
        inputs: 1,
    },
    Spec {
        id: "tfc:anvil_bronze",
        kind: Kind::Anvil,
        inputs: 1,
    },
    Spec {
        id: "tfc:anvil_wrought_iron",
        kind: Kind::Anvil,
        inputs: 1,
    },
    Spec {
        id: "tfc:quern",
        kind: Kind::Quern,
        inputs: 1,
    },
    Spec {
        id: "tfc:barrel",
        kind: Kind::Barrel,
        inputs: 1,
    },
    Spec {
        id: "tfc:sluice",
        kind: Kind::Sluice,
        inputs: 1,
    },
    Spec {
        id: "tfc:blast_furnace",
        kind: Kind::BlastFurnace,
        inputs: 2,
    },
    Spec {
        id: "tfc:crucible",
        kind: Kind::Crucible,
        inputs: 2,
    },
    Spec {
        id: "tfc:powderkeg",
        kind: Kind::Powderkeg,
        inputs: 0,
    },
];

pub fn is_ours(block: &str) -> bool {
    find(block).is_some()
}

pub fn find(block: &str) -> Option<Spec> {
    SPECS.iter().copied().find(|s| s.id == block)
}

pub fn is_rock(block: &str) -> bool {
    block.starts_with("tfc:rock_")
        && !block.contains("gravel")
        && !block.contains("sand")
        && !block.contains("loose")
}

pub fn is_ore(block: &str) -> bool {
    block.starts_with("tfc:ore_")
}

pub fn is_support(block: &str) -> bool {
    matches!(
        block,
        "tfc:support_horizontal" | "tfc:support_vertical" | "tfc:support_beam"
    )
}

fn simple_container(slots: usize, menu: &str) -> ModContainer {
    let inputs: Vec<usize> = (0..slots.saturating_sub(1)).collect();
    let outputs = if slots > 0 {
        vec![slots - 1]
    } else {
        vec![]
    };
    let mut faces = [
        Vec::new(),
        Vec::new(),
        Vec::new(),
        Vec::new(),
        Vec::new(),
        Vec::new(),
    ];
    for i in &inputs {
        faces[1].push(*i);
        faces[2].push(*i);
    }
    for o in &outputs {
        faces[0].push(*o);
    }
    ModContainer {
        slots,
        faces,
        inputs,
        outputs,
        menu: Some(menu.to_owned()),
    }
}

impl Spec {
    pub fn container(self) -> Option<ModContainer> {
        match self.kind {
            Kind::Powderkeg => None,
            _ => Some(simple_container(self.inputs.max(1) + 1, self.id)),
        }
    }
}
