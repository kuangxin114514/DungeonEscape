# -*- coding: utf-8 -*-
"""t203 strip3: UE4.27-safe BP Interact chain removal."""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t203_strip3.txt"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
EG = "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T203S3: " + s)
    except Exception:
        print(s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def get_nodes(graph):
    for attr in ("nodes", "Nodes"):
        try:
            return list(graph.get_editor_property(attr))
        except Exception:
            pass
    try:
        return list(graph.nodes)
    except Exception:
        pass
    return []

def node_class(n):
    try:
        return n.get_class().get_name()
    except Exception:
        return "?"

def node_pins(n):
    for attr in ("pins", "Pins"):
        try:
            return list(n.get_editor_property(attr))
        except Exception:
            pass
    try:
        return list(n.pins)
    except Exception:
        return []

def remove_node(graph, n):
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
                    log("  %s err %s" % (meth, e))
    try:
        n.destroy_node()
        return "destroy"
    except Exception as e:
        log("  destroy err " + str(e))
    try:
        # NodeEnabledState
        for st in ("DISABLED", "Disabled", 2):
            try:
                if hasattr(unreal, "NodeEnabledState"):
                    n.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
                    return "disabled"
            except Exception:
                pass
        n.set_editor_property("enabled_state", 2)
        return "disabled2"
    except Exception as e:
        log("  disable err " + str(e))
        return False

def iter_bp_objects():
    out = []
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight" in pn and "EventGraph" in pn:
            out.append((pn, o))
    return out

def describe(n):
    cn = node_class(n)
    extra = ""
    try:
        if cn == "K2Node_InputAction":
            extra = " action=" + str(n.get_editor_property("input_action_name"))
        elif cn == "K2Node_CallFunction":
            mr = n.get_editor_property("function_reference")
            extra = " fn=" + str(mr.get_editor_property("member_name"))
            for p in node_pins(n):
                try:
                    dv = str(p.get_editor_property("default_value") or "")
                except Exception:
                    dv = ""
                if dv and len(dv) < 48:
                    extra += " {%s}" % dv
        elif "CreateWidget" in cn:
            extra = " CW"
    except Exception as e:
        extra = " err=" + str(e)
    try:
        extra += " @" + n.get_name()
    except Exception:
        pass
    return cn + extra

def is_hard_drop(n):
    cn = node_class(n)
    if "CreateWidget" in cn:
        return True, "CreateWidget"
    if cn == "K2Node_InputAction":
        try:
            an = str(n.get_editor_property("input_action_name"))
        except Exception:
            an = ""
        if "Interact" in an:
            return True, "Interact"
    if cn == "K2Node_CallFunction":
        try:
            mn = str(n.get_editor_property("function_reference").get_editor_property("member_name"))
        except Exception:
            mn = ""
        if mn in ("try_hub_interact", "TryHubInteract", "close_hub_shop", "CreateWidget"):
            return True, mn
        if mn in ("PrintString", "print_string"):
            blob = ""
            for p in node_pins(n):
                try:
                    blob += " " + str(p.get_editor_property("default_value") or "")
                except Exception:
                    pass
            low = blob.lower()
            if any(x in low for x in ("hello", "ok", "no", "控件")):
                return True, "Print:" + blob.strip()[:40]
    try:
        c = str(n.get_editor_property("node_comment") or "")
        if "DE_HubInteract" in c:
            return True, "comment"
    except Exception:
        pass
    return False, ""

def is_soft(n):
    cn = node_class(n)
    if cn == "K2Node_CallFunction":
        try:
            mn = str(n.get_editor_property("function_reference").get_editor_property("member_name"))
        except Exception:
            mn = ""
        if mn in (
            "AddToViewport", "SetInputModeUIOnly", "SetInputModeUIOnlyEx",
            "SetShowMouseCursor", "GetPlayerController", "IsValid",
        ):
            # GetPlayerController is dangerous — only soft-link from CreateWidget chain
            if mn == "GetPlayerController":
                return "gpc"
            return True
    if "IsValid" in cn or cn == "K2Node_MacroInstance":
        return True
    return False

def pin_links(p):
    for attr in ("linked_to", "LinkedTo"):
        try:
            return list(p.get_editor_property(attr))
        except Exception:
            pass
    try:
        return list(p.linked_to)
    except Exception:
        return []

def expand(nodes, hard, soft_map):
    # soft_map: node -> kind
    pin_owner = {}
    for n in nodes:
        for p in node_pins(n):
            pin_owner[p] = n
    reach = set(hard)
    changed = True
    while changed:
        changed = False
        for n in list(reach):
            for p in node_pins(n):
                for lp in pin_links(p):
                    other = pin_owner.get(lp)
                    if other is None:
                        for cand in nodes:
                            if lp in node_pins(cand):
                                other = cand
                                break
                    if other is None or other in reach:
                        continue
                    sk = soft_map.get(other)
                    if sk:
                        # don't pull lone GetPlayerController unless linked from soft UI chain
                        reach.add(other)
                        changed = True
    return reach

def main():
    log("=== strip3 ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP)
    log("bp=" + str(bp))

    # try get_editor_property ubergraph
    for prop in ("ubergraph_pages", "UbergraphPages", "function_graphs", "FunctionGraphs"):
        try:
            v = bp.get_editor_property(prop)
            log("prop %s type=%s len?=%s" % (prop, type(v), (len(list(v)) if v is not None else None)))
        except Exception as e:
            log("prop %s ERR %s" % (prop, e))

    graph = unreal.load_object(None, EG)
    log("EventGraph load_object=" + str(graph))

    objs = iter_bp_objects()
    log("ObjectIterator EventGraph objs=%d" % len(objs))
    for pn, o in objs[:80]:
        log("  " + pn + " cls=" + o.get_class().get_name())

    if graph is None:
        for pn, o in objs:
            if pn.endswith(":EventGraph") or pn.endswith(".EventGraph"):
                graph = o
                break
                    # find by class name containing EdGraph
        for pn, o in objs:
            cn = o.get_class().get_name()
            if cn == "EdGraph" or "Graph" == cn[-5:]:
                if "EventGraph" in pn:
                    graph = o
                    log("picked graph " + pn)
                    break

    if graph is None:
        # last resort: any object that has nodes property under BP
        for pn, o in objs:
            try:
                ns = get_nodes(o)
            except Exception:
                ns = []
            if ns:
                log("fallback graph with nodes: %s n=%d" % (pn, len(ns)))
                graph = o
                break

    if graph is None:
        log("NO GRAPH — try disable nodes by path")
        # disable known CreateWidget / InputAction by iterating all
        disabled = 0
        for pn, o in objs:
            cn = o.get_class().get_name()
            drop = False
            if "CreateWidget" in cn or "CreateWidget" in pn:
                drop = True
            if cn == "K2Node_InputAction":
                try:
                    if "Interact" in str(o.get_editor_property("input_action_name")):
                        drop = True
                except Exception:
                    pass
            if cn == "K2Node_CallFunction":
                try:
                    mn = str(o.get_editor_property("function_reference").get_editor_property("member_name"))
                except Exception:
                    mn = ""
                if mn == "PrintString":
                    blob = ""
                    for p in node_pins(o):
                        try:
                            blob += str(p.get_editor_property("default_value") or "")
                        except Exception:
                            pass
                    if any(x in blob.lower() for x in ("hello", "ok", "no")):
                        drop = True
                if mn in ("AddToViewport", "SetInputModeUIOnly", "SetInputModeUIOnlyEx", "try_hub_interact"):
                    # only AddToViewport if CreateWidget sibling — disable AddToViewport always risky?
                    # User's only AddToViewport is for shop — disable
                    if mn != "GetPlayerController":
                        drop = True
            if drop:
                try:
                    o.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
                    disabled += 1
                    log("DISABLED " + pn)
                except Exception as e:
                    try:
                        o.set_editor_property("enabled_state", 2)
                        disabled += 1
                        log("DISABLED2 " + pn)
                    except Exception as e2:
                        log("fail disable " + pn + " " + str(e2))
        log("disabled_count=%d" % disabled)
        try:
            unreal.EditorAssetLibrary.save_asset(BP)
        except Exception as e:
            log("save " + str(e))
        flush()
        return

    nodes = get_nodes(graph)
    log("graph=%s nodes=%d" % (graph.get_path_name(), len(nodes)))
    hard = []
    soft_map = {}
    for n in nodes:
        ok, why = is_hard_drop(n)
        if ok:
            hard.append(n)
            log("HARD " + describe(n) + " :: " + why)
        else:
            sk = is_soft(n)
            if sk:
                soft_map[n] = sk
                log("SOFT " + describe(n) + " :: " + str(sk))

    to_drop = expand(nodes, hard, soft_map)
    for n in hard:
        to_drop.add(n)
    # exclude lone GetPlayerController if not reached — expand only adds soft linked
    # but soft_map includes gpc — only added if linked from reach. Good.

    log("to_drop=%d" % len(to_drop))
    removed = 0
    for n in list(to_drop):
        # skip GetPlayerController if somehow alone — already filtered
        r = remove_node(graph, n)
        log("REM %s => %s" % (describe(n), r))
        if r:
            removed += 1

    nodes2 = get_nodes(graph)
    still = 0
    for n in nodes2:
        ok, why = is_hard_drop(n)
        if ok:
            still += 1
            log("STILL " + describe(n))
    log("removed=%d still_hard=%d nodes_now=%d" % (removed, still, len(nodes2)))

    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved loaded")
    except Exception as e:
        log("save loaded " + str(e))
    try:
        unreal.KismetEditorUtilities.compile_blueprint(bp)
        log("compiled")
    except Exception as e:
        log("compile " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(BP)
        log("saved asset")
    except Exception as e:
        log("save asset " + str(e))
    log("=== strip3 done ===")
    flush()

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
    flush()
