# -*- coding: utf-8 -*-
"""Wire ensure_dungeon_pawn(world) into _on_tick; verify GATE_RANGE=280."""
from __future__ import print_function
import os
import sys
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\wire_ensure_dungeon_pawn_t218c.txt"
PATHS = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",
]
_lines = []


def log(m):
    _lines.append(str(m))
    try:
        unreal.log("WireEnsureT218c: " + str(m))
    except Exception:
        print(m)


def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


def patch(path):
    raw = open(path, "r", encoding="utf-8").read()
    if "GATE_RANGE = 280.0" not in raw:
        import re
        raw = re.sub(r"GATE_RANGE\s*=\s*[0-9.]+", "GATE_RANGE = 280.0", raw, count=1)
        log("forced GATE_RANGE=280 in " + path)
    # Look for an actual call line (indented), not the def
    if "\n    ensure_dungeon_pawn(world)\n" in raw or "\n\tensure_dungeon_pawn(world)\n" in raw:
        log("call already wired in " + path)
    else:
        if "_fix_view_once(world)" in raw:
            raw = raw.replace(
                "_fix_view_once(world)",
                "ensure_dungeon_pawn(world)\n    _fix_view_once(world)",
                1,
            )
            log("wired call before _fix_view_once in " + path)
        elif "world = _pie_world()" in raw:
            # fallback: after None check block - insert after first successful world use
            needle = "    if world is None:\n        _PREV_E[0] = False\n        _PREV_ESC[0] = False\n        _LAST_HINT_KEY[0] = None\n        return\n"
            if needle in raw:
                raw = raw.replace(needle, needle + "    ensure_dungeon_pawn(world)\n", 1)
                log("wired call after world None-check in " + path)
            else:
                log("FAIL find insert point in " + path)
                return False
        else:
            log("FAIL no insert point in " + path)
            return False
    if "def ensure_dungeon_pawn" not in raw:
        log("FAIL ensure_dungeon_pawn def missing in " + path)
        return False
    open(path, "w", encoding="utf-8").write(raw)
    log("saved " + path)
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
    # show source has call
    src = open(PATHS[1], "r", encoding="utf-8").read()
    log("content_has_call_line=" + str("\n    ensure_dungeon_pawn(world)\n" in src))


def main():
    log("=== wire_ensure_dungeon_pawn_t218c ===")
    for p in PATHS:
        if os.path.exists(p):
            patch(p)
        else:
            log("missing " + p)
    reload_mod()
    log("DONE")
    flush()


main()
