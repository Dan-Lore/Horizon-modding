//! Read Horizon Teams membership from the shared world folder.

use std::fs;
use std::path::Path;
use std::sync::{LazyLock, Mutex};

static MEMBER: LazyLock<Mutex<std::collections::HashMap<u128, String>>> =
    LazyLock::new(|| Mutex::new(std::collections::HashMap::new()));

fn parse_hex_u128(s: &str) -> Option<u128> {
    u128::from_str_radix(s, 16).ok()
}

pub fn refresh(world_dir: &Path) {
    let path = world_dir.join("horizon-teams").join("teams.json");
    let Ok(text) = fs::read_to_string(path) else {
        return;
    };
    let mut map = MEMBER.lock().unwrap_or_else(|e| e.into_inner());
    map.clear();
    // members listed as 32-hex strings
    let mut current_team: Option<String> = None;
    for line in text.lines() {
        if let Some(i) = line.find("\"id\":\"") {
            let rest = &line[i + 6..];
            if let Some(end) = rest.find('"') {
                current_team = Some(rest[..end].to_owned());
            }
        }
        if line.contains("\"members\"") {
            let team = current_team.clone();
            for part in line.split('"') {
                if part.len() == 32 && part.chars().all(|c| c.is_ascii_hexdigit()) {
                    if let (Some(u), Some(t)) = (parse_hex_u128(part), team.as_ref()) {
                        map.insert(u, t.clone());
                    }
                }
            }
        }
        // also owner field
        if let Some(i) = line.find("\"owner\":\"") {
            let rest = &line[i + 9..];
            if let Some(end) = rest.find('"') {
                if let (Some(u), Some(t)) = (parse_hex_u128(&rest[..end]), current_team.as_ref()) {
                    map.insert(u, t.clone());
                }
            }
        }
    }
}

pub fn team_id(uuid: u128) -> String {
    let map = MEMBER.lock().unwrap_or_else(|e| e.into_inner());
    map.get(&uuid)
        .cloned()
        .unwrap_or_else(|| format!("solo_{uuid:032x}"))
}
