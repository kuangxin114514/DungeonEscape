# -*- coding: utf-8 -*-
"""t203: neutralize Interact chain by breaking all pin links + rename action."""
from __future__ import print_function
import unreal
import traceback

LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t203_break.txt"
BP = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
DROP = [
    "K2Node_InputAction_0",
    "K2Node_CreateWidget_0",
    "K2Node_CallFunction_2",
    "K2Node_CallFunction_3",
    "K2Node_CallFunction_4",
    "K2Node_CallFunction_5",
    "K2Node_CallFunction_7",
    "K2Node_CallFunction_9",
    "K2Node_MacroInstance_0",
]
lines = []

def log(m):
    lines.append(str(m))

def flush():
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

def pins(n):
    for a in ("pins", "Pins"):
        try:
            return list(n.get_editor_property(a))
        except Exception as e:
            log("  pins(%s) %s" % (a, e))
    # try dir
    for a in dir(n):
        if "pin" in a.lower() and not a.startswith("_"):
            log("  hasattr " + a)
    return []

def break_pin(p):
    # try every known API
    for meth in ("break_all_pin_links", "BreakAllPinLinks", "break_link_to"):
        fn = getattr(p, meth, None)
        if callable(fn):
            try:
                fn()
                return meth
            except TypeError:
                try:
                    # break_link_to needs other pin
                    linked = []
                    for a in ("linked_to", "LinkedTo"):
                        try:
                            linked = list(p.get_editor_property(a))
                        except Exception:
                            pass
                    for lp in linked:
                        try:
                            fn(lp)
                        except Exception:
                            pass
                    return meth + "_loop"
                except Exception as e:
                    log("  %s %s" % (meth, e))
            except Exception as e:
                log("  %s %s" % (meth, e))
    try:
        schema = unreal.EdGraphSchema_K2()
        for meth in ("break_pin_links", "BreakPinLinks", "break_single_pin_link"):
            fn = getattr(schema, meth, None)
            if callable(fn):
                try:
                    fn(p)
                    return "schema." + meth
                except Exception:
                    try:
                        fn(p, True)
                        return "schema." + meth + "2"
                    except Exception as e:
                        log("  schema.%s %s" % (meth, e))
    except Exception as e:
        log("  schema " + str(e))
    # clear linked_to property?
    for a in ("linked_to", "LinkedTo"):
        try:
            p.set_editor_property(a, [])
            return "set_" + a
        except Exception as e:
            log("  set %s %s" % (a, e))
    return False

def main():
    log("=== breaklinks ===")
    graph = unreal.load_object(None, BP + ".BP_KayKitKnight:EventGraph")
    log("graph=%s" % graph)
    # probe graph methods
    gmeths = [a for a in dir(graph) if "node" in a.lower() or "remove" in a.lower() or "pin" in a.lower()]
    log("graph_meths=" + ",".join(gmeths[:60]))

    found = {}
    for o in unreal.ObjectIterator():
        try:
            pn = o.get_path_name()
        except Exception:
            continue
        if "BP_KayKitKnight:EventGraph." not in pn:
            continue
        found[o.get_name()] = o

    # probe one pin API
    sample = found.get("K2Node_CreateWidget_0") or found.get("K2Node_InputAction_0")
    if sample:
        ps = pins(sample)
        log("sample_pins=%d" % len(ps))
        if ps:
            p = ps[0]
            log("pin0 dir=" + ",".join([a for a in dir(p) if not a.startswith("_")][:40]))
            for a in ("linked_to", "LinkedTo", "pin_name", "PinName"):
                try:
                    log("  p.%s=%s" % (a, p.get_editor_property(a)))
                except Exception as e:
                    log("  p.%s ERR %s" % (a, e))

    broken = 0
    for name in DROP:
        n = found.get(name)
        if not n:
            log("missing " + name)
            continue
        # rename Interact action so it never fires
        if name.startswith("K2Node_InputAction"):
            for prop in ("input_action_name", "InputActionName"):
                try:
                    old = n.get_editor_property(prop)
                    n.set_editor_property(prop, "Interact_DISABLED_T203")
                    log("renamed %s %s -> Interact_DISABLED_T203" % (name, old))
                    broken += 1
                    break
                except Exception as e:
                    log("rename %s %s: %s" % (name, prop, e))
        ps = pins(n)
        log("%s pins=%d" % (name, len(ps)))
        for p in ps:
            r = break_pin(p)
            if r:
                broken += 1
                log("  broke %s" % r)

    # Also try graph.remove_node via call_method
    for name in DROP:
        n = found.get(name)
        if not n:
            continue
        for meth in ("remove_node", "RemoveNode"):
            try:
                graph.call_method(meth, (n,))
                log("call_method %s %s OK" % (meth, name))
                broken += 1
                break
            except Exception as e:
                try:
                    graph.call_method(meth, (n, True))
                    log("call_method %s %s OK2" % (meth, name))
                    broken += 1
                    break
                except Exception as e2:
                    log("call_method %s %s: %s / %s" % (meth, name, e, e2))

    bp = unreal.EditorAssetLibrary.load_asset(BP)
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        log("saved")
    except Exception as e:
        log("save " + str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(BP)
    except Exception:
        pass
    log("broken_ops=%d" % broken)
    log("=== done ===")
    flush()
    unreal.log("T203BREAK broken_ops=%d" % broken)

try:
    main()
except Exception:
    log("FATAL\n" + traceback.format_exc())
    flush()
