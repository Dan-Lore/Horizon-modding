#!/usr/bin/env python3
"""Pack mods/teams into a combined .hmod (POSIX zip paths)."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mods" / "teams"
OUT = SRC / "dist" / "teams.hmod"
REV = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"
MIXINS = "5a64af938ec86b00d53d16a408aabc0038fb3e57"
HOOKS = 411


def main() -> None:
    if not (SRC / "assets").is_dir() or not (SRC / "data").is_dir():
        raise SystemExit("missing teams content")
    stage = Path(tempfile.mkdtemp(prefix="teams-pack-"))
    try:
        mixin = stage / "mixins" / "teams"
        mixin.mkdir(parents=True)
        shutil.copy(SRC / "horizon-mod.toml", stage / "horizon-mod.toml")
        shutil.copytree(SRC / "assets", stage / "assets")
        shutil.copytree(SRC / "data", stage / "data")
        shutil.copy(SRC / "horizon-mixin.toml", mixin / "horizon-mixin.toml")
        shutil.copytree(
            SRC / "api",
            mixin / "api",
            ignore=shutil.ignore_patterns("target", ".horizon-cache"),
        )
        for name in ("README.md", "NOTICE"):
            shutil.copy(SRC / name, mixin / name)
        native = {
            "schema": 1,
            "id": "teams",
            "version": "0.1.0",
            "game": "26.3",
            "horizon": REV,
            "mixins": MIXINS,
            "hooks": HOOKS,
        }
        (stage / "horizon-native.json").write_text(json.dumps(native), encoding="utf-8")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        if OUT.exists():
            OUT.unlink()
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in stage.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(stage).as_posix())
        print(f"{OUT} {OUT.stat().st_size}")
    finally:
        shutil.rmtree(stage)


if __name__ == "__main__":
    main()
