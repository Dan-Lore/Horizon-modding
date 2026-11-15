//! Machine / interactive block registry (table-driven).

use horizon_client::mod_api::ModContainer;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Firepit,
    Forge,
    Bloomery,
    Anvil,
    Quern,
    Barrel,
    PitKiln,
    BlastFurnace,
    Sluice,
}

#[derive(Clone, Copy, Debug)]
pub struct Spec {
    pub id: &'static str,
    pub menu: &'static str,
    pub kind: Kind,
    pub inputs: usize,
    pub output: Option<usize>,
    pub recipe_type: Option<&'static str>,
}

const SPECS: &[Spec] = &[
    Spec {
        id: "tfc:firepit",
        menu: "tfc:firepit",
        kind: Kind::Firepit,
        inputs: 1,
        output: Some(1),
        recipe_type: Some("tfc:firepit"),
    },
    Spec {
        id: "tfc:charcoal_forge",
        menu: "tfc:charcoal_forge",
        kind: Kind::Forge,
        inputs: 2,
        output: Some(2),
        recipe_type: Some("tfc:charcoal_forge"),
    },
    Spec {
        id: "tfc:bloomery",
        menu: "tfc:bloomery",
        kind: Kind::Bloomery,
        inputs: 2,
        output: Some(2),
        recipe_type: Some("tfc:bloomery"),
    },
    Spec {
        id: "tfc:anvil",
        menu: "tfc:anvil",
        kind: Kind::Anvil,
        inputs: 1,
        output: Some(1),
        recipe_type: Some("tfc:anvil"),
    },
    Spec {
        id: "tfc:quern",
        menu: "tfc:quern",
        kind: Kind::Quern,
        inputs: 1,
        output: Some(1),
        recipe_type: Some("tfc:quern"),
    },
    Spec {
        id: "tfc:barrel",
        menu: "tfc:barrel",
        kind: Kind::Barrel,
        inputs: 2,
        output: Some(2),
        recipe_type: Some("tfc:barrel"),
    },
    Spec {
        id: "tfc:pit_kiln",
        menu: "tfc:pit_kiln",
        kind: Kind::PitKiln,
        inputs: 1,
        output: Some(1),
        recipe_type: Some("tfc:pit_kiln"),
    },
    Spec {
        id: "tfc:blast_furnace",
        menu: "tfc:blast_furnace",
        kind: Kind::BlastFurnace,
        inputs: 2,
        output: Some(2),
        recipe_type: Some("tfc:blast_furnace"),
    },
    Spec {
        id: "tfc:sluice",
        menu: "tfc:sluice",
        kind: Kind::Sluice,
        inputs: 1,
        output: Some(1),
        recipe_type: Some("tfc:sluice"),
    },
];

pub fn find(block: &str) -> Option<Spec> {
    SPECS.iter().copied().find(|s| s.id == block)
}

pub fn is_ours(block: &str) -> bool {
    find(block).is_some()
}

impl Spec {
    pub fn slots(&self) -> usize {
        match self.output {
            Some(out) => out + 1,
            None => self.inputs.max(1),
        }
    }

    pub fn container(&self) -> Option<ModContainer> {
        let slots = self.slots();
        let inputs: Vec<usize> = (0..self.inputs).collect();
        let outputs: Vec<usize> = self.output.map(|o| vec![o]).unwrap_or_default();
        let mut faces = [
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
            Vec::new(),
        ];
        for i in 0..self.inputs {
            faces[1].push(i);
            faces[2].push(i);
        }
        if let Some(out) = self.output {
            faces[0].push(out);
        }
        Some(ModContainer {
            slots,
            faces,
            inputs,
            outputs,
            menu: Some(self.menu.to_string()),
        })
    }
}
