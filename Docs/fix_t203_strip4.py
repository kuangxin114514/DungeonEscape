# -*- coding: utf-8 -*-
"""t203 strip4: remove Interact/CreateWidget/Hello via ObjectIterator + remove_node."""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t203_strip4.txt"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
EG = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T203S4: " + s)
    except Exception:
        print(s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def node_pins(n):
    for attr in ("pins", "Pins"):
        try:
            return list(n.get_editor_property(attr))
        except Exception:
            pass
    return []

def fn_name(n):
    try:
        return str(n.get_editor_property("function_reference").get_editor_property("member_name"))
    except Exception:
        return ""

def pin_defaults(n):
    blob = ""
    for p in node_pins(n):
        try:
            blob += " " + str(p.get_editor_property("default_value") or "")
        except Exception:
            pass
    return blob

def remove_or_disable(graph, n):
    for meth in ("remove_node", "RemoveNode"):
        fn = getattr(graph, meth, None)
        if callable(fn):
            try:
                fn(n)
                return meth
            except Exception:
                try:
                    fn(n, True)
                    return meth + "2"
                except Exception as e:
                    log("  %s: %s" % (meth, e))
    try:
        n.destroy_node()
        return "destroy"
    except Exception as e:
        log("  destroy: " + str(e))
    try:
        n.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
        return "disabled"
    except Exception:
        try:
            n.set_editor_property("enabled_state", 2)
            return "disabled2"
        except Exception as e:
            log("  disable: " + str(e))
            return False

def classify(n, pn):
    cn = n.get_class().get_name()
    if "CreateWidget" in cn or "CreateWidget" in pn:
        return "hard", "CreateWidget"
    if cn == "K2Node_InputAction":
        try:
            an = str(n.get_editor_property("input_action_name"))
        except Exception:
            an = ""
        if "Interact" in an:
            return "hard", "Interact:" + an
        return "keep", an
    if cn == "K2Node_CallFunction":
        mn = fn_name(n)
        if mn in ("try_hub_interact", "TryHubInteract", "close_hub_shop"):
            return "hard", mn
        if mn in ("PrintString", "print_string"):
            blob = pin_defaults(n).lower()
            if any(x in blob for x in ("hello", "ok", "no", "控件")):
                return "hard", "Print:" + blob.strip()[:40]
            return "keep", mn
        if mn in ("AddToViewport", "SetInputModeUIOnly", "SetInputModeUIOnlyEx", "SetShowMouseCursor"):
            return "soft", mn
        if mn == "GetPlayerController":
            return "soft_gpc", mn
        return "keep", mn
    if cn == "K2Node_MacroInstance":
        return "soft", "Macro"
    try:
        c = str(n.get_editor_property("node_comment") or "")
        if "DE_HubInteract" in c:
            return "hard", "comment"
    except Exception:
        pass
    return "keep", cn

def pin_links(p):
    for attr in ("linked_to", "LinkedTo"):
        try:
            return list(p.get_editor_property(attr))
        except Exception:
            pass
    return []

def main():
    log("=== strip4 ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP)
    graph = unreal.load_object(None, EG)
    log("graph=" + str(graph))

    nodes = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph." not in pn:
            continue
        # skip the graph itself
        if pn.endswith(":EventGraph"):
            continue
        nodes.append((pn, o))
    log("nodes_found=%d" % len(nodes))

    hard = []
    soft = []
    soft_gpc = []
    for pn, n in nodes:
        kind, why = classify(n, pn)
        log("%s %s :: %s" % (kind, pn.split(".")[-1], why))
        if kind == "hard":
            hard.append(n)
        elif kind == "soft":
            soft.append(n)
        elif kind == "soft_gpc":
            soft_gpc.append(n)

    # BFS: soft(/gpc) linked to hard
    pin_owner = {}
    for pn, n in nodes:
        for p in node_pins(n):
            pin_owner[p] = n
    soft_set = set(soft + soft_gpc)
    reach = set(hard)
    changed = True
    while changed:
        changed = False
        for n in list(reach):
            for p in node_pins(n):
                for lp in pin_links(p):
                    other = pin_owner.get(lp)
                    if other is None:
                        for _, cand in nodes:
                            if lp in node_pins(cand):
                                other = cand
                                break
                    if other is not None and other in soft_set and other not in reach:
                        reach.add(other)
                        changed = True
                        log("link-pull " + other.get_name())

    # If pin walking failed (protected pins), force-drop soft UI helpers when CreateWidget/Interact present
    if hard and len(reach) <= len(hard):
        for n in soft:
            reach.add(n)
            log("force-soft " + n.get_name())
        # only GPC that sit near shop chain names (CallFunction_3..9 area) — skip if cannot tell; safer skip GPC
        log("force-soft applied because pin-walk pulled nothing extra")

    to_drop = list(reach)
    log("to_drop=%d (hard=%d)" % (len(to_drop), len(hard)))

    removed = 0
    for n in to_drop:
        r = remove_or_disable(graph, n)
        log("REM %s => %s" % (n.get_name(), r))
        if r:
            removed += 1

    # verify by re-iterating
    still = 0
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph." not in pn:
            continue
        kind, why = classify(o, pn)
        if kind == "hard":
            still += 1
            log("STILL " + pn.split(".")[-1] + " " + why)
    log("removed=%d still_hard=%d" % (removed, still))

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

    # try compile via console
    try:
        unreal.SystemLibrary.execute_console_command(None, "Kismet.CompileBlueprint " + BP)
    except Exception:
        pass
    log("=== strip4 done ===")
    flush()

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
    flush()
