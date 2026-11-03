# -*- coding: utf-8 -*-
"""Reload shop_interact_runtime after Map_Dungeon1 OpenLevel patch."""
from __future__ import print_function
import importlib
import sys
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_dungeon_gate.txt"
_lines = []


def log(msg):
    s = str(msg)
    _lines.append(s)
    try:
        unreal.log("ReloadDungeonGate: " + s)
    except Exception:
        print(s)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


def main():
    log("=== reload_dungeon_gate Map_Dungeon1 ===")
    for path in (
        "/Game/Maps/Dungeon/Map_Dungeon1",
        "/Game/Maps/Dungeon/Map_Dungeon",
    ):
        try:
            exists = unreal.EditorAssetLibrary.does_asset_exist(path)
        except Exception as e:
            exists = "err:" + str(e)
        log("%s exists=%s" % (path, exists))
    mod_name = "shop_interact_runtime"
    try:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
            log("reloaded " + mod_name)
        else:
            __import__(mod_name)
            log("imported " + mod_name)
    except Exception as e:
        log("reload fail " + str(e))
        try:
            import shop_interact_runtime as m
            importlib.reload(m)
            log("force reload ok")
        except Exception as e2:
            log("force fail " + str(e2))
    try:
        import shop_interact_runtime as m
        log("has enter_dungeon=" + str(hasattr(m, "enter_dungeon")))
        log("has resolve=" + str(hasattr(m, "resolve_dungeon_level")))
        log("DUNGEON_LEVEL=" + str(getattr(m, "DUNGEON_LEVEL", None)))
        if hasattr(m, "resolve_dungeon_level"):
            log("resolved=" + str(m.resolve_dungeon_level()))
            log("DUNGEON_LEVEL_after=" + str(getattr(m, "DUNGEON_LEVEL", None)))
    except Exception as e:
        log("inspect fail " + str(e))
    log("DONE")
    flush()


main()
