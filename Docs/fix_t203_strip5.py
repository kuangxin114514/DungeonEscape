# -*- coding: utf-8 -*-
"""t203 strip5: hard-remove known Interact/CreateWidget/Hello nodes by path name.
Minimal logging so remote_execution JSON does not truncate.
"""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t203_strip5.txt"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
EG = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
# From user's Interact->Hello/CreateWidget/IsValid/AddToViewport/SetInputMode chain
DROP_NAMES = set([
    "K2Node_InputAction_0",      # Interact (user-added)
    "K2Node_CreateWidget_0",
    "K2Node_CallFunction_2",     # Print Hello / chain
    "K2Node_CallFunction_3",
    "K2Node_CallFunction_4",
    "K2Node_CallFunction_5",
    "K2Node_CallFunction_7",
    "K2Node_CallFunction_9",
    "K2Node_MacroInstance_0",    # Is Valid
])
lines = []

def log(m):
    lines.append(str(m))

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def remove_or_disable(graph, n):
    for meth in ("remove_node", "RemoveNode"):
        fn = getattr(graph, meth, None)
        if callable(fn):
            try:
                fn(n)
                return meth
            except Exception as e:
                try:
                    fn(n, True)
                    return meth + "2"
                except Exception as e2:
                    log("  %s fail %s / %s" % (meth, e, e2))
    try:
        n.destroy_node()
        return "destroy"
    except Exception as e:
        log("  destroy fail " + str(e))
    try:
        n.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
        return "disabled"
    except Exception:
        try:
            n.set_editor_property("enabled_state", 2)
            return "disabled2"
        except Exception as e:
            log("  disable fail " + str(e))
            return False

def main():
    log("=== strip5 ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP)
    graph = unreal.load_object(None, EG)
    log("graph_ok=%s" % bool(graph))

    # Collect candidates
    found = {}
    create_widgets = []
    input_actions = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph." not in pn:
            continue
        name = o.get_name()
        found[name] = o
        cn = o.get_class().get_name()
        if "CreateWidget" in cn:
            create_widgets.append(name)
        if cn == "K2Node_InputAction":
            input_actions.append(name)
    log("create_widgets=%s" % create_widgets)
    log("input_actions=%s" % input_actions)

    drop = set(DROP_NAMES)
    for n in create_widgets:
        drop.add(n)
    # Prefer InputAction_0; if only one InputAction exists among {0} drop it
    # Do NOT drop InputAction_3 / _60 (Jump etc.) unless named Interact — property often protected,
    # so only drop _0 which user added for Interact in screenshots.
    log("drop_set=%s" % sorted(drop))

    removed = 0
    for name in sorted(drop):
        n = found.get(name)
        if n is None:
            log("missing " + name)
            continue
        r = remove_or_disable(graph, n)
        log("REM %s => %s" % (name, r))
        if r:
            removed += 1

    # verify
    still_cw = []
    still_ia0 = False
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph." not in pn:
            continue
        name = o.get_name()
        cn = o.get_class().get_name()
        if "CreateWidget" in cn:
            still_cw.append(name)
        if name == "K2Node_InputAction_0":
            still_ia0 = True
        if name in DROP_NAMES:
            # check enabled
            try:
                st = o.get_editor_property("enabled_state")
                log("left %s enabled_state=%s" % (name, st))
            except Exception:
                log("left %s (no state)" % name)

    log("removed=%d still_cw=%s still_ia0=%s" % (removed, still_cw, still_ia0))
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved")
    except Exception as e:
        log("save " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(BP)
        log("saved asset")
    except Exception as e:
        log("save asset " + str(e))
    log("=== strip5 done ===")
    flush()
    # one short engine log
    try:
        unreal.log("T203S5 removed=%d still_cw=%s" % (removed, still_cw))
    except Exception:
        pass

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
    flush()
