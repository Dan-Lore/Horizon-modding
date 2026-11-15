#!/usr/bin/env python3
"""Validate mods/quests/tables/questfile.json shape (no Horizon runtime)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "mods" / "quests" / "tables" / "questfile.json"


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    quests = {q["id"]: q for q in data["quests"]}
    assert data["schema"] == 1
    assert "intro" in {c["id"] for c in data["chapters"]}
    for chapter in data["chapters"]:
        assert chapter["progression"] in ("linear", "flexible")
        for qid in chapter["quests"]:
            assert qid in quests, qid
    for q in data["quests"]:
        for dep in q.get("dependencies", []):
            assert dep in quests, dep
        for t in q["tasks"]:
            assert "id" in t and "type" in t
        for r in q["rewards"]:
            assert "id" in r and "type" in r
    tables = {t["id"] for t in data["reward_tables"]}
    assert "starter_crate" in tables
    # First five pack-line quests exist
    for qid in ("welcome", "gather_sticks", "open_board", "ae2_book", "see_greglite"):
        assert qid in quests, qid
    print(f"ok {len(quests)} quests, {len(data['chapters'])} chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
