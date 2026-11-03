# -*- coding: utf-8 -*-
"""Reload shop_interact_runtime + force Lit/Game view. Run via remote_execution."""
from __future__ import print_function
import unreal
import sys
import importlib

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_and_fix_view.txt"
lines = []

def log(m):
    lines.append(str(m))
    try:
        unreal.log("RELOAD: " + str(m))
    except Exception:
        print(m)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def fix_view():
    world = None
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
    except Exception:
        pass
    cmds = [
        "viewmode lit",
        "show flag.Wireframe 0",
        "show flag.MeshEdges 0",
        "show flag.Collision 0",
        "show flag.CollisionVisibility 0",
        "show flag.CollisionPawn 0",
        "show flag.Bounds 0",
        "show flag.BSPVertices 0",
        "show flag.Brushes 0",
        "show flag.SelectionOutline 0",
        "show flag.Game 1",
    ]
    for c in cmds:
        try:
            unreal.SystemLibrary.execute_console_command(world, c, None)
            log("cmd " + c)
        except Exception as e:
            log("fail " + c + " " + str(e))
    for fn_name in ("editor_set_game_view", "set_game_view"):
        fn = getattr(unreal.EditorLevelLibrary, fn_name, None)
        if fn:
            try:
                fn(True)
                log(fn_name + "(True)")
            except Exception as e:
                log(str(e))

def reload_runtime():
    # Remove cached module so uclass may re-register (best-effort in UE4)
    for name in list(sys.modules.keys()):
        if "shop_interact" in name:
            try:
                del sys.modules[name]
                log("del module " + name)
            except Exception:
                pass
    try:
        import shop_interact_runtime
        importlib.reload(shop_interact_runtime)
        log("reloaded shop_interact_runtime")
        log("has lib=" + str(hasattr(shop_interact_runtime, "DE_HubInteractLib")))
    except Exception as e:
        log("reload err " + str(e))
        try:
            import shop_interact_runtime
            log("import ok after err")
        except Exception as e2:
            log("import fail " + str(e2))

log("=== reload_and_fix_view ===")
fix_view()
reload_runtime()
fix_view()
log("DONE — stop PIE, Alt+P, walk to yellow 按E, press E")
flush()
