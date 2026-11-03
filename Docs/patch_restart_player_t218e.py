# -*- coding: utf-8 -*-
"""Prefer GameMode.restart_player in ensure_dungeon_pawn."""
from __future__ import print_function
import os, sys, unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_restart_player_t218e.txt"
PATHS = [
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py",
    r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",
]
_lines = []

OLD = '''    if _DUNGEON_PAWN_TRIED[0]:
        return False
    _DUNGEON_PAWN_TRIED[0] = True
    cls = unreal.load_class(None, _BP_KNIGHT)
'''

NEW = '''    if _DUNGEON_PAWN_TRIED[0]:
        return False
    _DUNGEON_PAWN_TRIED[0] = True
    # Prefer RestartPlayer: OpenLevel PIE often skips it even when GM/PlayerStart are set.
    try:
        gm = unreal.GameplayStatics.get_game_mode(world)
        if gm is not None:
            gm.restart_player(pc)
            try:
                if pc.get_controlled_pawn() is not None:
                    _log("ensure_dungeon_pawn: RestartPlayer ok")
                    _print(world, u"地下城角色已就绪", (0.3, 1.0, 0.5, 1.0), 2.0)
                    return True
            except Exception:
                pass
    except Exception as e:
        _log("ensure_dungeon_pawn RestartPlayer " + str(e))
    # Fallback: possess already-placed Dungeon_PlayerPawn if present
    try:
        knight_cls = unreal.load_class(None, _BP_KNIGHT)
        if knight_cls:
            for a in unreal.GameplayStatics.get_all_actors_of_class(world, knight_cls):
                try:
                    pc.possess(a)
                    _log("ensure_dungeon_pawn: possessed placed " + str(a))
                    _print(world, u"地下城角色已就绪", (0.3, 1.0, 0.5, 1.0), 2.0)
                    return True
                except Exception:
                    continue
    except Exception as e:
        _log("ensure_dungeon_pawn placed possess " + str(e))
    cls = unreal.load_class(None, _BP_KNIGHT)
'''


def log(m):
    _lines.append(str(m))
    try:
        unreal.log("PatchRestartT218e: " + str(m))
    except Exception:
        print(m)


def main():
    log("=== patch_restart_player_t218e ===")
    for path in PATHS:
        raw = open(path, "r", encoding="utf-8").read()
        if "ensure_dungeon_pawn: RestartPlayer ok" in raw:
            log("already patched " + path)
            continue
        if OLD not in raw:
            log("OLD block missing " + path)
            continue
        raw = raw.replace(OLD, NEW, 1)
        compile(raw, path, "exec")
        open(path, "w", encoding="utf-8").write(raw)
        log("patched SYNTAX_OK " + path)
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
    log("GATE_RANGE=" + str(m.GATE_RANGE))
    log("has_ensure=" + str(hasattr(m, "ensure_dungeon_pawn")))
    log("DONE")
    open(OUT, "w", encoding="utf-8").write("\n".join(_lines) + "\n")


main()
