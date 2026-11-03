# -*- coding: utf-8 -*-
"""Repair corrupted _fix_view_once, keep ensure_dungeon_pawn, wire call safely."""
from __future__ import print_function
import os
import re
import sys
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\repair_runtime_t218d.txt"
PATHS = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",
]
_lines = []

GOOD_VIEW = '''def _fix_view_once(world):
    if _VIEW_FIXED[0]:
        return
    _VIEW_FIXED[0] = True
    try:
        unreal.SystemLibrary.execute_console_command(world, "viewmode lit")
    except Exception:
        try:
            cls = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
            unreal.get_default_object(cls).execute_console_command(world, "viewmode lit", None)
        except Exception:
            pass
'''

BROKEN_VIEW = '''def ensure_dungeon_pawn(world)
    _fix_view_once(world):
    if _VIEW_FIXED[0]:
        return
    _VIEW_FIXED[0] = True
    try:
        unreal.SystemLibrary.execute_console_command(world, "viewmode lit")
    except Exception:
        try:
            cls = unreal.load_class(None, "/Script/Engine.KismetSystemLibrary")
            unreal.get_default_object(cls).execute_console_command(world, "viewmode lit", None)
        except Exception:
            pass
'''


def log(m):
    _lines.append(str(m))
    try:
        unreal.log("RepairT218d: " + str(m))
    except Exception:
        print(m)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


def repair(path):
    raw = open(path, "r", encoding="utf-8").read()
    raw = re.sub(r"GATE_RANGE\s*=\s*[0-9.]+", "GATE_RANGE = 280.0", raw, count=1)
    if BROKEN_VIEW in raw:
        raw = raw.replace(BROKEN_VIEW, GOOD_VIEW, 1)
        log("restored _fix_view_once in " + path)
    elif "def _fix_view_once(world):" in raw:
        log("_fix_view_once already ok in " + path)
    else:
        log("WARN no _fix_view_once pattern in " + path)

    if "def ensure_dungeon_pawn(world):" not in raw:
        log("FAIL missing ensure_dungeon_pawn def in " + path)
        return False

    # Wire call: unique context in _on_tick only
    needle = "        return\n    _fix_view_once(world)\n    pc = unreal.GameplayStatics.get_player_controller(world, 0)"
    repl = "        return\n    ensure_dungeon_pawn(world)\n    _fix_view_once(world)\n    pc = unreal.GameplayStatics.get_player_controller(world, 0)"
    if "    ensure_dungeon_pawn(world)\n    _fix_view_once(world)\n    pc = unreal.GameplayStatics" in raw:
        log("call already wired in " + path)
    elif needle in raw:
        raw = raw.replace(needle, repl, 1)
        log("wired ensure call in _on_tick in " + path)
    else:
        log("FAIL wire needle missing in " + path)
        # show nearby for debug
        idx = raw.find("def _on_tick")
        log("on_tick snippet=" + repr(raw[idx:idx+350]))
        return False

    open(path, "w", encoding="utf-8").write(raw)
    # syntax check
    try:
        compile(raw, path, "exec")
        log("SYNTAX_OK " + path)
    except SyntaxError as e:
        log("SYNTAX_FAIL " + path + " " + str(e))
        return False
    return True


def reload_mod():
    for p in (
        r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python",
        r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs",
    ):
        if p not in sys.path:
            sys.path.insert(0, p)
    import importlib
    if "shop_interact_runtime" in sys.modules:
        importlib.reload(sys.modules["shop_interact_runtime"])
        m = sys.modules["shop_interact_runtime"]
    else:
        m = __import__("shop_interact_runtime")
    log("GATE_RANGE=" + str(getattr(m, "GATE_RANGE", None)))
    log("has_ensure=" + str(hasattr(m, "ensure_dungeon_pawn")))


def main():
    log("=== repair_runtime_t218d ===")
    ok = True
    for p in PATHS:
        if not os.path.exists(p):
            log("missing " + p)
            ok = False
            continue
        if not repair(p):
            ok = False
    if ok:
        reload_mod()
    log("DONE ok=" + str(ok))
    flush()


main()
