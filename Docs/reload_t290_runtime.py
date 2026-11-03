# -*- coding: utf-8 -*-
"""Hot-reload shop_interact_runtime after T290 distance-scale enemy HP bars."""
from __future__ import print_function
import unreal
import importlib
import sys
import os
import shutil

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t290.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("ReloadT290: " + str(m))
    except Exception:
        print(m)

try:
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path:
        sys.path.insert(0, py)
    docs = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
    dst = os.path.join(py, "shop_interact_runtime.py")
    try:
        shutil.copy2(docs, dst)
        log("copied Docs -> Content/Python")
    except Exception as e:
        log("copy warn " + str(e))
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
    for name in (
        "ensure_enemy_health_bars",
        "_enemy_head_world_loc",
        "_enemy_bar_z_offset",
        "_enemy_bar_dist_scale",
        "_apply_enemy_bar_scale",
        "_pc_camera_world_loc",
        "_project_head_to_screen",
        "_purge_enemy_viewport_widgets",
    ):
        log("%s=%s" % (name, hasattr(m, name)))
    log("ENEMY_HP_BAR_Z_OFFSET=%s" % getattr(m, "ENEMY_HP_BAR_Z_OFFSET", None))
    log("ENEMY_HP_BAR_REF_DISTANCE=%s" % getattr(m, "ENEMY_HP_BAR_REF_DISTANCE", None))
    log("ENEMY_HP_BAR_MIN_SCALE=%s" % getattr(m, "ENEMY_HP_BAR_MIN_SCALE", None))
    log("ENEMY_HP_BAR_MAX_SCALE=%s" % getattr(m, "ENEMY_HP_BAR_MAX_SCALE", None))
    tag = None
    try:
        text = open(dst, encoding="utf-8").read()
        if "T290_DIST_SCALE" in text and "ENEMY_HP_BAR_REF_DISTANCE" in text:
            tag = "T290_DIST_SCALE"
        elif "ENEMY_HP_BAR_Z_OFFSET" in text or "T288_OFFSET" in text:
            tag = "T288_OFFSET"
        elif "T285_PROJECT_HUD" in text:
            tag = "T285_PROJECT_HUD"
        else:
            tag = "NO_T290"
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
