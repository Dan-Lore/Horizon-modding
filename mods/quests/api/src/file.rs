//! Quest definitions (baked table + world title overrides).

use std::collections::HashMap;
use std::fs;
use std::sync::Mutex;

use crate::baked;

#[derive(Clone, Debug)]
pub struct Task {
    pub id: String,
    pub kind: String,
    pub title: String,
    pub item: Option<String>,
    pub count: i32,
    pub x: i32,
    pub y: i32,
    pub z: i32,
    pub radius: i32,
}

#[derive(Clone, Debug)]
pub struct Reward {
    pub id: String,
    pub kind: String,
    pub item: Option<String>,
    pub count: i32,
    pub amount: i32,
    pub command: Option<String>,
    pub table: Option<String>,
    pub options: Vec<(String, i32)>,
}

#[derive(Clone, Debug)]
pub struct Quest {
    pub id: String,
    pub title: String,
    pub dependencies: Vec<String>,
    pub tasks: Vec<Task>,
    pub rewards: Vec<Reward>,
}

#[derive(Clone, Debug)]
pub struct Chapter {
    pub id: String,
    pub title: String,
    pub progression: String,
    pub quests: Vec<String>,
}

#[derive(Clone, Debug)]
pub struct TableEntry {
    pub item: String,
    pub count: i32,
    pub weight: i32,
}

#[derive(Clone, Debug, Default)]
pub struct QuestFile {
    pub chapters: Vec<Chapter>,
    pub quests: HashMap<String, Quest>,
    pub tables: HashMap<String, Vec<TableEntry>>,
    pub themes: HashMap<String, String>,
    pub theme_default: String,
}

static FILE: Mutex<Option<QuestFile>> = Mutex::new(None);
static TITLE_OVERRIDES: Mutex<HashMap<String, String>> = Mutex::new(HashMap::new());

fn apply_overrides(mut file: QuestFile) -> QuestFile {
    let map = TITLE_OVERRIDES.lock().unwrap_or_else(|e| e.into_inner());
    for (id, title) in map.iter() {
        if let Some(q) = file.quests.get_mut(id) {
            q.title = title.clone();
        }
    }
    file
}

pub fn load() -> QuestFile {
    let mut guard = FILE.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(file) = guard.as_ref() {
        return file.clone();
    }
    let file = apply_overrides(baked::baked());
    *guard = Some(file.clone());
    file
}

pub fn reload(world_dir: Option<std::path::PathBuf>) -> QuestFile {
    if let Some(dir) = world_dir.as_ref() {
        let titles = dir.join("horizon-quests").join("title_overrides.json");
        if let Ok(t) = fs::read_to_string(titles) {
            let mut map = TITLE_OVERRIDES.lock().unwrap_or_else(|e| e.into_inner());
            map.clear();
            for part in t.split(',') {
                let part = part.replace(['{', '}', '\n'], "");
                if let Some((k, v)) = part.split_once(':') {
                    let k = k.trim().trim_matches('"');
                    let v = v.trim().trim_matches('"');
                    if !k.is_empty() {
                        map.insert(k.to_owned(), v.to_owned());
                    }
                }
            }
        }
    }
    let file = apply_overrides(baked::baked());
    let mut guard = FILE.lock().unwrap_or_else(|e| e.into_inner());
    *guard = Some(file.clone());
    file
}

pub fn set_title_override(world_dir: std::path::PathBuf, quest_id: &str, title: &str) {
    let dir = world_dir.join("horizon-quests");
    let _ = fs::create_dir_all(&dir);
    {
        let mut map = TITLE_OVERRIDES.lock().unwrap_or_else(|e| e.into_inner());
        map.insert(quest_id.to_owned(), title.to_owned());
        let mut out = String::from("{\n");
        let mut first = true;
        for (k, v) in map.iter() {
            if !first {
                out.push_str(",\n");
            }
            first = false;
            out.push_str(&format!(
                "  \"{}\":\"{}\"",
                k.replace('"', ""),
                v.replace('"', "")
            ));
        }
        out.push_str("\n}\n");
        let _ = fs::write(dir.join("title_overrides.json"), out);
    }
    let _ = reload(Some(world_dir));
}

pub fn quest(id: &str) -> Option<Quest> {
    load().quests.get(id).cloned()
}

pub fn chapter_for_quest(quest_id: &str) -> Option<Chapter> {
    load()
        .chapters
        .into_iter()
        .find(|c| c.quests.iter().any(|q| q == quest_id))
}

pub fn accent(theme: &str) -> String {
    load()
        .themes
        .get(theme)
        .cloned()
        .unwrap_or_else(|| "§6".into())
}

pub fn counts() -> (usize, usize) {
    let f = load();
    (f.chapters.len(), f.quests.len())
}
