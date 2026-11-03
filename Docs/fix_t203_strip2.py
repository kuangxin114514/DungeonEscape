# -*- coding: utf-8 -*-
"""t203 strip2: find EventGraph via ObjectIterator and remove Interact/CreateWidget/Hello chain."""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t203_strip2.txt"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
lines = []

def log(m):
    s = str(m)
    lines.append(s)
    try:
        unreal.log("T203S2: " + s)
    except Exception:
        print(s)

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def node_class(n):
    try:
        return n.get_class().get_name()
    except Exception:
        return "?"

def node_pins(n):
    try:
        return list(n.pins)
    except Exception:
        try:
            return list(n.get_editor_property("pins"))
        except Exception:
            return []

def remove_node(graph, n):
    for meth in ("remove_node", "RemoveNode"):
        fn = getattr(graph, meth, None)
        if callable(fn):
            try:
                fn(n)
                return "remove_node"
            except Exception:
                try:
                    fn(n, True)
                    return "remove_node2"
                except Exception as e:
                    log("  %s fail %s" % (meth, e))
    try:
        n.destroy_node()
        return "destroy"
    except Exception as e:
        log("  destroy fail " + str(e))
    try:
        n.set_editor_property("enabled_state", unreal.NodeEnabledState.DISABLED)
        return "disabled"
    except Exception as e:
        log("  disable fail " + str(e))
        return False

def find_graphs():
    graphs = []
    # ObjectIterator all EdGraph under BP
    for o in unreal.ObjectIterator(unreal.EdGraph):
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight" in pn:
            graphs.append(o)
            log("graph " + pn)
    return graphs

def describe_node(n):
    cn = node_class(n)
    extra = ""
    if cn == "K2Node_InputAction":
        try:
            extra = " action=" + str(n.get_editor_property("input_action_name"))
        except Exception:
            pass
    elif cn == "K2Node_CallFunction":
        try:
            extra = " fn=" + str(n.get_editor_property("function_reference").get_editor_property("member_name"))
        except Exception:
            pass
        for p in node_pins(n):
            try:
                dv = str(p.get_editor_property("default_value") or "")
            except Exception:
                dv = ""
            if dv and len(dv) < 40:
                extra += " [" + pin_name_safe(p) + "=" + dv + "]"
    elif "CreateWidget" in cn:
        extra = " CREATEWIDGET"
    return cn + extra

def pin_name_safe(p):
    try:
        return str(p.get_editor_property("pin_name"))
    except Exception:
        return "?"

def should_drop(n):
    cn = node_class(n)
    if "CreateWidget" in cn:
        return True, "CreateWidget"
    if cn == "K2Node_InputAction":
        try:
            an = str(n.get_editor_property("input_action_name"))
        except Exception:
            an = ""
        if "Interact" in an:
            return True, "InputAction Interact"
    if cn == "K2Node_CallFunction":
        try:
            mn = str(n.get_editor_property("function_reference").get_editor_property("member_name"))
        except Exception:
            mn = ""
        if mn in ("try_hub_interact", "TryHubInteract", "close_hub_shop"):
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
                return True, "Print " + blob.strip()[:40]
        if mn in ("AddToViewport", "SetInputModeUIOnly", "SetInputModeUIOnlyEx", "SetShowMouseCursor"):
            # Only if near CreateWidget — checked by chain later; for now collect as soft
            return "soft", mn
    if cn == "K2Node_MacroInstance":
        try:
            # Is Valid macro often used
            ref = n.get_editor_property("macro_graph_reference")
            # can't easily read; soft
            return "soft", "Macro"
        except Exception:
            pass
    try:
        c = str(n.get_editor_property("node_comment") or "")
        if "DE_HubInteract" in c:
            return True, "comment " + c
    except Exception:
        pass
    return False, ""

def pin_links(p):
    try:
        return list(p.get_editor_property("linked_to"))
    except Exception:
        try:
            return list(p.linked_to)
        except Exception:
            return []

def expand_soft_from_hard(nodes, hard, soft):
    """BFS: soft nodes connected to hard become hard."""
    pin_owner = {}
    for n in nodes:
        for p in node_pins(n):
            pin_owner[id(p)] = n
            try:
                pin_owner[p] = n
            except Exception:
                pass
    reach = set(hard)
    changed = True
    while changed:
        changed = False
        for n in list(reach):
            for p in node_pins(n):
                for lp in pin_links(p):
                    other = pin_owner.get(lp) or pin_owner.get(id(lp))
                    if other is None:
                        for cand in nodes:
                            if lp in node_pins(cand):
                                other = cand
                                break
                    if other is not None and other in soft and other not in reach:
                        reach.add(other)
                        changed = True
    return reach

def compile_bp(bp):
    # UE4.27: use AssetTools / KismetEditorUtilities if available
    for path in (
        ("/Script/UnrealEd.KismetEditorUtilities", "compile_blueprint"),
        ("/Script/BlueprintGraph.BlueprintEditorLibrary", "compile_blueprint"),
    ):
        pass
    try:
        kue = unreal.KismetEditorUtilities
        kue.compile_blueprint(bp)
        log("compile via KismetEditorUtilities")
        return True
    except Exception as e:
        log("KismetEditorUtilities " + str(e))
    try:
        # load CDO
        cls = unreal.load_class(None, "/Script/UnrealEd.KismetEditorUtilities")
        if cls:
            # static
            unreal.KismetEditorUtilities.compile_blueprint(bp)
            return True
    except Exception as e:
        log("compile2 " + str(e))
    # force save at least
    return False

def main():
    log("=== strip2 start ===")
    bp = unreal.EditorAssetLibrary.load_asset(BP)
    log("bp=" + str(bp))
    try:
        pages = list(bp.ubergraph_pages)
        log("ubergraph_pages n=%d" % len(pages))
        for i, g in enumerate(pages):
            try:
                nn = list(g.nodes)
            except Exception:
                try:
                    nn = list(g.get_editor_property("nodes"))
                except Exception:
                    nn = []
            log("  page[%d] %s nodes=%d" % (i, g.get_path_name(), len(nn)))
    except Exception as e:
        log("ubergraph err " + str(e))

    graphs = find_graphs()
    if not graphs:
        # try direct load
        for suffix in (":EventGraph", ".BP_KayKitKnight:EventGraph"):
            g = unreal.load_object(None, BP + suffix if not suffix.startswith(".") else BP.replace("/Game", "/Game") )
            # correct path
            pass
        g = unreal.load_object(None, "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight:EventGraph")
        log("direct EventGraph=" + str(g))
        if g:
            graphs = [g]

    total = 0
    for graph in graphs:
        try:
            nodes = list(graph.nodes)
        except Exception:
            try:
                nodes = list(graph.get_editor_property("nodes"))
            except Exception:
                nodes = []
        log("processing %s nodes=%d" % (graph.get_path_name(), len(nodes)))
        hard = []
        soft = []
        for n in nodes:
            drop, why = should_drop(n)
            desc = describe_node(n)
            if drop is True:
                hard.append(n)
                log("HARD " + desc + " :: " + why)
            elif drop == "soft":
                soft.append(n)
                log("SOFT " + desc + " :: " + why)

        to_drop = expand_soft_from_hard(nodes, hard, soft)
        # always drop hard
        for n in hard:
            to_drop.add(n)
        log("to_drop=%d" % len(to_drop))
        for n in list(to_drop):
            r = remove_node(graph, n)
            log("  REMOVED %s => %s" % (describe_node(n), r))
            if r:
                total += 1

        # verify
        try:
            nodes2 = list(graph.nodes)
        except Exception:
            nodes2 = list(graph.get_editor_property("nodes")) if hasattr(graph, "get_editor_property") else []
        left_bad = 0
        for n in nodes2:
            drop, why = should_drop(n)
            if drop is True:
                left_bad += 1
                log("STILL " + describe_node(n))
        log("left_hard=%d nodes_now=%d" % (left_bad, len(nodes2)))

    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved")
    except Exception as e:
        log("save " + str(e))
    compile_bp(bp)
    try:
        unreal.EditorAssetLibrary.save_asset(BP)
        log("saved asset")
    except Exception as e:
        log("save asset " + str(e))
    log("total_removed=%d" % total)
    log("=== strip2 done ===")
    flush()

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
    flush()
