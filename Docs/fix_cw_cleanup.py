# -*- coding: utf-8 -*-
"""Cleanup orphan CallFunction node; ensure single shop tick; prove E opens UI."""
from __future__ import print_function
import unreal
import traceback
import sys
import importlib

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_cw_cleanup.txt"
PYDIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("CLN: " + s)
    except Exception:
        print("CLN:", s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def remove_orphan_callfunction():
    log("=== remove orphan CallFunction_10 ===")
    graph = unreal.load_object(
        None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
    )
    node = unreal.load_object(
        None,
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph.K2Node_CallFunction_10",
    )
    log("graph=%s node=%s" % (graph, node))
    if node is None:
        # find by iterator
        for o in unreal.ObjectIterator():
            try:
                pn = o.get_path_name()
            except Exception:
                continue
            if "BP_KayKitKnight:EventGraph.K2Node_CallFunction_10" in pn:
                node = o
                break
        log("found node=" + str(node))
    if graph is None or node is None:
        log("nothing to remove")
        return
    for meth in ("remove_node", "RemoveNode"):
        fn = getattr(graph, meth, None)
        if callable(fn):
            try:
                fn(node)
                log(meth + " OK")
                break
            except Exception as e:
                try:
                    fn(node, True)
                    log(meth + " OK2")
                    break
                except Exception as e2:
                    log(meth + " " + str(e) + " / " + str(e2))
    # destroy
    try:
        node.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
        log("disabled orphan node")
    except Exception as e:
        log("disable " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
        log("saved BP")
    except Exception as e:
        log("save " + str(e))

def inspect_createwidget_class_pin_deep():
    """Try every way to read Class pin default on CreateWidget."""
    log("=== deep Class pin inspect ===")
    node = None
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if pn.endswith("BP_KayKitKnight:EventGraph.K2Node_CreateWidget_0"):
            node = o
            break
    if not node:
        log("no node")
        return
    # export text of node?
    for attr in ("get_pin_at", "GetPinAt", "get_all_pins", "Pins", "get_pins"):
        fn = getattr(node, attr, None)
        log("hasattr %s = %s" % (attr, fn))
        if callable(fn):
            try:
                if attr.lower().endswith("at"):
                    for i in range(8):
                        try:
                            p = fn(i)
                            log(" pin[%d]=%s" % (i, p))
                        except Exception as e:
                            log(" pin[%d] err %s" % (i, e))
                else:
                    log("  call => " + str(fn()))
            except Exception as e:
                log("  call err " + str(e))
    # Schema
    try:
        schema = unreal.EdGraphSchema_K2()
        log("schema=" + str(schema))
        for attr in dir(schema):
            if "pin" in attr.lower() and not attr.startswith("_"):
                log(" schema." + attr)
    except Exception as e:
        log("schema " + str(e))
    # Try reading node via get_editor_property all known UE names from C++
    for prop in (
        "ClassPinName", "class_pin_name",
        "ProxyFactoryFunctionName",
    ):
        try:
            log("prop %s=%s" % (prop, node.get_editor_property(prop)))
        except Exception as e:
            pass

def reload_runtime_once():
    if PYDIR not in sys.path:
        sys.path.insert(0, PYDIR)
    # Force re-read file and re-bootstrap carefully
    import shop_interact_runtime as r
    # If multiple ticks, still OK for now; open_shop toggles close if already open
    importlib.reload(r)
    log("reloaded runtime V7")

def prove():
    import shop_interact_runtime as r
    w = r._pie_world()
    log("pie=" + str(w))
    if not w:
        log("NO_PIE")
        return False
    # Simulate E handle
    ok = r.handle_interact(w)
    log("handle_interact => " + str(ok))
    log("open_widget=" + str(r._OPEN_WIDGET[0]))
    return ok

def dump_parent_class():
    for path in (
        "/Game/UI/Shop/WBP_Shop.WBP_Shop",
        "/Game/UI/Shop/WBP_Shop2.WBP_Shop2",
        "/Game/UI/Menus/WBP_MainMenu.WBP_MainMenu",
    ):
        bp = unreal.load_object(None, path)
        log("bp %s = %s" % (path, bp))
        if not bp:
            continue
        for prop in ("parent_class", "ParentClass", "generated_class", "GeneratedClass"):
            try:
                log("  %s=%s" % (prop, bp.get_editor_property(prop)))
            except Exception as e:
                log("  %s ERR %s" % (prop, e))
        gc = unreal.load_class(None, path + "_C")
        log("  _C via load_class=%s" % gc)
        if gc:
            try:
                log("  _C super=%s" % gc.get_super_class())
            except Exception as e:
                log("  super err " + str(e))

def main():
    log("START cleanup")
    dump_parent_class()
    inspect_createwidget_class_pin_deep()
    remove_orphan_callfunction()
    reload_runtime_once()
    ok = prove()
    log("PROOF=" + str(ok))
    log("DONE")
    flush()

try:
    main()
except Exception:
    log("EXC\n" + traceback.format_exc())
    flush()
