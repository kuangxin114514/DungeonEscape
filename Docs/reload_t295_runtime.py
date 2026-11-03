# -*- coding: utf-8 -*-
"""Hot-reload shop_interact_runtime after T295 HP bar X offset."""
from __future__ import print_function
import unreal
import importlib
import sys
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t295.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("ReloadT295: " + str(m))
    except Exception:
        print(m)

try:
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path:
        sys.path.insert(0, py)
    dst = os.path.join(py, "shop_interact_runtime.py")
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
        log("reloaded existing shop_interact_runtime")
    else:
        import shop_interact_runtime as m
        log("imported shop_interact_runtime fresh")
    fn = getattr(m, "bootstrap", None)
    if callable(fn):
        try:
            fn()
            log("called bootstrap")
        except Exception as e:
            log("bootstrap err " + str(e))
    else:
        log("no bootstrap fn")
    log("ENEMY_HP_BAR_Z_OFFSET=%s" % getattr(m, "ENEMY_HP_BAR_Z_OFFSET", None))
    log("ENEMY_HP_BAR_X_OFFSET=%s" % getattr(m, "ENEMY_HP_BAR_X_OFFSET", None))
    tag = "NO_T295"
    try:
        text = open(dst, encoding="utf-8").read()
        if "ENEMY_HP_BAR_X_OFFSET" in text and "T295_X_OFFSET" in text:
            tag = "T295_X_OFFSET"
        elif "ENEMY_HP_BAR_X_OFFSET" in text:
            tag = "has_X_OFFSET"
    except Exception as e:
        tag = "readerr " + str(e)
    log("file_tag=" + str(tag))
    try:
        clr = getattr(m, "_clear_enemy_bars", None)
        if callable(clr):
            clr(True)
            log("cleared enemy bars")
    except Exception as e:
        log("clear err " + str(e))
    log("OK")
except Exception as e:
    log("FAIL " + str(e))

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)
