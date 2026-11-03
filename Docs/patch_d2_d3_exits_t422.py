# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
raw = io.open(p, encoding="utf-8").read().replace("\r\n", "\n")

# 1) Fix dungeon2 marker: Stairs alone OK for D1, but not HubReturn/ToDungeon3
old_d2 = '''def _is_dungeon2_exit_marker(lab, tags):
    """Skeleton-side / stairs exit on Map_Dungeon1 -> Map_Dungeon2."""
    if ("ToDungeon2" in tags) or ("Dungeon2Exit" in tags) or ("Dungeon2" in tags):
        return True
    if ("ToDungeon2" in lab) or ("Dungeon2Exit" in lab):
        return True
    # Existing stairs marker east of skeleton
    if "Stairs" in lab:
        return True
    return False'''
new_d2 = '''def _is_dungeon2_exit_marker(lab, tags):
    """Skeleton-side / stairs exit on Map_Dungeon1 -> Map_Dungeon2."""
    if ("HubReturn" in lab) or ("ToDungeon3" in lab) or ("HubReturn" in tags) or ("ToDungeon3" in tags):
        return False
    if ("ToDungeon2" in tags) or ("Dungeon2Exit" in tags) or ("Dungeon2" in tags):
        return True
    if ("ToDungeon2" in lab) or ("Dungeon2Exit" in lab):
        return True
    # Existing stairs marker east of skeleton (Map_Dungeon1)
    if "Stairs" in lab:
        return True
    return False


def _is_dungeon3_exit_marker(lab, tags):
    """Map_Dungeon2 down-stairs -> Map_Dungeon3."""
    return (
        ("ToDungeon3" in tags)
        or ("Dungeon3Exit" in tags)
        or ("ToDungeon3" in lab)
        or ("Dungeon3Exit" in lab)
    )


def _world_is_dungeon2(world):
    try:
        p = str(world.get_path_name())
        return ("Map_Dungeon2" in p)
    except Exception:
        return False


def _world_is_dungeon3(world):
    try:
        p = str(world.get_path_name())
        return ("Map_Dungeon3" in p)
    except Exception:
        return False'''
if old_d2 not in raw:
    print("D2_MARKER_MISSING")
else:
    raw = raw.replace(old_d2, new_d2, 1)
    print("markers_ok")

# 2) Extend scan_near return to include dungeon3_exit
old_scan_doc = '''def scan_near(world, pawn_loc):
    """Return (shop_key, title, gate, hub_return, dungeon2_exit).
    Gate: Hub -> Map_Dungeon1.
    hub_return: Map_Dungeon1 spawn-back exit -> Map_Hub.
    dungeon2_exit: Map_Dungeon1 skeleton/stairs exit -> Map_Dungeon2.
    """
    best = None
    best_d = 1e18
    gate = False
    best_gate_d = 1e18
    hub_return = False
    best_hub_d = 1e18
    dungeon2_exit = False
    best_d2_d = 1e18
    try:
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception:
        return None, None, False, False, False
    for actor in actors:
        try:
            loc = actor.get_actor_location()
        except Exception:
            continue
        d = _dist(pawn_loc, loc)
        tags = _tags(actor)
        lab = _label(actor)
        is_shop = ("ShopInteract" in tags) or lab.startswith("HubShop_") or lab.startswith("ShopTrigger_")
        is_gate = (
            ("DungeonGate" in tags)
            or ("GateInteract" in tags)
            or ("HubGate" in lab)
            or ("GateTrigger" in lab)
            or ("DungeonEntrance" in lab)
            or lab.startswith("GateTrigger_")
        )
        is_d2 = _is_dungeon2_exit_marker(lab, tags)
        is_hub = _is_hub_return_marker(lab, tags)
        if is_shop and d < SHOP_RANGE and d < best_d:
            meta = _meta_for_actor(lab, tags)
            if meta:
                best_d = d
                best = meta
        if is_gate and d < GATE_RANGE and d < best_gate_d:
            best_gate_d = d
            gate = True
        if is_d2 and d < EXIT_RANGE and d < best_d2_d:
            best_d2_d = d
            dungeon2_exit = True
        if is_hub and d < EXIT_RANGE and d < best_hub_d:
            best_hub_d = d
            hub_return = True
    if best:
        return best[0], best[1], gate, hub_return, dungeon2_exit
    return None, None, gate, hub_return, dungeon2_exit'''

new_scan = '''def scan_near(world, pawn_loc):
    """Return (shop_key, title, gate, hub_return, dungeon2_exit, dungeon3_exit).
    Gate: Hub -> Map_Dungeon1.
    hub_return: Map_Dungeon1 spawn-back / Map_Dungeon2 up-stairs -> Map_Hub.
    dungeon2_exit: Map_Dungeon1 skeleton/stairs exit -> Map_Dungeon2.
    dungeon3_exit: Map_Dungeon2 down-stairs -> Map_Dungeon3.
    """
    best = None
    best_d = 1e18
    gate = False
    best_gate_d = 1e18
    hub_return = False
    best_hub_d = 1e18
    dungeon2_exit = False
    best_d2_d = 1e18
    dungeon3_exit = False
    best_d3_d = 1e18
    try:
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception:
        return None, None, False, False, False, False
    for actor in actors:
        try:
            loc = actor.get_actor_location()
        except Exception:
            continue
        d = _dist(pawn_loc, loc)
        tags = _tags(actor)
        lab = _label(actor)
        is_shop = ("ShopInteract" in tags) or lab.startswith("HubShop_") or lab.startswith("ShopTrigger_")
        is_gate = (
            ("DungeonGate" in tags)
            or ("GateInteract" in tags)
            or ("HubGate" in lab)
            or ("GateTrigger" in lab)
            or ("DungeonEntrance" in lab)
            or lab.startswith("GateTrigger_")
        )
        is_d3 = _is_dungeon3_exit_marker(lab, tags)
        is_d2 = _is_dungeon2_exit_marker(lab, tags)
        is_hub = _is_hub_return_marker(lab, tags)
        if is_shop and d < SHOP_RANGE and d < best_d:
            meta = _meta_for_actor(lab, tags)
            if meta:
                best_d = d
                best = meta
        if is_gate and d < GATE_RANGE and d < best_gate_d:
            best_gate_d = d
            gate = True
        if is_d3 and d < EXIT_RANGE and d < best_d3_d:
            best_d3_d = d
            dungeon3_exit = True
        if is_d2 and d < EXIT_RANGE and d < best_d2_d:
            best_d2_d = d
            dungeon2_exit = True
        if is_hub and d < EXIT_RANGE and d < best_hub_d:
            best_hub_d = d
            hub_return = True
    if best:
        return best[0], best[1], gate, hub_return, dungeon2_exit, dungeon3_exit
    return None, None, gate, hub_return, dungeon2_exit, dungeon3_exit'''

if old_scan_doc not in raw:
    print("SCAN_MISSING")
else:
    raw = raw.replace(old_scan_doc, new_scan, 1)
    print("scan_ok")

# 3) Add DUNGEON3_LEVEL + enter_dungeon3
if "DUNGEON3_LEVEL" not in raw:
    raw = raw.replace(
        'DUNGEON2_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon2"',
        'DUNGEON2_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon2"\nDUNGEON3_LEVEL = "/Game/Maps/Dungeon/Map_Dungeon3"',
        1,
    )
    print("level_const")

old_enter2_end = '''def return_to_hub(world_ctx):
    """OpenLevel to Map_Hub (true hub return — not the Map_Dungeon1 skeleton exit)."""'''
enter3 = '''def enter_dungeon3(world_ctx):
    """OpenLevel to Map_Dungeon3 when E near Map_Dungeon2 down-stairs."""
    if world_ctx is None:
        return False
    close_shop(world_ctx)
    _reset_ui_after_travel("enter_dungeon3")
    _LAST_WORLD_KEY[0] = None
    _print(world_ctx, u"进入地下城3层", (1.0, 0.85, 0.2, 1.0), 2.0)
    level = DUNGEON3_LEVEL
    try:
        unreal.GameplayStatics.open_level(world_ctx, level, True, "")
        _log("OpenLevel " + level)
        return True
    except Exception as e:
        _log("OpenLevel dungeon3 fail " + str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world_ctx, "Open " + level)
        _log("console Open " + level)
        return True
    except Exception as e2:
        _log("console Open dungeon3 fail " + str(e2))
        _print(world_ctx, u"进3层失败: " + str(e2), (1.0, 0.3, 0.3, 1.0), 3.0)
        return False


def return_to_hub(world_ctx):
    """OpenLevel to Map_Hub (true hub return — not the Map_Dungeon1 skeleton exit)."""'''
if "def enter_dungeon3(" not in raw:
    if old_enter2_end not in raw:
        print("RETURN_HUB_MISSING")
    else:
        raw = raw.replace(old_enter2_end, enter3, 1)
        print("enter3_ok")
else:
    print("enter3_exists")

# 4) Patch try_interact unpack + routing
# Replace all scan_near unpacks of 5-tuple with 6-tuple carefully
raw2 = raw
# interact E handler
old_e = '''    shop_key, title, gate, hub_return, dungeon2_exit = scan_near(world, pawn.get_actor_location())
    if shop_key and title:
        _NEAR_SHOP[0] = (shop_key, title)
    else:
        _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = gate
    _NEAR_EXIT[0] = bool(hub_return or dungeon2_exit)
    # Map_Dungeon1: skeleton/stairs -> Dungeon2; spawn-back -> Hub; Hub gate -> Dungeon1.
    if dungeon2_exit and _world_is_dungeon(world):
        _log("E near skeleton/stairs exit -> enter_dungeon2")
        return enter_dungeon2(world)
    if hub_return and _world_is_dungeon(world):
        _log("E near spawn-back exit -> return_to_hub")
        return return_to_hub(world)'''
new_e = '''    shop_key, title, gate, hub_return, dungeon2_exit, dungeon3_exit = scan_near(world, pawn.get_actor_location())
    if shop_key and title:
        _NEAR_SHOP[0] = (shop_key, title)
    else:
        _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = gate
    _NEAR_EXIT[0] = bool(hub_return or dungeon2_exit or dungeon3_exit)
    # Map_Dungeon2: up-stairs -> Hub; down-stairs -> Dungeon3
    if dungeon3_exit and _world_is_dungeon2(world):
        _log("E near D2 down-stairs -> enter_dungeon3")
        return enter_dungeon3(world)
    if hub_return and _world_is_dungeon2(world):
        _log("E near D2 up-stairs -> return_to_hub")
        return return_to_hub(world)
    # Map_Dungeon1: skeleton/stairs -> Dungeon2; spawn-back -> Hub; Hub gate -> Dungeon1.
    if dungeon2_exit and _world_is_dungeon(world) and (not _world_is_dungeon2(world)) and (not _world_is_dungeon3(world)):
        _log("E near skeleton/stairs exit -> enter_dungeon2")
        return enter_dungeon2(world)
    if hub_return and _world_is_dungeon(world) and (not _world_is_dungeon2(world)):
        _log("E near spawn-back exit -> return_to_hub")
        return return_to_hub(world)'''
if old_e not in raw2:
    print("E_HANDLER_MISSING")
else:
    raw2 = raw2.replace(old_e, new_e, 1)
    print("e_handler_ok")

# tick hint unpack - find and patch
old_tick = '''        shop_key, title, gate, hub_return, dungeon2_exit = scan_near(world, pawn.get_actor_location())'''
new_tick = '''        shop_key, title, gate, hub_return, dungeon2_exit, dungeon3_exit = scan_near(world, pawn.get_actor_location())'''
c = raw2.count(old_tick)
raw2 = raw2.replace(old_tick, new_tick)
print("tick_unpack", c)

# near exit flag in tick
raw2 = raw2.replace(
    '_NEAR_EXIT[0] = bool(hub_return or dungeon2_exit)',
    '_NEAR_EXIT[0] = bool(hub_return or dungeon2_exit or dungeon3_exit)',
)
# hint priority block
old_hint = '''        if dungeon2_exit and _world_is_dungeon(world):
            key = ("exit_d2",)
        elif hub_return and _world_is_dungeon(world):
            key = ("exit_hub",)'''
# read more context from file for hints
if old_hint in raw2:
    new_hint = '''        if dungeon3_exit and _world_is_dungeon2(world):
            key = ("exit_d3",)
        elif hub_return and _world_is_dungeon2(world):
            key = ("exit_hub_d2",)
        elif dungeon2_exit and _world_is_dungeon(world) and (not _world_is_dungeon2(world)):
            key = ("exit_d2",)
        elif hub_return and _world_is_dungeon(world):
            key = ("exit_hub",)'''
    raw2 = raw2.replace(old_hint, new_hint, 1)
    print("hint_ok")
else:
    print("HINT_MISSING")

io.open(p, "w", encoding="utf-8", newline="\n").write(raw2)
compile(raw2, p, "exec")
print("syntax_ok")
