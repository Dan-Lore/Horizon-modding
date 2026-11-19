#!/usr/bin/env python3
"""One-shot: mods/gtceu → mods/gtceu and rewrite ids/paths (Wave 0)."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mods" / "gtceu"
DST = ROOT / "mods" / "gtceu"

TEXT_SUFFIXES = {
    ".rs",
    ".toml",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".inc",
}


def rewrite_text(text: str) -> str:
    # Order matters: longer / more specific first.
    repls = [
        ("mods/gtceu", "mods/gtceu"),
        ("mods\\gtceu", "mods\\gtceu"),
        ("mixins/gtceu", "mixins/gtceu"),
        ("mixins\\gtceu", "mixins\\gtceu"),
        ("mod-gtceu", "mod-gtceu"),
        ("pack-gtceu", "pack-gtceu"),
        ("_gtceu-pack", "_gtceu-pack"),
        ("gtceu.hmod", "gtceu.hmod"),
        ("@gtceu", "@gtceu"),
        ("gtceu:", "gtceu:"),
        ("itemGroup.gtceu", "itemGroup.gtceu"),
        ('id = "gtceu"', 'id = "gtceu"'),
        ("id = 'gtceu'", "id = 'gtceu'"),
        ('"id": "gtceu"', '"id": "gtceu"'),
        ('"gtceu"', '"gtceu"'),
        ("'gtceu'", "'gtceu'"),
        ("GregTech", "GregTech"),
        ("gtceu", "gtceu"),
    ]
    out = text
    for a, b in repls:
        out = out.replace(a, b)
    return out


def copy_tree_renaming_ns() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    for path in SRC.rglob("*"):
        rel = path.relative_to(SRC)
        parts = []
        for p in rel.parts:
            parts.append("gtceu" if p == "gtceu" else p)
        dest = DST.joinpath(*parts)
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
            "NOTICE",
            "LICENSE",
            "PLAY.txt",
        }:
            try:
                raw = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(path, dest)
                continue
            dest.write_text(rewrite_text(raw), encoding="utf-8", newline="\n")
        else:
            shutil.copy2(path, dest)


def rewrite_repo_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"NOTICE"}:
        return False
    # Skip this migrator and huge unrelated trees
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if rel.startswith("mods/gtceu/") or rel.startswith("mods/gtceu/"):
        return False
    if path.name == "migrate-gtceu-to-gtceu.py":
        return False
    if any(
        rel.startswith(p)
        for p in (
            "launcher/",
            "upstream/",
            "reference/",
            ".git/",
            "tools/_gtceu-pack",
            "tools/_gtceu-pack",
        )
    ):
        return False
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    if "gtceu" not in raw and "GregTech" not in raw:
        return False
    new = rewrite_text(raw)
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False


def rewrite_repo_refs() -> list[str]:
    changed: list[str] = []
    roots = [
        ROOT / "tools",
        ROOT / "pack",
        ROOT / "docs",
        ROOT / "mods" / "quests",
        ROOT / "mods" / "adastra",
        ROOT / "mods" / "tfc",
        ROOT / "mods" / "firmalife",
        ROOT / "mods" / "teams",
        ROOT / "mods" / "greate-horizon",
        ROOT / "AGENTS.md",
        ROOT / ".cursor",
    ]
    for root in roots:
        if root.is_file():
            if rewrite_repo_file(root):
                changed.append(str(root.relative_to(ROOT)))
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if rewrite_repo_file(path):
                changed.append(str(path.relative_to(ROOT)))
    return changed


def write_pack_gtceu() -> None:
    src = ROOT / "tools" / "pack-gtceu.ps1"
    text = src.read_text(encoding="utf-8") if src.exists() else ""
    # Prefer rewriting from current gtceu script content before tree delete
    if not text:
        text = (ROOT / "tools" / "pack-gtceu.ps1").read_text(encoding="utf-8")
    text = rewrite_text(text)
    # Fix default Out path explicitly
    text = text.replace(
        "tfg-horizon\\horizon-native-mods\\gtceu.hmod",
        "tfg-horizon\\horizon-native-mods\\gtceu.hmod",
    )
    (ROOT / "tools" / "pack-gtceu.ps1").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"missing {SRC}")
    print("copying tree…")
    copy_tree_renaming_ns()
    # horizon-mod.toml force
    toml = DST / "horizon-mod.toml"
    toml.write_text(
        rewrite_text(
            """id = "gtceu"
name = "GregTech"
version = "0.5.5"
description = "GregTech Modern rewrite on Horizon (Absolute port). Technical id gtceu."
authors = ["Horizon-modding workshop"]
api = "0.2"
side = "both"
capabilities = ["registries"]
"""
        ),
        encoding="utf-8",
        newline="\n",
    )
    # Cargo name
    cargo = DST / "api" / "Cargo.toml"
    if cargo.exists():
        cargo.write_text(rewrite_text(cargo.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    write_pack_gtceu()
    print("rewriting repo refs…")
    changed = rewrite_repo_refs()
    print(f"repo files touched: {len(changed)}")
    # Remove old tree
    print("removing mods/gtceu…")
    shutil.rmtree(SRC)
    old_pack = ROOT / "tools" / "pack-gtceu.ps1"
    if old_pack.exists():
        old_pack.unlink()
    # Rename glue data folder if present
    glue_old = ROOT / "pack" / "glue" / "data" / "gtceu"
    glue_new = ROOT / "pack" / "glue" / "data" / "gtceu"
    if glue_old.is_dir():
        if glue_new.exists():
            shutil.rmtree(glue_new)
        glue_old.rename(glue_new)
        for path in glue_new.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                path.write_text(rewrite_text(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print("OK", DST)


if __name__ == "__main__":
    main()
