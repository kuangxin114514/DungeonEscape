# -*- coding: utf-8 -*-
from __future__ import print_function
import io, re, os
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
print("len", len(raw), "crlf", raw.count("\r\n"), "lf", raw.count("\n"))

# show ensure section
m = re.search(r"def _ensure_move_settings\(pawn\):.*?def _get_ai_controller", raw, re.S)
print("---ENSURE---")
print(m.group(0) if m else "NO")
