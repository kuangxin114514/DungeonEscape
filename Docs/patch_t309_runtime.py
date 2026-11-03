# -*- coding: utf-8 -*-
from __future__ import print_function
import io

path = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
src = io.open(path, "r", encoding="utf-8").read()
orig = src

old_hdr = "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud."
new_hdr = (
    "# T278: after OpenLevel Hub<->Map_Dungeon1, clear HUD/enemy caches and recreate ensure_health_hud.\n"
    "# T309: GI_DungeonGame Gold/Inventory via player_meta helpers (OpenLevel-safe); dungeon exit E -> Map_Dungeon2.\n"
    "#       ClearProgress for new-save later. Map_Hub buildings untouched."
)
if "T309: GI_DungeonGame" not in src:
    if old_hdr in src:
        src = src.replace(old_hdr, new_hdr, 1)
        print("hdr ok")
    else:
        print("hdr MISSING")

old_levels = (
    'DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon1"\n'
    'HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"'
)
new_levels = (
    'DUNGEON_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon1"\n'
    'DUNGEON2_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon2"\n'
    'HUB_LEVEL = "/Game/Maps/Hub/Map_Hub"\n'
    "# T309 player meta (Gold + Inventory). Prefers live GI_DungeonGame props; else module+JSON.\n"
    "DEFAULT_GOLD = 100\n"
    '_PLAYER_META = {"gold": DEFAULT_GOLD, "inventory": [], "ready": False}\n'
    '_PLAYER_META_PATH = r"C:\\Users\\86178\\Documents\\Unreal Projects\\DungeonEscape\\Saved\\PlayerMeta.json"'
)
if "DUNGEON2_LEVEL" not in src:
    if old_levels in src:
        src = src.replace(old_levels, new_levels, 1)
        print("levels ok")
    else:
        print("levels MISSING")

META_BLOCK = r'''
def _gi_from_world(world_ctx):
    """Return live GameInstance (GI_DungeonGame) or None."""
    if world_ctx is None:
        return None
    try:
        return unreal.GameplayStatics.get_game_instance(world_ctx)
    except Exception:
        return None


def _meta_load_file():
    import json
    import os
    try:
        if os.path.isfile(_PLAYER_META_PATH):
            data = json.load(open(_PLAYER_META_PATH, "r", encoding="utf-8"))
            _PLAYER_META["gold"] = int(data.get("gold", DEFAULT_GOLD))
            inv = data.get("inventory", [])
            if not isinstance(inv, list):
                inv = []
            _PLAYER_META["inventory"] = [str(x) for x in inv]
            return True
    except Exception as e:
        _log("meta load file " + str(e))
    return False


def _meta_save_file():
    import json
    import os
    try:
        d = os.path.dirname(_PLAYER_META_PATH)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        json.dump(
            {"gold": int(_PLAYER_META["gold"]), "inventory": list(_PLAYER_META["inventory"])},
            open(_PLAYER_META_PATH, "w", encoding="utf-8"),
            ensure_ascii=False,
            indent=2,
        )
        return True
    except Exception as e:
        _log("meta save file " + str(e))
        return False


def _meta_pull_gi(gi):
    if gi is None:
        return False
    ok = False
    try:
        g = gi.get_editor_property("Gold")
        _PLAYER_META["gold"] = int(g)
        ok = True
    except Exception:
        pass
    try:
        inv = gi.get_editor_property("Inventory")
        _PLAYER_META["inventory"] = [str(x) for x in list(inv or [])]
        ok = True
    except Exception:
        pass
    return ok


def _meta_push_gi(gi):
    if gi is None:
        return False
    ok = False
    try:
        gi.set_editor_property("Gold", int(_PLAYER_META["gold"]))
        ok = True
    except Exception:
        pass
    try:
        gi.set_editor_property("Inventory", list(_PLAYER_META["inventory"]))
        ok = True
    except Exception:
        pass
    return ok


def ensure_player_meta(world_ctx=None):
    """Init Gold/Inventory once per session; sync GI if BP vars exist."""
    if not _PLAYER_META["ready"]:
        if not _meta_load_file():
            _PLAYER_META["gold"] = int(DEFAULT_GOLD)
            _PLAYER_META["inventory"] = []
        _PLAYER_META["ready"] = True
    gi = _gi_from_world(world_ctx)
    if gi is not None:
        _meta_pull_gi(gi)
        _meta_push_gi(gi)
    return _PLAYER_META


def get_gold(world_ctx=None):
    ensure_player_meta(world_ctx)
    return int(_PLAYER_META["gold"])


def set_gold(amount, world_ctx=None):
    ensure_player_meta(world_ctx)
    _PLAYER_META["gold"] = int(amount)
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    return _PLAYER_META["gold"]


def add_gold(delta, world_ctx=None):
    return set_gold(get_gold(world_ctx) + int(delta), world_ctx)


def spend_gold(cost, world_ctx=None):
    """Return True if spent; False if not enough."""
    cost = int(cost)
    g = get_gold(world_ctx)
    if g < cost:
        return False
    set_gold(g - cost, world_ctx)
    return True


def get_inventory(world_ctx=None):
    ensure_player_meta(world_ctx)
    return list(_PLAYER_META["inventory"])


def add_item(item_name, world_ctx=None):
    ensure_player_meta(world_ctx)
    _PLAYER_META["inventory"].append(str(item_name))
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    return list(_PLAYER_META["inventory"])


def clear_progress(world_ctx=None):
    """New-save wipe: gold back to DEFAULT_GOLD, inventory empty."""
    _PLAYER_META["gold"] = int(DEFAULT_GOLD)
    _PLAYER_META["inventory"] = []
    _PLAYER_META["ready"] = True
    _meta_push_gi(_gi_from_world(world_ctx))
    _meta_save_file()
    _log("clear_progress gold=%s inv=0" % _PLAYER_META["gold"])
    return True


'''

if "def ensure_player_meta(" not in src:
    needle = "def enter_dungeon(world_ctx):"
    if needle in src:
        src = src.replace(needle, META_BLOCK + needle, 1)
        print("meta helpers ok")
    else:
        print("enter_dungeon MISSING")

if "def enter_dungeon2(" not in src:
    marker = "def return_to_hub(world_ctx):"
    if marker not in src:
        print("return_to_hub MISSING")
    else:
        enter2 = (
            "def enter_dungeon2(world_ctx):\n"
            '    """OpenLevel to Map_Dungeon2 when E near Map_Dungeon1 stairs / exit behind skeleton."""\n'
            "    if world_ctx is None:\n"
            "        return False\n"
            "    close_shop(world_ctx)\n"
            '    _reset_ui_after_travel("enter_dungeon2")\n'
            "    _LAST_WORLD_KEY[0] = None\n"
            '    _print(world_ctx, u"进入地下城2层", (1.0, 0.85, 0.2, 1.0), 2.0)\n'
            "    level = DUNGEON2_LEVEL\n"
            "    try:\n"
            '        unreal.GameplayStatics.open_level(world_ctx, level, True, "")\n'
            '        _log("OpenLevel " + level)\n'
            "        return True\n"
            "    except Exception as e:\n"
            '        _log("OpenLevel dungeon2 fail " + str(e))\n'
            "    try:\n"
            '        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + level)\n'
            '        _log("console Open " + level)\n'
            "        return True\n"
            "    except Exception as e2:\n"
            '        _log("console Open dungeon2 fail " + str(e2))\n'
            '        _print(world_ctx, u"进2层失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)\n'
            "        return False\n\n\n"
        )
        src = src.replace(marker, enter2 + marker, 1)
        src = src.replace(
            '"""OpenLevel to Map_Hub when E near dungeon stairs exit."""',
            '"""OpenLevel to Map_Hub (true hub return — not the Map_Dungeon1 skeleton exit)."""',
            1,
        )
        print("enter_dungeon2 ok")

old_interact = (
    "    if hub_exit and _world_is_dungeon(world):\n"
    '        _log("E near dungeon exit -> return_to_hub")\n'
    "        return return_to_hub(world)"
)
new_interact = (
    "    if hub_exit and _world_is_dungeon(world):\n"
    '        _log("E near dungeon exit -> enter_dungeon2")\n'
    "        return enter_dungeon2(world)"
)
count = src.count(old_interact)
if count:
    src = src.replace(old_interact, new_interact)
    print("interact replace count", count)
else:
    print("interact pattern MISSING")
    idx = src.find("hub_exit and _world_is_dungeon")
    print("idx", idx)
    if idx >= 0:
        print(repr(src[idx : idx + 220]))

src = src.replace(
    "Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs -> Map_Hub.",
    "Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs -> Map_Dungeon2.",
)

if "ensure_player_meta(None)" not in src and "def bootstrap():" in src:
    src = src.replace(
        "def bootstrap():",
        "def bootstrap():\n"
        "    try:\n"
        "        ensure_player_meta(None)\n"
        "    except Exception as e:\n"
        '        _log("ensure_player_meta " + str(e))\n',
        1,
    )
    print("bootstrap meta ok")

if src == orig:
    print("NO CHANGES")
else:
    io.open(path + ".pre_t309", "w", encoding="utf-8").write(orig)
    io.open(path, "w", encoding="utf-8").write(src)
    print("WROTE", path, "len", len(src))