# -*- coding: utf-8 -*-
"""Hot-reload shop_interact_runtime after T299 HP50 delayed damage."""
from __future__ import print_function
import unreal
import importlib
import sys
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t299.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("ReloadT299: " + str(m))
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
    log("ENEMY_HP_BARS_ENABLED=%s" % getattr(m, "ENEMY_HP_BARS_ENABLED", None))
    log("ATTACK_DAMAGE=%s" % getattr(m, "ATTACK_DAMAGE", None))
    log("ATTACK_DAMAGE_DELAY=%s" % getattr(m, "ATTACK_DAMAGE_DELAY", None))
    log("_ENEMY_HP_DEFAULT=%s" % getattr(m, "_ENEMY_HP_DEFAULT", None))
    tag = "NO_T299"
    try:
        text = open(dst, encoding="utf-8").read()
        if "T299_HP50" in text and "ATTACK_DAMAGE_DELAY = 1.0" in text:
            tag = "T299_HP50"
        elif "T299_HP50" in text:
            tag = "T299_partial"
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
    try:
        cache = getattr(m, "_ENEMY_HP_CACHE", None)
        if isinstance(cache, dict):
            cache.clear()
            log("cleared hp cache")
    except Exception as e:
        log("cache err " + str(e))
    try:
        pend = getattr(m, "_PENDING_ATTACK_HIT", None)
        if isinstance(pend, list):
            pend[0] = None
            log("cleared pending hit")
    except Exception as e:
        log("pending err " + str(e))
    log("OK")
except Exception as e:
    log("FAIL " + str(e))

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)
