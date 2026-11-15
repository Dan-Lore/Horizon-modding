//! Machine / workstation registry (table-driven).

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
    LogPile,
    Support,
    BlastFurnace,
    Powderkeg,
}

#[derive(Clone, Copy, Debug)]
pub struct Spec {
    pub id: &'static str,
    pub menu: &'static str,
    pub kind: Kind,
    pub inputs: usize,
    pub output: Option<usize>,
}

const SPECS: &[Spec] = &[
    Spec { id: "tfc:firepit", menu: "tfc:firepit", kind: Kind::Firepit, inputs: 1, output: Some(1) },
    Spec { id: "tfc:pit_kiln", menu: "tfc:pit_kiln", kind: Kind::PitKiln, inputs: 1, output: Some(1) },
    Spec { id: "tfc:charcoal_forge", menu: "tfc:charcoal_forge", kind: Kind::Forge, inputs: 1, output: Some(1) },
    Spec { id: "tfc:bloomery", menu: "tfc:bloomery", kind: Kind::Bloomery, inputs: 2, output: Some(2) },
    Spec { id: "tfc:anvil_stone", menu: "tfc:anvil_stone", kind: Kind::Anvil, inputs: 1, output: Some(1) },
    Spec { id: "tfc:anvil_bronze", menu: "tfc:anvil_bronze", kind: Kind::Anvil, inputs: 1, output: Some(1) },
    Spec { id: "tfc:quern", menu: "tfc:quern", kind: Kind::Quern, inputs: 1, output: Some(1) },
    Spec { id: "tfc:barrel", menu: "tfc:barrel", kind: Kind::Barrel, inputs: 1, output: Some(1) },
    Spec { id: "tfc:sluice", menu: "tfc:sluice", kind: Kind::Sluice, inputs: 1, output: Some(1) },
    Spec { id: "tfc:log_pile", menu: "tfc:log_pile", kind: Kind::LogPile, inputs: 0, output: None },
    Spec { id: "tfc:support_beam", menu: "tfc:support_beam", kind: Kind::Support, inputs: 0, output: None },
    Spec { id: "tfc:blast_furnace", menu: "tfc:blast_furnace", kind: Kind::BlastFurnace, inputs: 2, output: Some(2) },
    Spec { id: "tfc:powderkeg", menu: "tfc:powderkeg", kind: Kind::Powderkeg, inputs: 0, output: None },
];

pub fn find(block: &str) -> Option<&'static Spec> {
    SPECS.iter().find(|s| s.id == block)
}

pub fn is_ours(block: &str) -> bool {
    find(block).is_some()
}

impl Spec {
    pub fn slots(self) -> usize {
        match self.output {
            Some(out) => out + 1,
            None => self.inputs.max(1),
        }
    }

    pub fn container(self) -> Option<ModContainer> {
        match self.kind {
            Kind::LogPile | Kind::Support | Kind::Powderkeg => None,
            _ => {
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
                for &i in &inputs {
                    faces[1].push(i);
                    faces[2].push(i);
                }
                for &o in &outputs {
                    faces[0].push(o);
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
    }
}
