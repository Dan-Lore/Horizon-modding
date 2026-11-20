#!/usr/bin/env python3
"""Pack mods/firmalife into a combined .hmod (no tables JSON under mixins)."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mods" / "firmalife"
REV = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"
MIXINS = "5a64af938ec86b00d53d16a408aabc0038fb3e57"
HOOKS = 411
DEFAULT_OUT = (
    Path.home()
    / "AppData/Roaming/horizon/instances/tfg-dev/horizon-native-mods/firmalife.hmod"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out: Path = args.out

    stage = Path(tempfile.mkdtemp(prefix="firmalife-pack-"))
    try:
        mixin = stage / "mixins" / "firmalife"
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
            src = SRC / name
            if src.is_file():
                shutil.copy(src, mixin / name)
        native = {
            "schema": 1,
            "id": "firmalife",
            "version": "0.1.3",
            "game": "26.3",
            "horizon": REV,
            "mixins": MIXINS,
            "hooks": HOOKS,
        }
        (stage / "horizon-native.json").write_text(
            json.dumps(native), encoding="utf-8"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out.unlink()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in stage.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(stage).as_posix())
        print(f"{out} {out.stat().st_size}")
    finally:
        shutil.rmtree(stage)


if __name__ == "__main__":
    main()
