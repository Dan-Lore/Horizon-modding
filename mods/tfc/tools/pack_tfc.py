#!/usr/bin/env python3
"""Pack mods/tfc into a combined .hmod (POSIX zip paths)."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # mods/tfc
REPO = ROOT.parents[1]
OUT_DEFAULT = REPO / "pack" / "mods" / "tfc.hmod"


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()
    out: Path = args.out

    # Ensure content is fresh
    gen = ROOT / "tools" / "gen_content.py"
    if gen.is_file():
        import subprocess

        subprocess.check_call(["python3", str(gen)])

    stage = REPO / "tools" / "_tfc-pack"
    if stage.exists():
        shutil.rmtree(stage)
    mixin = stage / "mixins" / "tfc"
    mixin.mkdir(parents=True)
    shutil.copy(ROOT / "horizon-mod.toml", stage / "horizon-mod.toml")
    shutil.copytree(ROOT / "assets", stage / "assets")
    shutil.copytree(ROOT / "data", stage / "data")
    shutil.copy(ROOT / "horizon-mixin.toml", mixin / "horizon-mixin.toml")
    shutil.copytree(ROOT / "api", mixin / "api")
    for name in ("README.md", "NOTICE"):
        src = ROOT / name
        if src.is_file():
            shutil.copy(src, mixin / name)

    native = {
        "schema": 1,
        "id": "tfc",
        "version": "0.1.0",
        "game": "26.3",
        "horizon": "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca",
        "mixins": "5a64af938ec86b00d53d16a408aabc0038fb3e57",
        "hooks": 411,
    }
    (stage / "horizon-native.json").write_text(json.dumps(native, indent=2) + "\n", encoding="utf-8")

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in stage.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(stage).as_posix())
    shutil.rmtree(stage)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
