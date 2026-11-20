//! Machine registry. Spec list is generated into `specs.inc.rs`.

use horizon_client::mod_api::ModContainer;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Generator,
    Solar,
    Processor,
    Loader,
    Distributor,
    Storage,
    Vacuum,
    Marker,
}

#[derive(Clone, Copy, Debug)]
pub struct Spec {
    pub id: &'static str,
    pub kind: Kind,
    pub fuel: bool,
    pub inputs: usize,
    pub output: Option<usize>,
    pub recipe_type: Option<&'static str>,
    pub fe_cap: i32,
    pub fe_rate: i32,
}

const SPECS: &[Spec] = &include!("specs.inc.rs");

pub fn find(block: &str) -> Option<Spec> {
    SPECS.iter().copied().find(|spec| spec.id == block)
}

pub fn is_ours(block: &str) -> bool {
    find(block).is_some() || block.starts_with("adastra:")
}

pub fn fe_ok(spec: &Spec) -> bool {
    matches!(
        spec.kind,
        Kind::Generator | Kind::Solar | Kind::Processor | Kind::Loader | Kind::Distributor
    )
}

impl Spec {
    pub fn slots(&self) -> usize {
        match self.kind {
            Kind::Storage => self.inputs,
            Kind::Generator => 1,
            Kind::Distributor => 1,
            Kind::Solar | Kind::Vacuum | Kind::Marker => 0,
            Kind::Processor | Kind::Loader => self.output.unwrap_or(self.inputs) + 1,
        }
    }

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
            None => Vec::new(),
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
