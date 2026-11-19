//! Persistent team store under `world_dir()/horizon-teams/`.

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

const INVITE_TTL_SECS: u64 = 600;

#[derive(Clone, Debug)]
pub struct Team {
    pub id: String,
    pub name: String,
    pub owner: u128,
    pub members: Vec<u128>,
}

#[derive(Clone, Debug)]
pub struct Invite {
    pub team_id: String,
    pub team_name: String,
    pub to_uuid: u128,
    pub to_name: String,
    pub from_uuid: u128,
    pub expires_unix: u64,
}

#[derive(Default)]
struct State {
    teams: HashMap<String, Team>,
    /// player uuid -> team id
    membership: HashMap<u128, String>,
    /// lowercase player name -> uuid (best-effort, updated on login)
    names: HashMap<String, u128>,
    /// uuid -> display name
    display: HashMap<u128, String>,
    invites: Vec<Invite>,
    dir: Option<PathBuf>,
}

static STATE: LazyLock<Mutex<State>> = LazyLock::new(|| {
    Mutex::new(State {
        teams: HashMap::new(),
        membership: HashMap::new(),
        names: HashMap::new(),
        display: HashMap::new(),
        invites: Vec::new(),
        dir: None,
    })
});

fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

fn escape(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}

fn teams_path(dir: &Path) -> PathBuf {
    dir.join("teams.json")
}

fn save_locked(state: &State) {
    let Some(dir) = state.dir.as_ref() else {
        return;
    };
    let _ = fs::create_dir_all(dir);
    let mut out = String::from("{\n  \"teams\": [\n");
    let mut first = true;
    for team in state.teams.values() {
        if !first {
            out.push_str(",\n");
        }
        first = false;
        let members: Vec<String> = team.members.iter().map(|m| format!("\"{m:032x}\"")).collect();
        out.push_str(&format!(
            "    {{\"id\":\"{}\",\"name\":\"{}\",\"owner\":\"{:032x}\",\"members\":[{}]}}",
            escape(&team.id),
            escape(&team.name),
            team.owner,
            members.join(",")
        ));
    }
    out.push_str("\n  ],\n  \"invites\": [\n");
    first = true;
    let now = now_unix();
    for inv in state.invites.iter().filter(|i| i.expires_unix >= now) {
        if !first {
            out.push_str(",\n");
        }
        first = false;
        out.push_str(&format!(
            "    {{\"team_id\":\"{}\",\"team_name\":\"{}\",\"to\":\"{:032x}\",\"to_name\":\"{}\",\"from\":\"{:032x}\",\"expires\":{}}}",
            escape(&inv.team_id),
            escape(&inv.team_name),
            inv.to_uuid,
            escape(&inv.to_name),
            inv.from_uuid,
            inv.expires_unix
        ));
    }
    out.push_str("\n  ]\n}\n");
    let _ = fs::write(teams_path(dir), out);
}

fn parse_hex_u128(s: &str) -> Option<u128> {
    u128::from_str_radix(s.trim_matches('"'), 16).ok()
}

/// Very small extractor for `"key":"value"` pairs in a flat object snippet.
fn json_str<'a>(obj: &'a str, key: &str) -> Option<&'a str> {
    let pat = format!("\"{key}\":\"");
    let i = obj.find(&pat)? + pat.len();
    let rest = &obj[i..];
    let end = rest.find('"')?;
    Some(&rest[..end])
}

fn json_num(obj: &str, key: &str) -> Option<u64> {
    let pat = format!("\"{key}\":");
    let i = obj.find(&pat)? + pat.len();
    let rest = obj[i..].trim_start();
    let end = rest
        .find(|c: char| !c.is_ascii_digit())
        .unwrap_or(rest.len());
    rest[..end].parse().ok()
}

fn load_locked(state: &mut State) {
    let Some(dir) = state.dir.clone() else {
        return;
    };
    let path = teams_path(&dir);
    let Ok(text) = fs::read_to_string(&path) else {
        return;
    };
    state.teams.clear();
    state.membership.clear();
    state.invites.clear();
    // Teams array objects
    if let Some(start) = text.find("\"teams\"") {
        let slice = &text[start..];
        for obj in slice.split('{').skip(1) {
            if obj.contains("\"invites\"") && !obj.contains("\"members\"") {
                break;
            }
            let Some(id) = json_str(obj, "id") else {
                continue;
            };
            let Some(name) = json_str(obj, "name") else {
                continue;
            };
            let Some(owner_s) = json_str(obj, "owner") else {
                continue;
            };
            let Some(owner) = parse_hex_u128(owner_s) else {
                continue;
            };
            let mut members = Vec::new();
            if let Some(m_i) = obj.find("\"members\"") {
                let mslice = &obj[m_i..];
                for part in mslice.split('"') {
                    if part.len() == 32 && part.chars().all(|c| c.is_ascii_hexdigit()) {
                        if let Some(u) = parse_hex_u128(part) {
                            members.push(u);
                        }
                    }
                    if mslice[..mslice.find(part).unwrap_or(0) + part.len()].contains(']') {
                        // keep scanning hex only
                    }
                }
            }
            if members.is_empty() {
                members.push(owner);
            }
            let team = Team {
                id: id.to_owned(),
                name: name.to_owned(),
                owner,
                members: members.clone(),
            };
            for m in &members {
                state.membership.insert(*m, team.id.clone());
            }
            state.teams.insert(team.id.clone(), team);
        }
    }
    if let Some(start) = text.find("\"invites\"") {
        let slice = &text[start..];
        for obj in slice.split('{').skip(1) {
            let Some(team_id) = json_str(obj, "team_id") else {
                continue;
            };
            let Some(team_name) = json_str(obj, "team_name") else {
                continue;
            };
            let Some(to_s) = json_str(obj, "to") else {
                continue;
            };
            let Some(to_uuid) = parse_hex_u128(to_s) else {
                continue;
            };
            let to_name = json_str(obj, "to_name").unwrap_or("").to_owned();
            let from = json_str(obj, "from")
                .and_then(parse_hex_u128)
                .unwrap_or(0);
            let expires = json_num(obj, "expires").unwrap_or(0);
            state.invites.push(Invite {
                team_id: team_id.to_owned(),
                team_name: team_name.to_owned(),
                to_uuid,
                to_name,
                from_uuid: from,
                expires_unix: expires,
            });
        }
    }
}

pub fn bind_world(dir: PathBuf) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    if state.dir.as_ref() == Some(&dir) {
        return;
    }
    state.dir = Some(dir.join("horizon-teams"));
    load_locked(&mut state);
}

pub fn remember_player(uuid: u128, name: &str) {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.names.insert(name.to_ascii_lowercase(), uuid);
    state.display.insert(uuid, name.to_owned());
}

pub fn resolve_name(name: &str) -> Option<u128> {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.names.get(&name.to_ascii_lowercase()).copied()
}

pub fn display_name(uuid: u128) -> String {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state
        .display
        .get(&uuid)
        .cloned()
        .unwrap_or_else(|| format!("{uuid:032x}"))
}

fn slug(name: &str) -> String {
    let s: String = name
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() {
                c.to_ascii_lowercase()
            } else {
                '_'
            }
        })
        .collect();
    if s.is_empty() {
        "team".into()
    } else {
        s
    }
}

pub fn ensure_personal(uuid: u128, name: &str) -> Team {
    remember_player(uuid, name);
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(id) = state.membership.get(&uuid) {
        if let Some(team) = state.teams.get(id) {
            return team.clone();
        }
    }
    let id = format!("solo_{uuid:032x}");
    let team = Team {
        id: id.clone(),
        name: format!("{name}'s party"),
        owner: uuid,
        members: vec![uuid],
    };
    state.membership.insert(uuid, id.clone());
    state.teams.insert(id, team.clone());
    save_locked(&state);
    team
}

pub fn team_of(uuid: u128) -> Option<Team> {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    let id = state.membership.get(&uuid)?;
    state.teams.get(id).cloned()
}

pub fn create(uuid: u128, name: &str) -> Result<Team, &'static str> {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    if state.membership.contains_key(&uuid) {
        // Leave personal/auto teams first.
        if let Some(old) = state.membership.get(&uuid).cloned() {
            if let Some(team) = state.teams.get(&old) {
                if team.members.len() > 1 || !team.id.starts_with("solo_") {
                    return Err("already in a team; /team leave first");
                }
            }
            // dissolve solo
            state.teams.remove(&old);
            state.membership.remove(&uuid);
        }
    }
    let base = slug(name);
    let mut id = base.clone();
    let mut n = 2;
    while state.teams.contains_key(&id) {
        id = format!("{base}_{n}");
        n += 1;
    }
    let team = Team {
        id: id.clone(),
        name: name.to_owned(),
        owner: uuid,
        members: vec![uuid],
    };
    state.membership.insert(uuid, id.clone());
    state.teams.insert(id, team.clone());
    save_locked(&state);
    Ok(team)
}

pub fn invite(from: u128, to_name: &str) -> Result<Invite, &'static str> {
    let to = resolve_name(to_name).ok_or("player not seen yet (they must join once)")?;
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    let team_id = state
        .membership
        .get(&from)
        .cloned()
        .ok_or("create a team first")?;
    let team = state.teams.get(&team_id).ok_or("team missing")?.clone();
    if team.owner != from {
        return Err("only the owner can invite");
    }
    if state.membership.get(&to) == Some(&team_id) {
        return Err("already a member");
    }
    let now = now_unix();
    state.invites.retain(|i| i.expires_unix >= now && i.to_uuid != to);
    let inv = Invite {
        team_id: team.id.clone(),
        team_name: team.name.clone(),
        to_uuid: to,
        to_name: to_name.to_owned(),
        from_uuid: from,
        expires_unix: now + INVITE_TTL_SECS,
    };
    state.invites.push(inv.clone());
    save_locked(&state);
    Ok(inv)
}

pub fn invites_for(uuid: u128) -> Vec<Invite> {
    let now = now_unix();
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.invites.retain(|i| i.expires_unix >= now);
    state
        .invites
        .iter()
        .filter(|i| i.to_uuid == uuid)
        .cloned()
        .collect()
}

pub fn join(uuid: u128, team_name: &str) -> Result<Team, &'static str> {
    let now = now_unix();
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.invites.retain(|i| i.expires_unix >= now);
    let team = state
        .teams
        .values()
        .find(|t| t.name.eq_ignore_ascii_case(team_name) || t.id.eq_ignore_ascii_case(team_name))
        .cloned()
        .ok_or("no such team")?;
    let invited = state
        .invites
        .iter()
        .any(|i| i.to_uuid == uuid && i.team_id == team.id);
    if !invited {
        return Err("no invite for that team");
    }
    // leave old
    if let Some(old) = state.membership.remove(&uuid) {
        if let Some(t) = state.teams.get_mut(&old) {
            t.members.retain(|m| *m != uuid);
            if t.members.is_empty() {
                state.teams.remove(&old);
            }
        }
    }
    let team_id = team.id.clone();
    if let Some(t) = state.teams.get_mut(&team_id) {
        if !t.members.contains(&uuid) {
            t.members.push(uuid);
        }
    }
    state.membership.insert(uuid, team_id.clone());
    state
        .invites
        .retain(|i| !(i.to_uuid == uuid && i.team_id == team_id));
    let out = state.teams.get(&team_id).cloned().ok_or("team missing")?;
    save_locked(&state);
    Ok(out)
}

pub fn leave(uuid: u128) -> Result<String, &'static str> {
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    let team_id = state.membership.remove(&uuid).ok_or("not in a team")?;
    let Some(mut team) = state.teams.remove(&team_id) else {
        return Ok("left".into());
    };
    team.members.retain(|m| *m != uuid);
    let msg = if team.members.is_empty() {
        format!("dissolved team {}", team.name)
    } else {
        if team.owner == uuid {
            team.owner = team.members[0];
        }
        state.membership.insert(team.owner, team_id.clone());
        for m in &team.members {
            state.membership.insert(*m, team_id.clone());
        }
        state.teams.insert(team_id, team.clone());
        format!("left team {}", team.name)
    };
    save_locked(&state);
    Ok(msg)
}

pub fn kick(owner: u128, target_name: &str) -> Result<String, &'static str> {
    let target = resolve_name(target_name).ok_or("player not seen")?;
    let mut state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    let team_id = state
        .membership
        .get(&owner)
        .cloned()
        .ok_or("not in a team")?;
    let name = {
        let team = state.teams.get_mut(&team_id).ok_or("team missing")?;
        if team.owner != owner {
            return Err("only the owner can kick");
        }
        if target == owner {
            return Err("cannot kick yourself; /hteam leave");
        }
        if !team.members.contains(&target) {
            return Err("not a member");
        }
        team.members.retain(|m| *m != target);
        team.name.clone()
    };
    state.membership.remove(&target);
    save_locked(&state);
    Ok(format!("kicked {target_name} from {name}"))
}

/// Path used by quests mod to read membership without linking crates.
pub fn team_id_of(uuid: u128) -> Option<String> {
    let state = STATE.lock().unwrap_or_else(|e| e.into_inner());
    state.membership.get(&uuid).cloned()
}
