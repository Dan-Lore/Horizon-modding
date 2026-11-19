#!/usr/bin/env python3
"""Vendor GregTech Modern machine sounds (LGPL-3.0) into mods/greglite/assets.

Default jar: TFG-Modern instance gtceu-*.jar
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_SOUNDS = ROOT / "assets" / "greglite" / "sounds"
OUT_JSON = ROOT / "assets" / "greglite" / "sounds.json"
NOTICE = ROOT / "NOTICE"
DEFAULT_MODS = Path.home() / "curseforge/minecraft/Instances/TerraFirmaGreg-Modern/mods"


def find_jar(explicit: Path | None) -> Path:
    if explicit:
        return explicit
    jars = sorted(DEFAULT_MODS.glob("gtceu-*.jar"))
    if not jars:
        raise SystemExit(f"no gtceu-*.jar under {DEFAULT_MODS}")
    return jars[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", type=Path, default=None)
    args = ap.parse_args()
    jar = find_jar(args.jar)
    print("jar", jar)
    with zipfile.ZipFile(jar) as z:
        toml = z.read("META-INF/mods.toml").decode("utf-8", errors="replace")
        lic = re.search(r'(?im)^license\s*=\s*"?([^"\r\n]+)"?', toml)
        lic_s = (lic.group(1) if lic else "").upper()
        if "LGPL" not in lic_s and "GPL" not in lic_s:
            print("warn: license", lic_s)
        raw = json.loads(z.read("assets/gtceu/sounds.json"))
        OUT_SOUNDS.mkdir(parents=True, exist_ok=True)
        # Remap event names under greglite namespace; copy oggs
        out_map: dict = {}
        for event, body in raw.items():
            sounds = body.get("sounds", [])
            new_sounds = []
            for s in sounds:
                name = s if isinstance(s, str) else s.get("name", "")
                # gtceu:foo or just foo
                leaf = name.split(":")[-1].split("/")[-1]
                zip_path = f"assets/gtceu/sounds/{leaf}.ogg"
                if zip_path not in z.namelist():
                    # try path from name
                    alt = name.replace(":", "/")
                    zip_path = f"assets/{alt}.ogg"
                if zip_path in z.namelist():
                    dest = OUT_SOUNDS / f"{leaf}.ogg"
                    dest.write_bytes(z.read(zip_path))
                    new_sounds.append(f"greglite:{leaf}")
                else:
                    print("missing", zip_path)
            if new_sounds:
                entry = dict(body)
                entry["sounds"] = new_sounds
                out_map[event] = entry
        OUT_JSON.write_text(json.dumps(out_map, indent=2) + "\n", encoding="utf-8")
        print("events", len(out_map), "ogg", len(list(OUT_SOUNDS.glob('*.ogg'))))
    text = NOTICE.read_text(encoding="utf-8") if NOTICE.is_file() else ""
    line = "Sounds: vendored from GregTech Modern (LGPL-3.0) via fetch_gtm_sounds.py.\n"
    if "fetch_gtm_sounds.py" not in text:
        NOTICE.write_text(text.rstrip() + "\n\n" + line, encoding="utf-8")


if __name__ == "__main__":
    main()
