# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
import importlib
import sys
import os

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t309.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("T309RL: " + str(m))
    except Exception:
        print(m)

def main():
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path:
        sys.path.insert(0, py)
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
        log("reloaded")
    else:
        import shop_interact_runtime as m
        log("imported")
    for name in ("DUNGEON2_LEVEL", "DEFAULT_GOLD", "enter_dungeon2", "get_gold", "spend_gold", "add_item", "clear_progress", "ensure_player_meta"):
        log("%s=%s" % (name, getattr(m, name, "MISSING")))
    # confirm map exists
    log("Map_Dungeon2 exists=%s" % unreal.EditorAssetLibrary.does_asset_exist("/Game/Maps/Dungeon/Map_Dungeon2"))
    log("GI exists=%s" % unreal.EditorAssetLibrary.does_asset_exist("/Game/Core/GameFlow/GI_DungeonGame"))
    try:
        m.ensure_player_meta(None)
        log("gold=%s inv=%s" % (m.get_gold(None), m.get_inventory(None)))
    except Exception as e:
        log("meta err " + str(e))
    fn = getattr(m, "bootstrap", None)
    if callable(fn):
        try:
            fn()
            log("bootstrap ok")
        except Exception as e:
            log("bootstrap err " + str(e))
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("WROTE", OUT)

main()