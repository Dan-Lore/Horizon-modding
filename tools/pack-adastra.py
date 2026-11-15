#!/usr/bin/env python3
"""Pack mods/adastra into a combined .hmod (POSIX zip paths).

Does not install the archive onto tfg-horizon. The launcher rewrites `hooks`
and `mixins` when it native-builds.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mods" / "adastra"
OUT = SRC / "dist" / "adastra.hmod"
REV = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"


def main() -> None:
    if not (SRC / "assets").is_dir() or not (SRC / "data").is_dir():
        raise SystemExit("missing generated content; run mods/adastra/tools/gen_content.py")
    stage = Path(tempfile.mkdtemp(prefix="adastra-pack-"))
    try:
        mixin = stage / "mixins" / "adastra"
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
            "id": "adastra",
            "version": "0.1.0",
            "game": "26.3",
            "horizon": REV,
            "mixins": REV,
            "hooks": 97,
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
