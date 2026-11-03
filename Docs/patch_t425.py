# -*- coding: utf-8 -*-
from __future__ import print_function
path = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
text = open(path, "r", encoding="utf-8").read()
# backup
open(path + ".pre_t425", "w", encoding="utf-8").write(text)

old = """    _LAST_HINT_KEY[0] = None
    _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = False
    _NEAR_EXIT[0] = False
    _PREV_E[0] = False
    _PREV_ESC[0] = False
    _PREV_LMB[0] = False"""

new = """    _LAST_HINT_KEY[0] = None
    _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = False
    _NEAR_EXIT[0] = False
    # After OpenLevel, E/LMB are often still held. Treat as already-down so the
    # rising edge does not fire on the first dungeon tick (spawn is near HubReturn).
    _PREV_E[0] = True
    _PREV_ESC[0] = True
    _PREV_LMB[0] = True"""

if old not in text:
    raise SystemExit("block not found")
text = text.replace(old, new, 1)

# Also: never hub-return while actually on Map_Hub (belt and suspenders)
old2 = """def _world_is_dungeon(world):
    try:
        p = str(world.get_path_name())
        return (\"Map_Dungeon\" in p) or (\"UEDPIE_\" in p and \"Dungeon\" in p)
    except Exception:
        return False"""

new2 = """def _world_is_hub(world):
    try:
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Map_Hub\" in n or n.endswith(\"Hub\"):
            return True
    except Exception:
        pass
    try:
        p = str(world.get_path_name())
        return (\"Map_Hub\" in p) and (\"Map_Dungeon\" not in p.split(\"Map_Hub\")[-1] if False else \"Map_Hub\" in p and \"Dungeon\" not in p.replace(\"Map_Hub\", \"\"))
    except Exception:
        return False


def _world_is_dungeon(world):
    try:
        if _world_is_hub(world):
            return False
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Map_Dungeon\" in n:
            return True
        p = str(world.get_path_name())
        return (\"Map_Dungeon\" in p) or (\"UEDPIE_\" in p and \"Dungeon\" in p)
    except Exception:
        return False"""

# Simpler hub check - the above got messy. Rewrite cleanly.
new2 = """def _world_is_hub(world):
    try:
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Hub\" in n and \"Dungeon\" not in n:
            return True
    except Exception:
        pass
    try:
        p = str(world.get_path_name())
        return (\"Map_Hub\" in p) and (\"Map_Dungeon\" not in p)
    except Exception:
        return False


def _world_is_dungeon(world):
    try:
        if _world_is_hub(world):
            return False
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Map_Dungeon\" in n:
            return True
        p = str(world.get_path_name())
        return (\"Map_Dungeon\" in p) or (\"UEDPIE_\" in p and \"Dungeon\" in p)
    except Exception:
        return False"""

if old2 not in text:
    raise SystemExit("world_is_dungeon not found")
text = text.replace(old2, new2, 1)

# harden dungeon2/3 similarly
text = text.replace(
"""def _world_is_dungeon2(world):
    try:
        p = str(world.get_path_name())
        return (\"Map_Dungeon2\" in p)
    except Exception:
        return False""",
"""def _world_is_dungeon2(world):
    try:
        if _world_is_hub(world):
            return False
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Map_Dungeon2\" in n:
            return True
        p = str(world.get_path_name())
        return (\"Map_Dungeon2\" in p)
    except Exception:
        return False""",
1)

text = text.replace(
"""def _world_is_dungeon3(world):
    try:
        p = str(world.get_path_name())
        return (\"Map_Dungeon3\" in p)
    except Exception:
        return False""",
"""def _world_is_dungeon3(world):
    try:
        if _world_is_hub(world):
            return False
        n = str(unreal.GameplayStatics.get_current_level_name(world, True))
        if \"Map_Dungeon3\" in n:
            return True
        p = str(world.get_path_name())
        return (\"Map_Dungeon3\" in p)
    except Exception:
        return False""",
1)

# In handle_interact: if on hub, never return_to_hub
old3 = """    if hub_return and _world_is_dungeon2(world):
        _log(\"E near D2 up-stairs -> return_to_hub\")
        return return_to_hub(world)"""
new3 = """    if hub_return and _world_is_dungeon2(world) and (not _world_is_hub(world)):
        _log(\"E near D2 up-stairs -> return_to_hub\")
        return return_to_hub(world)"""
if old3 not in text:
    raise SystemExit("hub_return d2 block missing")
text = text.replace(old3, new3, 1)

old4 = """    if hub_return and _world_is_dungeon(world) and (not _world_is_dungeon2(world)):
        _log(\"E near spawn-back exit -> return_to_hub\")
        return return_to_hub(world)"""
new4 = """    if hub_return and _world_is_dungeon(world) and (not _world_is_dungeon2(world)) and (not _world_is_hub(world)):
        _log(\"E near spawn-back exit -> return_to_hub\")
        return return_to_hub(world)"""
if old4 not in text:
    raise SystemExit("hub_return d1 block missing")
text = text.replace(old4, new4, 1)

compile(text, path, "exec")
open(path, "w", encoding="utf-8").write(text)
print("patched OK")
print("PREV_E True", "_PREV_E[0] = True" in text)
print("world_is_hub", "def _world_is_hub" in text)