# -*- coding: utf-8 -*-
"""Patch shop_interact_runtime: spawn-back exit -> Hub; skeleton/stairs exit -> Dungeon2."""
from __future__ import print_function
import os, shutil

SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
BAK = SRC + ".pre_t317_exits"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\patch_t317_exits.txt"
lines_log = []

def log(m):
    lines_log.append(str(m))
    print(m)

text = open(SRC, encoding="utf-8").read()
shutil.copyfile(SRC, BAK)
log("backup " + BAK)

old_scan = '''def scan_near(world, pawn_loc):
    """Return (shop_key, title, gate, hub_exit).
    Gate: Hub -> Map_Dungeon1. hub_exit: Map_Dungeon1 stairs -> Map_Dungeon2.
    """
    best = None
    best_d = 1e18
    gate = False
    best_gate_d = 1e18
    hub_exit = False
    best_exit_d = 1e18
    try:
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception:
        return None, None, False, False
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
        is_exit = (
            ("HubReturn" in tags)
            or ("DungeonExit" in tags)
            or ("HubExit" in tags)
            or lab.startswith("DungeonExit_")
            or lab.startswith("HubReturn_")
            or ("DungeonExit" in lab)
        )
        if is_shop and d < SHOP_RANGE and d < best_d:
            meta = _meta_for_actor(lab, tags)
            if meta:
                best_d = d
                best = meta
        if is_gate and d < GATE_RANGE and d < best_gate_d:
            best_gate_d = d
            gate = True
        if is_exit and d < EXIT_RANGE and d < best_exit_d:
            best_exit_d = d
            hub_exit = True
    if best:
        return best[0], best[1], gate, hub_exit
    return None, None, gate, hub_exit'''

new_scan = '''def _is_dungeon2_exit_marker(lab, tags):
    """Skeleton-side / stairs exit on Map_Dungeon1 -> Map_Dungeon2."""
    if ("ToDungeon2" in tags) or ("Dungeon2Exit" in tags) or ("Dungeon2" in tags):
        return True
    if ("ToDungeon2" in lab) or ("Dungeon2Exit" in lab):
        return True
    # Existing stairs marker east of skeleton
    if "Stairs" in lab:
        return True
    return False


def _is_hub_return_marker(lab, tags):
    """Spawn-back / hub-return exit on Map_Dungeon1 -> Map_Hub."""
    if _is_dungeon2_exit_marker(lab, tags):
        return False
    return (
        ("HubReturn" in tags)
        or ("HubExit" in tags)
        or ("DungeonExit" in tags)
        or lab.startswith("DungeonExit_")
        or lab.startswith("HubReturn_")
        or ("DungeonExit" in lab)
        or ("HubReturn" in lab)
    )


def scan_near(world, pawn_loc):
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

if old_scan not in text:
    log("FAIL old_scan not found")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
    raise SystemExit(2)
text = text.replace(old_scan, new_scan, 1)
log("patched scan_near")

# try_interact unpack + branch
old_try = '''    shop_key, title, gate, hub_exit = scan_near(world, pawn.get_actor_location())
    if shop_key and title:
        _NEAR_SHOP[0] = (shop_key, title)
    else:
        _NEAR_SHOP[0] = None
    _NEAR_GATE[0] = gate
    _NEAR_EXIT[0] = hub_exit
    # Dungeon stairs exit wins in Map_Dungeon1; hub gate wins over shop in Map_Hub.
    if hub_exit and _world_is_dungeon(world):
        _log("E near dungeon exit -> enter_dungeon2")
        return enter_dungeon2(world)
    if gate:'''

new_try = '''    shop_key, title, gate, hub_return, dungeon2_exit = scan_near(world, pawn.get_actor_location())
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
        return return_to_hub(world)
    if gate:'''

if old_try not in text:
    log("FAIL old_try not found")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
    raise SystemExit(3)
text = text.replace(old_try, new_try, 1)
log("patched try_interact")

old_hint = '''        shop_key, title, gate, hub_exit = scan_near(world, pawn.get_actor_location())
        if shop_key and title:
            _NEAR_SHOP[0] = (shop_key, title)
        else:
            _NEAR_SHOP[0] = None
        _NEAR_GATE[0] = gate
        _NEAR_EXIT[0] = hub_exit
        # Hint priority: dungeon exit > hub gate > shop
        if hub_exit and _world_is_dungeon(world):
            key = ("exit",)
        elif gate:
            key = ("gate",)
        elif shop_key and title:
            key = ("shop", shop_key)
        else:
            key = None
        if key is not None and key != _LAST_HINT_KEY[0]:
            if key[0] == "exit":
                _print(world, u"按 E 进入2层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "gate":
                _print(world, u"按 E 进入地下城", (1.0, 0.85, 0.2, 1.0), 2.0)
            else:
                _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 2.0)
        _LAST_HINT_KEY[0] = key'''

# File may have mojibake for Chinese; match more loosely by unique English structure
import re
pat_hint = re.compile(
    r"shop_key, title, gate, hub_exit = scan_near\(world, pawn\.get_actor_location\(\)\)\n"
    r"        if shop_key and title:\n"
    r"            _NEAR_SHOP\[0\] = \(shop_key, title\)\n"
    r"        else:\n"
    r"            _NEAR_SHOP\[0\] = None\n"
    r"        _NEAR_GATE\[0\] = gate\n"
    r"        _NEAR_EXIT\[0\] = hub_exit\n"
    r"        # Hint priority: dungeon exit > hub gate > shop\n"
    r"        if hub_exit and _world_is_dungeon\(world\):\n"
    r"            key = \(\"exit\",\)\n"
    r"        elif gate:\n"
    r"            key = \(\"gate\",\)\n"
    r"        elif shop_key and title:\n"
    r"            key = \(\"shop\", shop_key\)\n"
    r"        else:\n"
    r"            key = None\n"
    r"        if key is not None and key != _LAST_HINT_KEY\[0\]:\n"
    r"            if key\[0\] == \"exit\":\n"
    r"                _print\(world, u[^\n]+, \(0\.4, 0\.9, 1\.0, 1\.0\), 2\.0\)\n"
    r"            elif key\[0\] == \"gate\":\n"
    r"                _print\(world, u[^\n]+, \(1\.0, 0\.85, 0\.2, 1\.0\), 2\.0\)\n"
    r"            else:\n"
    r"                _print\(world, u[^\n]+ \+ str\(title\), \(0\.4, 1\.0, 0\.5, 1\.0\), 2\.0\)\n"
    r"        _LAST_HINT_KEY\[0\] = key",
    re.M,
)

new_hint = '''        shop_key, title, gate, hub_return, dungeon2_exit = scan_near(world, pawn.get_actor_location())
        if shop_key and title:
            _NEAR_SHOP[0] = (shop_key, title)
        else:
            _NEAR_SHOP[0] = None
        _NEAR_GATE[0] = gate
        _NEAR_EXIT[0] = bool(hub_return or dungeon2_exit)
        # Hint priority: dungeon2 exit > hub return > hub gate > shop
        if dungeon2_exit and _world_is_dungeon(world):
            key = ("exit_d2",)
        elif hub_return and _world_is_dungeon(world):
            key = ("exit_hub",)
        elif gate:
            key = ("gate",)
        elif shop_key and title:
            key = ("shop", shop_key)
        else:
            key = None
        if key is not None and key != _LAST_HINT_KEY[0]:
            if key[0] == "exit_d2":
                _print(world, u"按 E 进入2层", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "exit_hub":
                _print(world, u"按 E 返回主城", (0.4, 0.9, 1.0, 1.0), 2.0)
            elif key[0] == "gate":
                _print(world, u"按 E 进入地下城", (1.0, 0.85, 0.2, 1.0), 2.0)
            else:
                _print(world, u"按 E 打开" + str(title), (0.4, 1.0, 0.5, 1.0), 2.0)
        _LAST_HINT_KEY[0] = key'''

m = pat_hint.search(text)
if not m:
    log("FAIL hint block regex")
    # dump nearby for debug
    idx = text.find("Hint priority")
    log("hint idx=%s" % idx)
    if idx >= 0:
        log(repr(text[idx-200:idx+500]))
    open(OUT, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
    raise SystemExit(4)
text = pat_hint.sub(new_hint, text, count=1)
log("patched hint block")

# header comment tweak
text = text.replace(
    "# T309: GI_DungeonGame Gold/Inventory via player_meta helpers (OpenLevel-safe); dungeon exit E -> Map_Dungeon2.",
    "# T309: GI_DungeonGame Gold/Inventory via player_meta helpers (OpenLevel-safe).\n"
    "# T317: Map_Dungeon1 spawn-back exit E -> Map_Hub; skeleton/stairs exit E -> Map_Dungeon2.",
    1,
)
# also fix top comment if still says all exits to hub
text = text.replace(
    "# Map_Dungeon1: near DungeonExit -> OpenLevel Map_Hub; LMB plays 1H Chop.",
    "# Map_Dungeon1: spawn-back DungeonExit -> Map_Hub; stairs/skeleton exit -> Map_Dungeon2; LMB plays 1H Chop.",
    1,
)

# ensure no leftover 4-tuple unpack
if "hub_exit = scan_near" in text or ", hub_exit =" in text:
    log("WARN still has hub_exit unpack")
else:
    log("no leftover hub_exit unpack")

# mark version tag
if "T317_SPLIT_EXITS" not in text:
    text = text.replace("T313_GOLD_RIGHT", "T313_GOLD_RIGHT T317_SPLIT_EXITS", 1)
    log("tagged T317_SPLIT_EXITS")

open(SRC, "w", encoding="utf-8").write(text)
log("wrote " + SRC)
open(OUT, "w", encoding="utf-8").write("\n".join(lines_log) + "\n")
print("OK")