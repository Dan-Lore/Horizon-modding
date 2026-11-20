//! Per-team quest progress persisted under world_dir()/horizon-quests/.

use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex};

#[derive(Clone, Debug, Default)]
pub struct TeamProgress {
    pub completed_tasks: HashSet<String>,
    pub completed_quests: HashSet<String>,
    /// quest_id -> set of claimed reward ids for this player
    pub claimed: HashMap<String, HashSet<String>>,
    /// quest_id -> chosen choice index
    pub choices: HashMap<String, i32>,
}

#[derive(Default)]
struct State {
    dir: Option<PathBuf>,
    teams: HashMap<String, TeamProgress>,
    theme: String,
}

static STATE: LazyLock<Mutex<State>> = LazyLock::new(|| {
    Mutex::new(State {
        dir: None,
        teams: HashMap::new(),
        theme: String::new(),
    })
});

fn progress_path(dir: &Path) -> PathBuf {
    dir.join("progress.json")
}

fn theme_path(dir: &Path) -> PathBuf {
    dir.join("theme.txt")
}

pub fn bind(world_dir: PathBuf) {
    let dir = world_dir.join("horizon-quests");
    let _ = fs::create_dir_all(&dir);
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    if state.dir.as_ref() == Some(&dir) {
        return;
    }
    state.dir = Some(dir.clone());
    state.teams.clear();
    if let Ok(theme) = fs::read_to_string(theme_path(&dir)) {
        state.theme = theme.trim().to_owned();
    }
    if state.theme.is_empty() {
        state.theme = "copper".into();
    }
    if let Ok(text) = fs::read_to_string(progress_path(&dir)) {
        // lines: team|task:id / team|quest:id / team|claim:quest:reward / team|choice:quest:idx
        for line in text.lines() {
            let mut parts = line.split('|');
            let Some(team) = parts.next() else {
                continue;
            };
            let Some(kind) = parts.next() else {
                continue;
            };
            let entry = state.teams.entry(team.to_owned()).or_default();
            match kind {
                "task" => {
                    if let Some(id) = parts.next() {
                        entry.completed_tasks.insert(id.to_owned());
                    }
                }
                "quest" => {
                    if let Some(id) = parts.next() {
                        entry.completed_quests.insert(id.to_owned());
                    }
                }
                "claim" => {
                    if let (Some(q), Some(r)) = (parts.next(), parts.next()) {
                        entry
                            .claimed
                            .entry(q.to_owned())
                            .or_default()
                            .insert(r.to_owned());
                    }
                }
                "choice" => {
                    if let (Some(q), Some(i)) = (parts.next(), parts.next()) {
                        if let Ok(n) = i.parse() {
                            entry.choices.insert(q.to_owned(), n);
                        }
                    }
                }
                _ => {}
            }
        }
    }
}

fn save_locked(state: &State) {
    let Some(dir) = state.dir.as_ref() else {
        return;
    };
    let mut out = String::new();
    for (team, p) in &state.teams {
        for t in &p.completed_tasks {
            out.push_str(&format!("{team}|task|{t}\n"));
        }
        for q in &p.completed_quests {
            out.push_str(&format!("{team}|quest|{q}\n"));
        }
        for (q, rewards) in &p.claimed {
            for r in rewards {
                out.push_str(&format!("{team}|claim|{q}|{r}\n"));
            }
        }
        for (q, i) in &p.choices {
            out.push_str(&format!("{team}|choice|{q}|{i}\n"));
        }
    }
    let _ = fs::write(progress_path(dir), out);
    let _ = fs::write(theme_path(dir), &state.theme);
}

pub fn theme() -> String {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    if state.theme.is_empty() {
        "copper".into()
    } else {
        state.theme.clone()
    }
}

pub fn set_theme(id: &str) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.theme = id.to_owned();
    save_locked(&state);
}

fn team_mut<'a>(state: &'a mut State, team: &str) -> &'a mut TeamProgress {
    state.teams.entry(team.to_owned()).or_default()
}

pub fn complete_task(team: &str, task_id: &str) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    team_mut(&mut state, team)
        .completed_tasks
        .insert(task_id.to_owned());
    save_locked(&state);
}

pub fn is_task_done(team: &str, task_id: &str) -> bool {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state
        .teams
        .get(team)
        .map(|p| p.completed_tasks.contains(task_id))
        .unwrap_or(false)
}

pub fn complete_quest(team: &str, quest_id: &str) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    team_mut(&mut state, team)
        .completed_quests
        .insert(quest_id.to_owned());
    save_locked(&state);
}

pub fn is_quest_done(team: &str, quest_id: &str) -> bool {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state
        .teams
        .get(team)
        .map(|p| p.completed_quests.contains(quest_id))
        .unwrap_or(false)
}

fn claim_key(player: u128, reward_id: &str) -> String {
    format!("{player:032x}:{reward_id}")
}

/// Claim is per claiming player; team shares quest unlock only.
pub fn mark_claimed(team: &str, player: u128, quest_id: &str, reward_id: &str) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    team_mut(&mut state, team)
        .claimed
        .entry(quest_id.to_owned())
        .or_default()
        .insert(claim_key(player, reward_id));
    save_locked(&state);
}

pub fn is_claimed(team: &str, player: u128, quest_id: &str, reward_id: &str) -> bool {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state
        .teams
        .get(team)
        .and_then(|p| p.claimed.get(quest_id))
        .map(|s| s.contains(&claim_key(player, reward_id)))
        .unwrap_or(false)
}

pub fn set_choice(team: &str, quest_id: &str, index: i32) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    team_mut(&mut state, team)
        .choices
        .insert(quest_id.to_owned(), index);
    save_locked(&state);
}

pub fn choice(team: &str, quest_id: &str) -> Option<i32> {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state
        .teams
        .get(team)
        .and_then(|p| p.choices.get(quest_id).copied())
}

pub fn snapshot(team: &str) -> TeamProgress {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.teams.get(team).cloned().unwrap_or_default()
}
