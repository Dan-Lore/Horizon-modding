#!/usr/bin/env python3
"""Pack mods/tfc into a combined .hmod (POSIX zip paths)."""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "mods" / "tfc"
STAGE = ROOT / "tools" / "_tfc-pack"
DEFAULT_OUT = ROOT / "pack" / "mods" / "tfc.hmod"

HORIZON = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"
MIXINS = "5a64af938ec86b00d53d16a408aabc0038fb3e57"
HOOKS = 411


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    if not SRC.is_dir():
        print("missing", SRC, file=sys.stderr)
        return 1
    if STAGE.exists():
        shutil.rmtree(STAGE)
    (STAGE / "mixins" / "tfc").mkdir(parents=True)
    shutil.copy(SRC / "horizon-mod.toml", STAGE / "horizon-mod.toml")
    shutil.copytree(SRC / "assets", STAGE / "assets")
    shutil.copytree(SRC / "data", STAGE / "data")
    if (SRC / "tables").is_dir():
        shutil.copytree(SRC / "tables", STAGE / "tables")
    shutil.copy(SRC / "horizon-mixin.toml", STAGE / "mixins" / "tfc" / "horizon-mixin.toml")
    shutil.copytree(SRC / "api", STAGE / "mixins" / "tfc" / "api")
    for name in ("README.md", "NOTICE"):
        src = SRC / name
        if src.exists():
            shutil.copy(src, STAGE / "mixins" / "tfc" / name)
    native = {
        "schema": 1,
        "id": "tfc",
        "version": "0.1.0",
        "game": "26.3",
        "horizon": HORIZON,
        "mixins": MIXINS,
        "hooks": HOOKS,
    }
    (STAGE / "horizon-native.json").write_text(
        json.dumps(native, separators=(",", ":")), encoding="utf-8"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in STAGE.rglob("*"):
            if path.is_file():
                z.write(path, path.relative_to(STAGE).as_posix())
    print(out, out.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
