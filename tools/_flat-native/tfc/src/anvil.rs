//! Hammer steps. The anvil does not finish a recipe on its own.

use crate::recipes::{self, can_output, merge_output};
use horizon_client::mod_api::serde_json::{from_str, Value};
use horizon_client::mod_api::{ModBlockEntity, Tag};
use std::sync::OnceLock;

struct Plan {
    input: String,
    output: String,
    steps: Vec<String>,
}

fn plans() -> &'static Vec<Plan> {
    static PLANS: OnceLock<Vec<Plan>> = OnceLock::new();
    PLANS.get_or_init(|| {
        let value: Value = from_str(include_str!("../tables/anvil.json")).expect("anvil");
        value
            .as_array()
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Plan {
                            input: row.get("input")?.as_str()?.to_owned(),
                            output: row.get("output")?.as_str()?.to_owned(),
                            steps: row
                                .get("steps")?
                                .as_array()?
                                .iter()
                                .filter_map(|step| step.as_str().map(str::to_owned))
                                .collect(),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default()
    })
}

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(value)) => *value,
        _ => 0,
    }
}

fn nbt_set(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

fn stamp(id: &str) -> i32 {
    let mut hash = 0i32;
    for byte in id.bytes() {
        hash = hash.wrapping_mul(31).wrapping_add(byte as i32);
    }
    hash
}

fn ensure(entity: &mut ModBlockEntity) {
    if entity.items.len() < 2 {
        entity.items.resize(2, None);
    }
}

fn matching(item: &str) -> Vec<usize> {
    plans()
        .iter()
        .enumerate()
        .filter_map(|(index, plan)| (plan.input == item).then_some(index))
        .collect()
}

fn publish(entity: &mut ModBlockEntity, step: i32, len: i32, plan: i32, count: i32) {
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = step;
    entity.data[1] = len.max(1);
    entity.data[2] = plan;
    entity.data[3] = count.max(1);
}

/// Screen bar: steps finished / steps in the current plan.
pub fn gauge(entity: &mut ModBlockEntity) {
    ensure(entity);
    let Some(item) = entity.items[0].as_ref().map(|stack| stack.item.as_ref().to_owned()) else {
        publish(entity, 0, 1, 0, 1);
        return;
    };
    let found = matching(&item);
    if found.is_empty() {
        publish(entity, 0, 1, 0, 1);
        return;
    }
    let plan = nbt_i32(entity, "Plan").clamp(0, found.len() as i32 - 1);
    let steps = plans()[found[plan as usize]].steps.len() as i32;
    let step = nbt_i32(entity, "Step").clamp(0, steps);
    publish(entity, step, steps, plan, found.len() as i32);
}

pub fn strike(entity: &mut ModBlockEntity, sneaking: bool) -> String {
    ensure(entity);
    let Some(item) = entity.items[0].as_ref().map(|stack| stack.item.as_ref().to_owned()) else {
        return "TFC: put a workable piece on the anvil.".to_owned();
    };
    let mark = stamp(&item);
    if nbt_i32(entity, "InputSig") != mark {
        nbt_set(entity, "InputSig", mark);
        nbt_set(entity, "Plan", 0);
        nbt_set(entity, "Step", 0);
    }
    let found = matching(&item);
    if found.is_empty() {
        return "TFC: the anvil has no plan for that piece.".to_owned();
    }
    let mut plan_index = nbt_i32(entity, "Plan");
    if plan_index < 0 || plan_index as usize >= found.len() {
        plan_index = 0;
    }
    if sneaking {
        plan_index = (plan_index + 1) % found.len() as i32;
        nbt_set(entity, "Plan", plan_index);
        nbt_set(entity, "Step", 0);
        let plan = &plans()[found[plan_index as usize]];
        publish(entity, 0, plan.steps.len() as i32, plan_index, found.len() as i32);
        return format!(
            "TFC: anvil plan {} ({} of {}). Steps: {}.",
            plan.output,
            plan_index + 1,
            found.len(),
            plan.steps.join(", ")
        );
    }
    let plan = &plans()[found[plan_index as usize]];
    let mut step = nbt_i32(entity, "Step");
    if step < 0 || step as usize > plan.steps.len() {
        step = 0;
    }
    if step as usize >= plan.steps.len() {
        step = 0;
    }
    let name = plan.steps[step as usize].clone();
    let next = step + 1;
    if next as usize >= plan.steps.len() {
        let output = recipes::stack(&plan.output, 1);
        if !entity.items.get(1).is_some_and(|slot| can_output(slot, &output)) {
            return "TFC: anvil output is full.".to_owned();
        }
        let slot = &mut entity.items[0];
        if let Some(stack) = slot {
            if stack.count <= 1 {
                *slot = None;
            } else {
                stack.count -= 1;
            }
        }
        merge_output(&mut entity.items[1], &output);
        nbt_set(entity, "Step", 0);
        publish(entity, 0, plan.steps.len() as i32, plan_index, found.len() as i32);
        format!("TFC: anvil {name} finished {}.", plan.output)
    } else {
        nbt_set(entity, "Step", next);
        publish(entity, next, plan.steps.len() as i32, plan_index, found.len() as i32);
        format!(
            "TFC: anvil {name} ({next}/{}) toward {}.",
            plan.steps.len(),
            plan.output
        )
    }
}
