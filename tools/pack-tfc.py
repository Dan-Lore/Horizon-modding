#!/usr/bin/env python3
"""Repo-root wrapper: pack mods/tfc → pack/mods/tfc.hmod."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "mods" / "tfc" / "tools" / "pack_tfc.py"), run_name="__main__")
