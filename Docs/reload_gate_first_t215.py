# -*- coding: utf-8 -*-
"""Deploy + reload shop_interact_runtime with gate-first priority (t215/t216)."""
from __future__ import print_function
import importlib
import os
import shutil
import sys
import unreal

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_gate_first_t215.txt"
SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py"
DST = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
lines = []

def L(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("GateFirst: " + s)
    except Exception:
        print(s)

def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def main():
    L("=== reload_gate_first_t215 ===")
    try:
        if os.path.isfile(SRC):
            os.makedirs(os.path.dirname(DST), exist_ok=True)
            shutil.copy2(SRC, DST)
            L("copied Docs -> Content/Python")
        else:
            L("SRC missing: " + SRC)
    except Exception as e:
        L("copy fail " + str(e))

    # ensure Content/Python on sys.path
    py_dir = os.path.dirname(DST)
    if py_dir not in sys.path:
        sys.path.insert(0, py_dir)
        L("sys.path insert " + py_dir)

    mod_name = "shop_interact_runtime"
    try:
        if mod_name in sys.modules:
            m = importlib.reload(sys.modules[mod_name])
            L("reloaded " + mod_name)
        else:
            m = __import__(mod_name)
            L("imported " + mod_name)
    except Exception as e:
        L("import/reload fail " + str(e))
        flush()
        return

    L("SHOP_RANGE=" + str(getattr(m, "SHOP_RANGE", None)))
    L("GATE_RANGE=" + str(getattr(m, "GATE_RANGE", None)))
    L("DUNGEON_LEVEL=" + str(getattr(m, "DUNGEON_LEVEL", None)))
    L("has enter_dungeon=" + str(hasattr(m, "enter_dungeon")))
    L("has handle_interact=" + str(hasattr(m, "handle_interact")))

    # verify source markers
    try:
        body = open(DST, encoding="utf-8", errors="replace").read()
        L("marker_V14=" + str("SPLIT_WBP_V14_GATE_FIRST" in body))
        L("marker_gate_first_log=" + str("E near gate -> enter_dungeon" in body))
        L("marker_GateTrigger=" + str("GateTrigger" in body))
        L("marker_shop320=" + str("SHOP_RANGE = 320.0" in body))
    except Exception as e:
        L("read dst fail " + str(e))

    # re-bootstrap tick
    try:
        if hasattr(m, "bootstrap"):
            m.bootstrap()
            L("bootstrap ok")
        else:
            L("no bootstrap")
    except Exception as e:
        L("bootstrap fail " + str(e))

    # verify gate actors in editor world (labels only; no building edits)
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        L("editor_world=" + world.get_path_name())
        gates = []
        shops = []
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            lab = a.get_actor_label() or ""
            tags = []
            try:
                tags = [str(t) for t in list(a.get_editor_property("tags"))]
            except Exception:
                try:
                    tags = [str(t) for t in list(a.tags)]
                except Exception:
                    tags = []
            loc = a.get_actor_location()
            is_gate = ("HubGate" in lab) or ("GateTrigger" in lab) or ("DungeonEntrance" in lab) or ("GateInteract" in tags) or ("DungeonGate" in tags)
            is_shop = lab.startswith("HubShop_") or lab.startswith("ShopTrigger_") or ("ShopInteract" in tags)
            if is_gate:
                gates.append("%s tags=%s loc=(%.0f,%.0f,%.0f)" % (lab, tags, loc.x, loc.y, loc.z))
            if is_shop:
                shops.append("%s tags=%s loc=(%.0f,%.0f,%.0f)" % (lab, tags, loc.x, loc.y, loc.z))
        L("gate_count=" + str(len(gates)))
        for g in gates:
            L("GATE " + g)
        L("shop_count=" + str(len(shops)))
        for s in shops:
            L("SHOP " + s)
        # distance matrix shop->gate
        import math
        def dist(a, b):
            return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)
        gate_actors = []
        shop_actors = []
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            lab = a.get_actor_label() or ""
            tags = []
            try:
                tags = [str(t) for t in list(a.get_editor_property("tags"))]
            except Exception:
                tags = []
            if ("HubGate" in lab) or ("GateTrigger" in lab) or ("DungeonEntrance" in lab) or ("GateInteract" in tags) or ("DungeonGate" in tags):
                gate_actors.append(a)
            if lab.startswith("HubShop_") or lab.startswith("ShopTrigger_") or ("ShopInteract" in tags):
                shop_actors.append(a)
        for s in shop_actors:
            for g in gate_actors:
                d = dist(s.get_actor_location(), g.get_actor_location())
                L("dist %s -> %s = %.1f (shop_r=320 gate_r=520)" % (s.get_actor_label(), g.get_actor_label(), d))
    except Exception as e:
        L("actor scan fail " + str(e))

    L("Map_Dungeon=" + str(unreal.EditorAssetLibrary.does_asset_exist("/Game/Maps/Dungeon/Map_Dungeon")))
    L("DONE")
    flush()

main()
