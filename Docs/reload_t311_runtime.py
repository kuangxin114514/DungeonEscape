# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
import importlib
import sys

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t311.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("T311RL: " + str(m))
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
    for name in ("ensure_gold_hud", "get_gold", "GOLD_WBP_PATHS", "DEFAULT_GOLD"):
        log("%s=%s" % (name, getattr(m, name, "MISSING")))
    log("WBP_PlayerGold exists=%s" % unreal.EditorAssetLibrary.does_asset_exist("/Game/UI/HUD/WBP_PlayerGold"))
    try:
        m.ensure_player_meta(None)
        log("gold=%s" % m.get_gold(None))
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