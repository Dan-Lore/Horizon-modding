"""SQLite import for greglite-tracker.ps1 (stdlib only)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def import_db(catalog_path: Path, rows_path: Path, db_path: Path) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    rows = json.loads(rows_path.read_text(encoding="utf-8-sig"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS machines (
            id TEXT PRIMARY KEY,
            gtm_type TEXT NOT NULL,
            tier TEXT,
            kind TEXT,
            source_mod TEXT,
            catalog_status TEXT,
            wave TEXT,
            min_recipes INTEGER DEFAULT 0,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS content_scan (
            machine_id TEXT PRIMARY KEY REFERENCES machines(id),
            has_block INTEGER NOT NULL,
            has_menu INTEGER NOT NULL,
            recipe_count INTEGER NOT NULL,
            content_status TEXT NOT NULL,
            gaps TEXT
        );
        CREATE TABLE IF NOT EXISTS milestones (
            id TEXT PRIMARY KEY,
            title TEXT,
            catalog_status TEXT
        );
        """
    )
    con.execute("DELETE FROM machines")
    con.execute("DELETE FROM content_scan")
    con.execute("DELETE FROM milestones")
    for m in catalog.get("machines", []):
        con.execute(
            """INSERT INTO machines(
                id, gtm_type, tier, kind, source_mod, catalog_status, wave, min_recipes, notes
            ) VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                m["id"],
                m.get("gtm_type"),
                m.get("tier"),
                m.get("kind"),
                m.get("source_mod"),
                m.get("status"),
                m.get("wave"),
                int(m.get("min_recipes") or 0),
                m.get("notes"),
            ),
        )
    for r in rows:
        con.execute(
            """INSERT INTO content_scan(
                machine_id, has_block, has_menu, recipe_count, content_status, gaps
            ) VALUES (?,?,?,?,?,?)""",
            (
                r["id"],
                int(r["has_block"]),
                int(r["has_menu"]),
                int(r["recipe_count"]),
                r["content_status"],
                r.get("gaps") or "",
            ),
        )
    for ms in catalog.get("milestones", []):
        con.execute(
            "INSERT INTO milestones(id, title, catalog_status) VALUES (?,?,?)",
            (ms["id"], ms.get("title"), ms.get("status")),
        )
    con.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema', '1')"
    )
    con.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES ('updated', ?)",
        (catalog.get("updated", ""),),
    )
    con.commit()
    con.close()
    print(f"Wrote {db_path}")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: tracker_db.py <catalog.json> <rows.json> <greglite.db>")
    import_db(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    main()