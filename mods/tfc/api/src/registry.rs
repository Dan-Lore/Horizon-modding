//! Machine and crop registry. The spec list is generated.

use horizon_client::mod_api::ModContainer;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Machine,
    Crop,
    Storage,
}

#[derive(Clone, Copy, Debug)]
pub struct Spec {
    pub id: &'static str,
    pub kind: Kind,
    pub fuel: bool,
    pub inputs: usize,
    pub output: Option<usize>,
    pub recipe_type: Option<&'static str>,
}

const CROP: Spec = Spec {
    id: "tfc:crop",
    kind: Kind::Crop,
    fuel: false,
    inputs: 0,
    output: Some(0),
    recipe_type: None,
};

const SPECS: &[Spec] = &include!("specs.inc.rs");

pub fn find(block: &str) -> Option<Spec> {
    if block.starts_with("tfc:crop_") {
        return Some(CROP);
    }
    SPECS.iter().copied().find(|spec| spec.id == block)
}

pub fn is_ours(block: &str) -> bool {
    find(block).is_some()
}

impl Spec {
    pub fn slots(&self) -> usize {
        match self.output {
            Some(out) => out + 1,
            None => self.inputs,
        }
    }

    /// Hopper faces and the content menu. `block` is the real id (`tfc:crop_wheat`
    /// for the shared crop spec) so the menu file matches.
    pub fn container(&self, block: &str) -> Option<ModContainer> {
        let slots = self.slots();
        if slots == 0 {
            return None;
        }
        let all: Vec<usize> = (0..slots).collect();
        let inputs = match self.output {
            Some(out) => (0..slots).filter(|slot| *slot != out).collect(),
            None => all.clone(),
        };
        let outputs = match self.output {
            Some(out) => vec![out],
            None => all.clone(),
        };
        // AE2 bus contract: Down=extract, Up=insert, sides=both.
        let mut both = inputs.clone();
        both.extend(outputs.iter().copied());
        let faces = [
            outputs.clone(),
            inputs.clone(),
            both.clone(),
            both.clone(),
            both.clone(),
            both,
        ];
        Some(ModContainer {
            slots,
            faces,
            inputs,
            outputs,
            menu: Some(block.to_owned()),
        })
    }
}
