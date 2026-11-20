#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Bake quests first
import runpy

runpy.run_path(str(ROOT / "mods/quests/tools/gen_content.py"), run_name="__main__")

pairs = [
    (ROOT / "mods/quests/horizon-mixin.toml", "0.1.1", "0.1.2"),
    (ROOT / "tools/pack-quests.py", "0.1.1", "0.1.2"),
    (ROOT / "mods/tfc/horizon-mixin.toml", "0.2.1", "0.2.2"),
    (ROOT / "mods/tfc/horizon-mod.toml", "0.2.1", "0.2.2"),
    (ROOT / "mods/adastra/horizon-mixin.toml", "0.1.1", "0.1.2"),
    (ROOT / "tools/pack-adastra.py", "0.1.1", "0.1.2"),
    (ROOT / "mods/gtceu/horizon-mixin.toml", "0.5.6", "0.5.7"),
    (ROOT / "tools/pack-gtceu.ps1", "0.5.6", "0.5.7"),
]
for path, old, new in pairs:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"skip {path.name}: no {old}")
        continue
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"bumped {path.relative_to(ROOT)} {old} -> {new}")
