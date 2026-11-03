# -*- coding: utf-8 -*-
"""Hot-reload shop_interact_runtime after ATTACK_DAMAGE_DELAY=0.5 edit."""
from __future__ import print_function
import unreal
import importlib
import sys
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t305.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("ReloadT305: " + str(m))
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
    delay = getattr(m, "ATTACK_DAMAGE_DELAY", None)
    log("ATTACK_DAMAGE_DELAY=%s" % delay)
    log("ATTACK_DAMAGE=%s" % getattr(m, "ATTACK_DAMAGE", None))
    log("ENEMY_HP_BARS_ENABLED=%s" % getattr(m, "ENEMY_HP_BARS_ENABLED", None))
    try:
        text = open(dst, encoding="utf-8").read()
        if "ATTACK_DAMAGE_DELAY = 0.5" in text:
            log("file_tag=DELAY_0_5")
        elif "ATTACK_DAMAGE_DELAY = 1.0" in text:
            log("file_tag=DELAY_1_0")
        else:
            log("file_tag=OTHER")
    except Exception as e:
        log("file_tag=readerr " + str(e))
    try:
        pend = getattr(m, "_PENDING_ATTACK_HIT", None)
        if isinstance(pend, list):
            pend[0] = None
            log("cleared pending hit")
    except Exception as e:
        log("pending err " + str(e))
    if delay == 0.5 or delay == 0.5:
        log("OK")
    else:
        log("FAIL unexpected delay " + str(delay))
except Exception as e:
    log("FAIL " + str(e))

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("WROTE", OUT)
